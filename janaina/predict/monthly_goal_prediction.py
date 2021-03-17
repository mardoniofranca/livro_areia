import pandas as pd
import numpy as np
import seaborn as sns
import warnings
warnings.filterwarnings("ignore")


# Dataset paths
path_miner = '../../../data/miner/'
path_pred  = '../../../data/pred/'
path_res   = '../../../data/res/'
typ = '.csv'

# Subscriber data
id_ass  = '09517617000153'
id_loja = '3'
data = id_ass + '_' + id_loja + typ

# Third-party dataset data
oss_com_bol = 'osc_month_comercio_bolsa' + typ
vol_com_bol = 'vol_month_comercio_bolsa' + typ
mean_dol    = 'media_mensal_dolar_12-18a03-20' + typ
gas_for     = 'gasolina_fortaleza' + typ

#final dataset name
name_df_f = 'test1' + typ

# Third party data preparation function
def pre_of_third_party(data):
    data['Date']       = data['Date'].apply(pd.to_datetime)
    data.index         = data['Date'].dt.to_period('M')
    data.drop(['Date'], axis=1, inplace=True)
    data.index.name    = 'data'
    return (data)


# Importing subscriber CSV
df_ass   = pd.read_csv(path_miner + data, encoding="utf-8")

# Importing third-party dataset
df_osc = pd.read_csv(path_miner + oss_com_bol, encoding="utf-8")
df_vol = pd.read_csv(path_miner + vol_com_bol, encoding="utf-8")
df_dol = pd.read_csv(path_miner + mean_dol,    encoding="utf-8")
df_gas = pd.read_csv(path_miner + gas_for,     encoding="utf-8")

# Preparation of the subscriber's dataset
df_ass[['data']]       = df_ass[['data']].apply(pd.to_datetime)
df_ass[['produtoId']]  = df_ass[['produtoId']].apply(pd.to_numeric)
df_ass[['valor']]      = df_ass[['valor']].apply(pd.to_numeric)
df_ass[['quantidade']] = df_ass[['quantidade']].apply(pd.to_numeric)
df_ass[['valorCancelado']] = df_ass[['valorCancelado']].apply(pd.to_numeric)

df_ass['valorReal']  = df_ass['valor'] - df_ass['valorCancelado']

df_ass = df_ass.drop(['valorCancelado', 'quantidadeCancelada', 'quantidadeDocumentos', 'quantidadeValorZero'], axis=1)

# Preparation of third party dataset
df_osc = pre_of_third_party(df_osc)
df_vol = pre_of_third_party(df_vol)
df_dol = pre_of_third_party(df_dol)

df_gas['MÊS']        = df_gas['MÊS'].apply(pd.to_datetime)
df_gas.index         = df_gas['MÊS'].dt.to_period('M')
df_gas.drop(['Unnamed: 0','MÊS'], axis=1, inplace=True)
df_gas.index.name = 'data'

columns_osc = ['BTOW3_OSC', 'VVAR3_OSC', 'CGRA3_OSC', 'CGRA4_OSC', 'GUAR3_OSC',
               'WLMM3_OSC', 'WLMM4_OSC', 'HYPE3_OSC', 'LLIS3_OSC', 'ARZZ3_OSC', 'LREN3_OSC', 'AMAR3_OSC', 'LAME3_OSC',
               'MGLU3_OSC', 'LAME4_OSC']
columns_vol =  ['BTOW3_VOL', 'VVAR3_VOL', 'CGRA3_VOL', 'CGRA4_VOL', 'GUAR3_VOL', 'WLMM3_VOL',
                'WLMM4_VOL', 'HYPE3_VOL', 'LLIS3_VOL', 'ARZZ3_VOL', 'LREN3_VOL', 'AMAR3_VOL', 'LAME3_VOL', 'MGLU3_VOL',
                'LAME4_VOL']
columns_gas = ['PREÇO_MÉDIO_REVENDA', 'DESVIO_PADRÃO_REVENDA', 'PREÇO_MÍNIMO_REVENDA', 
               'PREÇO_MÁXIMO_REVENDA', 'PREÇO_MÉDIO_DISTRIBUIÇÃO', 'DESVIO_PADRÃO_DISTRIBUIÇÃO', 'PREÇO_MÍNIMO_DISTRIBUIÇÃO', 
               'PREÇO_MÁXIMO_DISTRIBUIÇÃO']
columns_dol = ['Dólar']

df_osc.columns = columns_osc
df_vol.columns = columns_vol
df_dol.columns = columns_dol
df_gas.columns = columns_gas

# Creation of the monthly accumulation dataset
df_by_month          = round(df_ass['valorReal'].groupby(df_ass['data'].dt.to_period('M')).sum(), 4)
df_by_month          = df_by_month.to_frame()
df_by_month['mes']   = df_by_month.index.month

# Subscriber concatenation with features for analysis
df_ass_feat = pd.concat( [df_by_month, df_osc, df_vol, df_gas, df_dol], sort=False, axis=1)

# Eliminating rows with NA data
df_ass_feat.dropna(axis=0, inplace=True)

# Correlation analysis
df_corr = df_ass_feat.drop(['mes'], axis=1).corr()[:1].transpose() 

# Relevant feature analysis
features = list(df_corr[(abs(df_corr['valorReal']) >= 0.5) & (abs(df_corr['valorReal']) < 1)].index)

# Concatenating the subscriber's dataset with the relevant features
df_final = pd.concat([df_by_month, df_ass_feat[features]], sort=False, axis=1) 

# Eliminating rows with NA data
df_final.dropna(axis=0, inplace=True)

# Exporting final dataset
df_final.to_csv(path_pred + name_df_f)