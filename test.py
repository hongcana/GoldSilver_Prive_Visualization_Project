from django.test import TestCase
from GetAPI import get_price_data
from Get_Latest_Date_From_DB import bulk_data_after_latest_date
from LoadPriceData_To_DB import bulk_price_data
from datetime import datetime, timedelta, date
from PriceDashBoard.models import MaterialsModel, MaterialsPriceModel
import pandas as pd
import unittest

class GetAPITest(unittest.TestCase):
    def test_get_price_data(self):
        # 데이터를 dictionary 형태로 정의합니다.
        data = {'Date': ['2013-01-02'], 'USD': [1693.75]}

        # 데이터프레임을 생성합니다.
        df = pd.DataFrame(data)

        # 인덱스를 'Date' 열로 지정합니다.
        df.set_index('Date', inplace=True)
        df.index = pd.to_datetime(df.index)
        # 컬럼 이름을 'USD'로 변경합니다.
        df.columns = ['USD']

        output = get_price_data("gold")
        print(output.index)
        print(df.index)

        print(output.columns)
        print(df.columns)

        #처음 시작이되는 날짜 인덱스의 레코드와 비교
        self.assertTrue(output.head(1).equals(df))

class LoadPriceDataToDBTest(unittest.TestCase):


    def test_True_bulk_price_data(self):
        # 적재된 모델과, 나스닥에서 받아온 데이터 프레임이 일치하는지 확인.
        yesterday = datetime.now() - timedelta(days=1)
        yesterday = yesterday.date().strftime("%Y-%m-%d")

        gold_price_data = get_price_data('gold')
        silver_price_data = get_price_data('silver')
        gold_price_data = gold_price_data.loc[:yesterday]
        silver_price_data =silver_price_data.loc[:yesterday]
        print(gold_price_data)

        # 판다스 데이터 프레임을 장고 모델로 변환
        gold_data_list = []
        gold_material = MaterialsModel.objects.get(pk=1)
        for index, row in gold_price_data.iterrows():
            price_data = MaterialsPriceModel(material_name=gold_material,
                                            date=index,
                                            price=row['USD'])
            
            gold_data_list.append(price_data)

        silver_data_list = []
        silver_material = MaterialsModel.objects.get(pk=2)
        for index, row in gold_price_data.iterrows():
            price_data = MaterialsPriceModel(material_name=silver_material,
                                            date=index,
                                            price=row['USD'])
            
            silver_data_list.append(price_data)
        # 어제까지 적재된 Model을 불러옴
        queryset = MaterialsPriceModel.objects.filter(date__lte=yesterday)
        gold_set = queryset.filter(material_name=gold_material)
        silver_set = queryset.filter(material_name=silver_material)
        
        # 각 값을 list 형식으로 Date, value 추출
        # GOLD
        gold_queryset_dates = list(gold_set.values_list('date', flat=True))
        gold_queryset_prices = list(gold_set.values_list('price', flat=True))

        gold_data_list_dates = list(price_data.date.date() for price_data in gold_data_list)
        gold_data_list_prices = list(price_data.price for price_data in gold_data_list)

        self.assertEqual(gold_queryset_dates, gold_data_list_dates)
        self.assertEqual(gold_queryset_prices, gold_data_list_prices)

        # SILVER
        silver_queryset_dates = list(silver_set.values_list('date', flat=True))
        silver_queryset_prices = list(silver_set.values_list('price', flat=True))

        silver_data_list_dates = list(price_data.date.date() for price_data in silver_data_list)
        silver_data_list_prices = list(price_data.price for price_data in silver_data_list)

        self.assertEqual(silver_queryset_dates, silver_data_list_dates)
        self.assertEqual(silver_queryset_prices, silver_data_list_prices)




class GetLatestDateFromDBTest(unittest.TestCase):
    def test_is_gold_silver_same_date(self):
        after_n = 3
        gold_latest = MaterialsPriceModel.objects.filter(material_name_id=1).latest('date')
        silver_latest = MaterialsPriceModel.objects.filter(material_name_id=2).latest('date')
        print(gold_latest)
        print(silver_latest)
        
        # 금, 은 날짜가 같은 날 고시되었는지 확인.
        self.assertEqual(gold_latest.date, silver_latest.date)




