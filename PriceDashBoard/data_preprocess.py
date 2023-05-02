import os
import sys
from django.core.files import File

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)) + '/app')))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

from PriceDashBoard.models import MaterialsPriceModel, MaterialsModel
import pandas as pd
import numpy as np

def data_processing_feature(df):
        df['20MA'] = df['price'].rolling(window = 20).mean()
        df['60MA'] = df['price'].rolling(window = 60).mean()
        df['120MA'] = df['price'].rolling(window= 120).mean()
        df['200MA'] = df['price'].rolling(window= 200).mean()
    
        df.dropna(inplace=True)
    
        upper_20 = np.where(df['price'] > df['20MA'], 1, 0) # 1 = 매수, 0 = 매도 signal
        upper_60 = np.where(df['price'] > df['60MA'], 1, 0) # 1 = 매수, 0 = 매도 signal
        regular_array = np.where((df['20MA'] > df['60MA']) & (df['60MA'] > df['120MA']) & (df['120MA'] > df['200MA']), 1, 0)
    
        df['upper_20'] = upper_20
        df['upper_60'] = upper_60
        df['regular_array'] = regular_array
    
        df.drop(['20MA','60MA','120MA','200MA'], axis=1, inplace=True)
    
        return df

def data_preprocess(material_id):
    """
    데이터 전처리 함수

    parameter = material_id (model에 들어간 원자재 id)
    return = 원자재 id, 가격, 분석지표(매수=1, 매도=0)들을 담은 JSON file
    """
    # queryset
    qs = MaterialsPriceModel.objects.filter(material_name_id=material_id)
    data = pd.DataFrame.from_records(qs.values())
    data.drop('id', axis=1, inplace=True)
    data.set_index('date', inplace=True)
    data = data_processing_feature(data)

    result_json = data.iloc[-1].to_json(orient='columns')

    print(data.iloc[-1].to_json(orient='columns'))
    return result_json

data_preprocess(1)

# 최종 목적
# JSON 뱉어내는 것
# {'date' : 2023-04-28, '분석1':1, '분석2':1, '분석3':0}