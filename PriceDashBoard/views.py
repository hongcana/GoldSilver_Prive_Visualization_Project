from datetime import datetime, timedelta
from io import BytesIO

from django.shortcuts import render
from .models import MaterialsPriceModel
from django.shortcuts import render
from .data_preprocess import data_preprocess

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import base64

def _get_time_series_data(start_date, end_date):
    """모델로부터 start_date ~ end_date의 금 / 은 가격 정보를 DataFrame으로 가져오는 함수"""
    # 시작일과 끝 날짜 사이 일자와 가격 데이터를 가져옴 
    gold_data = MaterialsPriceModel.objects.filter(date__range=(start_date, end_date), material_name__exact=1).values('id', 'price')
    
    if not gold_data:
        raise ValueError(f"No gold price data available for the given date range: {start_date} ~ {end_date}")
    
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

def _visualize_price_date(price_df: pd.DataFrame):
    """입력된 데이터를 토대로 시각화 이미지를 만든 후 decode하는 함수"""
    
    sns.set_style('darkgrid')
    
    plt.figure(figsize=(15, 7))
    plt.plot(price_df['price'])
    
    plt.xlabel('Date', fontsize=14)
    plt.ylabel('Price ($)', fontsize=14)
    
    plt.xticks(rotation=30)
    
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    
    visialization_png = buffer.getvalue()
    buffer.close()
    
    graphic = base64.b64encode(visialization_png)
    graphic = graphic.decode('utf-8')
    
    return graphic

def index(request):
    # 시작일 입력값이 들어온다면
    start_date = request.GET.get('start_date')
    if start_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
    
    # 들어오지 않는다면 default로 오늘부터 30일 이전 설정
    else:
        start_date = datetime.today() - timedelta(days=30)
        
    end_date = request.GET.get('end_date')
    if end_date:
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
        
    else:
        end_date = datetime.today()
    
    # 분석 지표 json 호출
    gold_analysis_indicator = data_preprocess(1)
    silver_analysis_indicator = data_preprocess(2)
    
    # 해당 일자의 데이터가 있는지 확인
    try:
        gold_price_df, silver_price_df = _get_time_series_data(start_date, end_date)
    
    # 없다면 ValueError를 발생시켜 예외 처리
    # 프론트 단에서 오류 메시지 출력할 수 있도록 error_message 추가
    except ValueError as e:
        error_message = str(e)
        gold_price_graph = None
        silver_price_graph = None
        
        return render(request, 'dashboard/index.html', {
            'start_date': start_date,
            'end_date': end_date,
            'gold_price_graph': gold_price_graph,
            'silver_price_graph': silver_price_graph,
            'error_message': error_message,
            'datas' :  [gold_analysis_indicator, silver_analysis_indicator]
        })
    
    # 이 구간의 금 / 은 가격 데이터프레임을 가져옴
    gold_price_df, silver_price_df = _get_time_series_data(start_date, end_date)
    
    # 시각화 이미지를 encode한 값을 가져옴
    gold_price_visualization_img = _visualize_price_date(gold_price_df)
    silver_price_visualization_img = _visualize_price_date(silver_price_df)
    
    # 이미지 / json 데이터를 전달하여 지표와 시각화 결과를 전송
    context = {
        'gold_price_graph' : gold_price_visualization_img,
        'silver_price_graph' : silver_price_visualization_img,
        'datas' :  [gold_analysis_indicator, silver_analysis_indicator]
    }
    
    return render(request, 'dashboard/index.html', context=context)