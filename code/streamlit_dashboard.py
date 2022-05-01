import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import pycaret.classification as pc

fname = '../data/operalization/final_teste.pkl'


dataset_train = pd.read_parquet('../Data/operalization/base_train.parquet')
dataset_test = pd.read_parquet('../Data/operalization/base_test.parquet')
results = pd.read_parquet('../data/processed/data_filtered.parquet')
result_pred_final = pd.read_parquet('../data/operalization/pred_final.parquet')

############################################ SIDE BAR TITLE
st.sidebar.title('Painel de Controle')
st.sidebar.markdown(f"""
Controle do preditor de arremessos e entrada de variáveis para avaliação de novas jogadas.
""")

st.sidebar.header('Tipo de Arremesso Analisado')

# results = load_data(fname)
model = pd.read_pickle('../data/operalization/final_teste.pkl')
train_data = results
features = results.drop(['shot_type', 'shot_made_flag'], axis=1).columns
target_col = results['shot_made_flag']
idx_train = dataset_train.index#train_data.categoria == 'treino'
idx_test = dataset_test.index


############################################ TITULO
st.title(f"""
Sistema Online de Avaliação de novos arremessos
""")

features_text = ''
for x in features:
    features_text = features_text + '\n - ' + str(x)

st.markdown(f"""
Esta interface pode ser utilizada para a explanação dos resultados
do modelo de classificação de arremessos,
segundo as variáveis utilizadas.

O modelo selecionado foi treinado com uma base total de {len(idx_train)} e avaliado
com {len(idx_test)} novos dados (histórico completo de {results.shape[0]} arremessos.)

Os arremessos são caracterizados pelas seguintes variáveis: 
{features_text}.
""")


############################################ ENTRADA DE VARIAVEIS
st.sidebar.header('Entrada de Variáveis')
form = st.sidebar.form("input_form")
input_variables = {'target_col': 0}
for cname in features:
    input_variables[cname] = form.slider(cname.capitalize(),
                                   results[cname].min(),
                                   results[cname].max())
form.form_submit_button("Avaliar")

############################################ PREVISAO DO MODELO 
@st.cache
def predict_user(input_variables):
    model_load = pc.load_model('../data/operalization/final_teste')
    new_prediction = pc.predict_model(model_load, data=pd.DataFrame(input_variables, index=[0]))
    return {
        'probabilidade': new_prediction.loc[0, 'Score'],
        'classificacao': new_prediction.loc[0, 'Label']
    }

user = predict_user(input_variables)

if user['classificacao'] == 0:
    st.sidebar.markdown("""Classificação:
    <span style="color:red">*Errou*</span>.
    """, unsafe_allow_html=True)
else:
    st.sidebar.markdown("""Classificação:
    <span style="color:green">*Acertou*</span>.
    """, unsafe_allow_html=True)

############################################ PAINEL COM AS PREVISOES HISTORICAS

fignum = plt.figure(figsize=(6,4))
target_col = 'shot_made_flag'
for i in results.shot_made_flag.unique():
    sns.distplot(result_pred_final[result_pred_final[target_col] == str(i)].Score,
                 label=result_pred_final[result_pred_final[target_col] == i][target_col],
                 ax = plt.gca())
# User wine
plt.plot(user['probabilidade'], 2, '*k', markersize=3, label='Arremessos')

plt.title('Preditor de Arremessos')
plt.ylabel('Densidade Estimada')
plt.xlabel('Probabilidade Acertar Cesta')
plt.xlim((0, 1))
plt.grid(True)
plt.legend(loc='best')
st.pyplot(fignum)
