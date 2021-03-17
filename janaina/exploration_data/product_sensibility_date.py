import pandas as pd
import numpy as np

import warnings
warnings.filterwarnings('ignore')
import holidays

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
    '''
    elif holliday == "Carnaval":
        CARNAVAL_DATE = str(day)
    elif holliday == "Sexta-feira Santa":
        SEMANA_DATE = str(day)
    elif holliday == "Natal":
        NATAL_DATE = str(day)
    '''

path_miner = '../../../data/miner/'
path_pred  = '../../../data/pred/'
path_res   = '../../../data/res/'

def is_var_holliday(id_ass, id_loja, id_prod):

    data = pd.read_csv(path_miner + id_ass +'_'+ id_loja+'.csv')
    data.index = data['data']

    data_prod         = data[data['produtoId'] == id_prod]
    data_prod['data'] = data_prod['data'].astype('datetime64[ns]')

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

def sense_product(data, data_holliday):

    data = pd.concat([data, data_holliday]).drop_duplicates(keep=False)
    sensibility = 1.25 #25%

    baseline_data          = data['quantidade'].mean()          # + data['quantidade'].std()
    baseline_data_holliday = data_holliday['quantidade'].mean() # + data_holliday['quantidade'].std()

    if (sensibility*(baseline_data) < baseline_data_holliday):
        return 1

    return 0


# CERV SKOL GF 300ML SO LIQ id = 144438
is_var_holliday('13014206000112', '000002', 144438)
