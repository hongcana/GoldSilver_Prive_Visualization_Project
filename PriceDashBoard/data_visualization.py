import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import base64

from io import BytesIO

from scipy import stats
from .models import MaterialsPriceModel
from .normalization_preprocess import normalize_column, merge_dataframes


def _visualize_normalization_data(total_df: pd.DataFrame):
    """정규화한 금 / 은 가격 데이터를 받아 시각화 이미지를 만든 후 decode 수행"""
    sns.set_style('darkgrid')
    
    plt.figure(figsize=(15, 7))

    normalize_df_list = total_df[['normalize_gold', 'normalize_sliver']]        
    
    plt.plot(normalize_df_list, label=['Gold Normalization Price', 
                                  'Silver Normalization Price'])
    
    plt.xlabel('Date')
    plt.ylabel('Normalized Price')
    plt.xticks(rotation=30)
    plt.legend(loc='best')
    
    # 저장 없이 템플릿에 띄우기 위해 바이트 데이터로 전환 후 utf-8 디코딩 
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    
    visialization_png = buffer.getvalue()
    buffer.close()
    
    graphic = base64.b64encode(visialization_png)
    graphic = graphic.decode('utf-8')
    
    return graphic


def _visualize_price_data(price_df: pd.DataFrame):
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

def _scatter_plot_graph():
    # 전체 데이터
    gold_queryset = MaterialsPriceModel.objects.filter(material_name_id=1).all().order_by('date').values()
    silver_queryset = MaterialsPriceModel.objects.filter(material_name_id=2).all().order_by('date').values()

    gold_df = pd.DataFrame.from_records(gold_queryset)
    silver_df = pd.DataFrame.from_records(silver_queryset)

    df_list = [gold_df, silver_df]
    total_df = merge_dataframes(df_list, 'outer', 'date')
    
    total_df.rename(columns={"price_x": "gold_price",
                               "price_y": "silver_price"}, inplace=True)
    
    # 날짜 기준 sort 및 인덱스 설정 후 필요없는 columns 정보 drop
    total_df.sort_values(by='date', inplace=True)
    total_df.set_index('date', inplace=True)
    total_df.drop('id_x', axis=1, inplace=True)
    total_df.drop('id_y', axis=1, inplace=True)
    total_df.drop('material_name_id_x', axis=1, inplace=True)
    total_df.drop('material_name_id_y', axis=1, inplace=True)
    
    total_df["gold_price_norm"] = normalize_column(total_df, "gold_price")
    total_df["silver_price_norm"] = normalize_column(total_df, "silver_price")
    
    # 데이터프레임에서 첫 세 개의 열만 선택
    normalize_df = total_df.iloc[:, 0:3]
    
    # 가격 데이터를 일정 기간만큼 이동시키기
    normalize_df["gold_price"] = normalize_df["gold_price"].shift(0)
    
    # 결측값 제거
    normalize_df = normalize_df.dropna()
    
    # 지정된 기간 동안의 백분율 변화 계산
    normalize_df = normalize_df.pct_change(periods=365) * 100
    
    # 결측값 제거
    normalize_df = normalize_df.dropna()
    
    fig, ax = plt.subplots(figsize=(15, 15))

    x = normalize_df["gold_price"]
    y = normalize_df["silver_price"]
    
    # 선형 회귀 계산
    slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)

    # 선형 회귀선의 데이터 생성
    line = slope * x + intercept

    # 산점도
    scatter_plot = sns.scatterplot(data=normalize_df, x="gold_price", y="silver_price", ax=ax,
                                    label="Gold & Silver")

    # 선형 회귀선
    sns.lineplot(x=x, y=line, ax=ax, color='red')

    # x축 y축 레이블 설정
    x_label = 'GOLD'
    y_label = 'SILVER'
    plt.xlabel(x_label, fontsize=15)
    plt.ylabel(y_label, fontsize=15)

    plt.title('Gold & Silver Price Comparison: 1-Year Scatter Plot with Linear Regression', fontsize=15)

    plt.legend(loc='best')

    # x축 및 y축 범위 설정
    scatter_plot.set(xlim=(-50, 100))
    scatter_plot.set(ylim=(-50, 100))

    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    
    visialization_png = buffer.getvalue()
    buffer.close()
    
    graphic = base64.b64encode(visialization_png)
    graphic = graphic.decode('utf-8')

    return graphic