import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from datetime import datetime
from datetime import timedelta
from PriceDashBoard.models import *
from GetAPI import get_price_data
from LoadPriceData_To_DB import bulk_price_data

def bulk_data_after_latest_date(after_n=3):
    """
    DB에 기록된 최신 날짜를 가져온 후 
    오늘 날짜 기준 after_n일이 지났다면 bulk 수행
    """
    
    # 데이터가 기록된 최신 날짜
    latest = MaterialsPriceModel.objects.last()
    latest_date = latest.date
    
    # DB 내 최신 날짜 기준 after_n일 후
    after_n_days = str(latest_date + timedelta(days=after_n))
    
    # 오늘 날짜
    today = datetime.now()
    today = today.strftime("%Y-%m-%d")
    
    # after_n일 이상 지남
    if today >= after_n_days:
        # 최신 날짜 이후 금/은 데이터를 API로 가져옴
        next_day = latest_date + timedelta(days=1)
        
        print(next_day)
        
        new_gold_price_data = get_price_data('gold', start_date=next_day)
        new_silver_price_data = get_price_data('silver', start_date=next_day)
        
        bulk_price_data(new_gold_price_data, 'Gold')
        bulk_price_data(new_silver_price_data, 'Silver')
        
        print('최신 데이터 bulk 완료')
        return
    
    else:
        print(f'{after_n}일이 지나지 않음')
        return

bulk_data_after_latest_date()