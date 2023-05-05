from .normalization_preprocess import normalize_column, merge_dataframes
from .models import MaterialsPriceModel

import pandas as pd

# get_data_for_visualization.py : 시각화를 위한 데이터 

def _get_normalization_data(start_date, end_date):
    """start_date ~ end_date 사이의 금 / 은 가격 값을 받아 정규화 컬럼 추가 로직 수행"""
    gold_data = MaterialsPriceModel.objects.filter(date__range=(start_date, end_date), material_name__exact=1).values('id', 'price')
    
    if not gold_data:
        raise ValueError(f"No gold price data available for the given date range: {start_date} ~ {end_date}")
    
    gold_price_df = pd.DataFrame(gold_data.values())
    gold_price_df['date'] = pd.to_datetime(gold_price_df['date'])

    silver_data = MaterialsPriceModel.objects.filter(date__range=(start_date, end_date), material_name__exact=2).values('id', 'price')
    
    if not silver_data:
        raise ValueError(f"No silver price data available for the given date range: {start_date} ~ {end_date}")
    
    silver_price_df = pd.DataFrame(silver_data.values())
    silver_price_df['date'] = pd.to_datetime(silver_price_df['date'])

    # 두 데이터프레임을 date 기준으로 merge 후 컬럼 이름 지정
    total_df = merge_dataframes([gold_price_df, silver_price_df], 'outer', 'date')
    total_df.rename(columns={"price_x": "gold_price",
                               "price_y": "silver_price"}, inplace=True)

    # 날짜 기준 sort 및 인덱스 설정 후 필요없는 columns 정보 drop
    total_df.sort_values(by='date', inplace=True)
    total_df.set_index('date', inplace=True)
    total_df.drop('id_x', axis=1, inplace=True)
    total_df.drop('id_y', axis=1, inplace=True)
    total_df.drop('material_name_id_x', axis=1, inplace=True)
    total_df.drop('material_name_id_y', axis=1, inplace=True)

    # 각 가격 정보를 정규화하여 새로운 컬럼으로 생성
    total_df["normalize_gold"] = normalize_column(total_df, "gold_price")
    total_df["normalize_sliver"] = normalize_column(total_df, "silver_price")
    
    return total_df

def _get_time_series_data(start_date, end_date):
    """모델로부터 start_date ~ end_date의 금 / 은 가격 정보를 DataFrame으로 가져오는 함수"""
    # 시작일과 끝 날짜 사이 일자와 가격 데이터를 가져옴 
    gold_data = MaterialsPriceModel.objects.filter(date__range=(start_date, end_date), material_name__exact=1).values('id', 'price')
    
    # 유효한 데이터가 없으면 ValueError를 발생시켜 템플릿에 전달
    if not gold_data:
        raise ValueError(f"No gold price data available for the given date range: {start_date} ~ {end_date}")
    
    # 인덱스를 날짜로 설정
    gold_price_df = pd.DataFrame(gold_data.values())
    gold_price_df['date'] = pd.to_datetime(gold_price_df['date'])
    gold_price_df.set_index('date', inplace=True)
    
    silver_data = MaterialsPriceModel.objects.filter(date__range=(start_date, end_date), material_name__exact=2).values('id', 'price')
    
    if not silver_data:
        raise ValueError(f"No silver price data available for the given date range: {start_date} ~ {end_date}")
    
    silver_price_df = pd.DataFrame(silver_data.values())
    silver_price_df['date'] = pd.to_datetime(silver_price_df['date'])
    silver_price_df.set_index('date', inplace=True)
    
    return gold_price_df, silver_price_df