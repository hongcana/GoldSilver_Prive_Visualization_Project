from datetime import datetime, timedelta

from django.shortcuts import render
from .get_data_for_visualization import _get_normalization_data, _get_time_series_data
from .data_preprocess import data_preprocess
from .data_visualization import _visualize_price_data, _scatter_plot_graph, _visualize_normalization_data

import matplotlib as mpl

# GUI 에러 방지 
mpl.use('Agg')

def index(request):
    # 시작일 입력값이 들어온다면
    before_month_date = datetime.now() - timedelta(days=30)
    
    start_date = request.GET.get('start_date') or before_month_date.strftime("%Y-%m-%d")        
    end_date = request.GET.get('end_date') or datetime.now().strftime("%Y-%m-%d")

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
        normalization_graph = None
        scatter_graph = None
            
        return render(request, 'dashboard/index.html', {
            'start_date': start_date,
            'end_date': end_date,
            'gold_price_graph': gold_price_graph,
            'silver_price_graph': silver_price_graph,
            'normalization_graph' : normalization_graph,
            'scatter_graph': scatter_graph,
            'error_message': error_message,
            'datas' :  [gold_analysis_indicator, silver_analysis_indicator]
        })
    
    # 이 구간의 금 / 은 가격 데이터프레임을 가져옴
    gold_price_df, silver_price_df = _get_time_series_data(start_date, end_date)
    
    # 정규화한 금 / 은 가격 통합 데이터프레임
    total_df = _get_normalization_data(start_date, end_date)
        
    # 시각화 이미지를 encode한 값을 가져옴
    gold_price_visualization_img = _visualize_price_data(gold_price_df)
    silver_price_visualization_img = _visualize_price_data(silver_price_df)
    normalization_visualization_img = _visualize_normalization_data(total_df)
    scatter_visualization_img = _scatter_plot_graph()
    
    # 이미지 / json 데이터를 전달하여 지표와 시각화 결과를 전송
    context = {
        'gold_price_graph' : gold_price_visualization_img,
        'silver_price_graph' : silver_price_visualization_img,
        'normalization_graph' : normalization_visualization_img,
        'scatter_graph' : scatter_visualization_img,
        'datas' :  [gold_analysis_indicator, silver_analysis_indicator],
        'start_date': start_date,
        'end_date': end_date 
    }
    
    return render(request, 'dashboard/index.html', context=context)