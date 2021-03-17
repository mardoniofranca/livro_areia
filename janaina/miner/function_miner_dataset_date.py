import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from datetime import date
import warnings
warnings.filterwarnings('ignore')
import holidays

import pandas.io.common

path_miner = '../../../data/miner/'
path_pred  = '../../../data/pred/'
path_res   = '../../../data/res/'

hollidays_br_2019 = holidays.Brazil(years=2019)
hollidays_br_2020 = holidays.Brazil(years=2020)

for day, holliday in hollidays_br_2019.items():
    if holliday == "Carnaval":
        CARNAVAL_DATE = str(day)
    elif holliday == "Sexta-feira Santa":
        SEMANA_DATE = str(day)
    elif holliday == "Natal":
        NATAL_DATE = str(day)

for day, holliday in hollidays_br_2020.items():
    if holliday == "Ano novo":
        ANO_NOVO_DATE = str(day)



def isWeekend(n):
    if n <5:
        return 0
    else:
        return 1

def isStartMes(n):
    if ( n > 30):
        return 1
    elif (n < 10):
        return 1
    else:
        return 0

def isHoliday(date):
    br_holidays = holidays.BR()
    if ((date in br_holidays)):
        return 1
    else:
        return 0

def ref(v1,v2, c):
    if (v1 > v2):
        div = (v1 - v2)/v1
        if (div > c):
            return v1
        else:
            return v2
    else:
        div = (v2 - v1)/v2
        if (div>c):
            return v1
        else:
            return v2

def is_var_holliday(id_ass, id_loja, id_prod=int):
    id_prod = int(id_prod)
    data = pd.read_csv(path_miner + id_ass +'_'+ id_loja+'.csv')

    if id_prod in data['produtoId'].values:
        data.index = data['data']

        data_prod         = data[data['produtoId'] == id_prod]
        data_prod[["data"]]   = data_prod[["data"]].apply(pd.to_datetime)

        CARNAVAL      = data_prod.loc['2019-02-26':CARNAVAL_DATE]
        SEMANA_SANTA  = data_prod.loc['2019-04-12':SEMANA_DATE]
        NATAL         = data_prod.loc['2019-12-22':NATAL_DATE]
        ANO_NOVO      = data_prod.loc['2019-12-29':ANO_NOVO_DATE]

        dict_hollidays = {'sense_Carnaval'    : CARNAVAL,
                          'sense_SemanaSanta': SEMANA_SANTA,
                          'sense_Natal'       : NATAL,
                          'sense_AnoNovo'    : ANO_NOVO}

        data_resp = pd.DataFrame(data_prod)

        for name_holliday, data_holliday in dict_hollidays.items():
            data_resp[name_holliday] = sense_product(data_prod, data_holliday)

        return data_resp
    else:
        print('Produto não existente')
        data_resp = pd.DataFrame()
        return data_resp

def sense_product(data, data_holliday):

    data = pd.concat([data, data_holliday]).drop_duplicates(keep=False)
    sensibility = 1.25 #25%

    baseline_data          = data['quantidade'].mean()          # + data['quantidade'].std()
    baseline_data_holliday = data_holliday['quantidade'].mean() # + data_holliday['quantidade'].std()

    if (sensibility*(baseline_data) < baseline_data_holliday):
        return 1

    return 0

def miner_dataset_date_sense(id_ass , id_loja, id_prod, var_preco = 0.05):
    id_prod = int(id_prod)

    data_prod = is_var_holliday(id_ass , id_loja , id_prod)
    if(data_prod.empty == False):
        data_prod[['valor']]                = data_prod[['valor']].apply(pd.to_numeric)
        data_prod[['quantidade']]           = data_prod[['quantidade']].apply(pd.to_numeric)

        #data_prod = data_prod.sort_values(by=['data'],ascending=True)

        data_prod['valor_unit']  =  round(data_prod['valor']/data_prod['quantidade'],2)
        data_prod['ano']         =  pd.DatetimeIndex(data_prod['data']).year
        data_prod['mes']         =  pd.DatetimeIndex(data_prod['data']).month
        data_prod['dia_semana']  =  pd.DatetimeIndex(data_prod['data']).dayofweek
        data_prod['dia']         =  pd.DatetimeIndex(data_prod['data']).day
        data_prod['fim_semana']  =  data_prod['dia_semana'].apply(lambda x: isWeekend((x)))
        data_prod['inicio_mes']  =  data_prod['dia'].apply(lambda x: isStartMes((x)))
        data_prod['feriado']     =  data_prod['data'].apply(lambda x: isHoliday((x)))

        columns = ['data', 'produtoId', 'descr', 'valor', 'valorCancelado', 'quantidadeCancelada',
                    'quantidadeDocumentos', 'quantidadeValorZero']
        data_prod.drop(columns, inplace=True, axis=1)

        preco_ref = data_prod.mode(axis=0)['valor_unit'][0]

        data_prod['valor_unit']  = data_prod['valor_unit'].apply(lambda x: ref(x, preco_ref, var_preco) )

        data_prod.index = range(0, len(data_prod))

        return data_prod


def miner_dataset_date(id_ass , id_loja, id_prod, var_preco = 0.05):
    id_prod = int(id_prod)

    dataset = pd.read_csv(path_miner + id_ass +'_'+ id_loja+'.csv')

    if id_prod in dataset['produtoId'].values:
        dataset[["data"]]       = dataset[["data"]].apply(pd.to_datetime)
        dataset[["valor"]]      = dataset[["valor"]].apply(pd.to_numeric)
        dataset[["quantidade"]] = dataset[["quantidade"]].apply(pd.to_numeric)
        dataset[['produtoId']]  = dataset[["produtoId"]].apply(pd.to_numeric)

        data_prod = dataset[dataset['produtoId'] == id_prod]

        data_prod['valor_unit']  =  round(data_prod['valor']/data_prod['quantidade'],2)
        data_prod['ano']         =  pd.DatetimeIndex(data_prod['data']).year
        data_prod['mes']         =  pd.DatetimeIndex(data_prod['data']).month
        data_prod['dia_semana']  =  pd.DatetimeIndex(data_prod['data']).dayofweek
        data_prod['dia']         =  pd.DatetimeIndex(data_prod['data']).day
        data_prod['fim_semana']  =  data_prod['dia_semana'].apply(lambda x: isWeekend((x)))
        data_prod['inicio_mes']  =  data_prod['dia'].apply(lambda x: isStartMes((x)))
        data_prod['feriado']     =  data_prod['data'].apply(lambda x: isHoliday((x)))

        columns = ['data', 'produtoId', 'descr', 'valor', 'valorCancelado', 'quantidadeCancelada',
                    'quantidadeDocumentos', 'quantidadeValorZero']
        data_prod.drop(columns, inplace=True, axis=1)

        preco_ref = data_prod.mode(axis=0)['valor_unit'][0]

        data_prod['valor_unit']  = data_prod['valor_unit'].apply(lambda x: ref(x, preco_ref, var_preco) )

        data_prod.index = range(0, len(data_prod))

        return data_prod
    else:
        print('Produto não existente')



