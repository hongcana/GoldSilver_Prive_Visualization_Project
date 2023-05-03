import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

import nasdaqdatalink as ndl

# DB -> 최신 날짜가 존재하면 굳이.. 안가져와도되는 분기 (1)


# 1. query로 latest_date를 확인한다 
# 2. Datetime 모듈 이용하여 오늘 날짜에 해당하는 데이터가 있는지 확인
# 3. API에서 추가가 되었다면 insert
# 4. 없다면 pass

# 제일 시간 순서대로 저장되어있다고 가정 (최신데이터의 날짜) == 오늘 날짜
# 아래가 (2)
# MYSQL DB -> 적재 (3)

def get_price_data(item_name, start_date='2013-01-01'):
    """원자재 이름으로 가격 정보를 가져오는 함수"""
    item_name = item_name.upper()
    
    # 전체 가격 데이터를 가져옴
    # 2013-01-01부터 최신까지
    price_data = ndl.get(f'LBMA/{item_name}', start_date=start_date, api_key='EDGmffrbRvVhGiNJhxwi')
    
    # 원자재 종류에 따라 추출할 데이터 columns
    if item_name == 'GOLD':
        price_data_from_2013 = price_data[['USD (PM)']]
        price_data_from_2013.fillna(method='ffill', inplace=True)
        price_data_from_2013.rename(columns={'USD (PM)' : 'USD'}, inplace=True)
        
    else:
        price_data_from_2013 = price_data[['USD']]
        price_data_from_2013.fillna(method='ffill', inplace=True)

    return price_data_from_2013

