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

    # Seaborn 스타일 설정
    sns.set_style('darkgrid')

    # 그림의 크기를 설정
    plt.figure(figsize=(15, 7))

    # 데이터프레임에서 정규화된 금과 은 가격 열만 선택
    normalize_df_list = total_df[['normalize_gold', 'normalize_sliver']]

    # 정규화된 금과 은 가격 데이터를 그래프로 그림
    plt.plot(normalize_df_list, label=['Gold Normalization Price', 'Silver Normalization Price'])

    # x축 레이블 설정
    plt.xlabel('Date')
    # y축 레이블 설정
    plt.ylabel('Normalized Price')
    # x축 틱 레이블 회전 설정
    plt.xticks(rotation=30)
    # 범례 위치 설정
    plt.legend(loc='best')

    # 그래프 이미지를 저장하지 않고 바이트 데이터로 변환하기 위해 버퍼 사용
    buffer = BytesIO()
    # 그래프를 png 형식으로 버퍼에 저장
    plt.savefig(buffer, format='png')
    # 버퍼 포인터를 처음으로 되돌림
    buffer.seek(0)

    # 버퍼에서 바이트 값을 가져옴
    visialization_png = buffer.getvalue()
    # 버퍼를 닫음
    buffer.close()

    # 바이트 값을 base64로 인코딩
    graphic = base64.b64encode(visialization_png)
    # 인코딩된 값을 utf-8로 디코딩하여 문자열로 변환
    graphic = graphic.decode('utf-8')

    # 최종 결과 반환
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
    # 데이터베이스에서 금과 은 가격 데이터를 가져옴
    gold_queryset = MaterialsPriceModel.objects.filter(material_name_id=1).all().order_by('date').values()
    silver_queryset = MaterialsPriceModel.objects.filter(material_name_id=2).all().order_by('date').values()

    # 데이터베이스 쿼리셋을 데이터프레임으로 변환
    gold_df = pd.DataFrame.from_records(gold_queryset)
    silver_df = pd.DataFrame.from_records(silver_queryset)

    # 금과 은 데이터프레임을 병합
    df_list = [gold_df, silver_df]
    total_df = merge_dataframes(df_list, 'outer', 'date')

    # 열 이름 변경
    total_df.rename(columns={"price_x": "gold_price",
                               "price_y": "silver_price"}, inplace=True)

    # 날짜를 기준으로 정렬하고, 인덱스 설정 후 불필요한 열 삭제
    total_df.sort_values(by='date', inplace=True)
    total_df.set_index('date', inplace=True)
    total_df.drop('id_x', axis=1, inplace=True)
    total_df.drop('id_y', axis=1, inplace=True)
    total_df.drop('material_name_id_x', axis=1, inplace=True)
    total_df.drop('material_name_id_y', axis=1, inplace=True)

    # 금과 은 가격을 정규화
    total_df["gold_price_norm"] = normalize_column(total_df, "gold_price")
    total_df["silver_price_norm"] = normalize_column(total_df, "silver_price")

    # 데이터프레임에서 첫 세 개의 열만 선택
    normalize_df = total_df.iloc[:, 0:3]

    # 가격 데이터를 일정 기간만큼 이동시키기(shift가 0이기 때문에 움직이는게 없음)
    normalize_df["gold_price"] = normalize_df["gold_price"].shift(0)

    # 결측값 제거
    normalize_df = normalize_df.dropna()

    # 지정된 기간 동안의 백분율 변화 계산(지금 설정은 1년에 대한 백분율)
    normalize_df = normalize_df.pct_change(periods=365) * 100

    # 결측값 제거
    normalize_df = normalize_df.dropna()

    # 그래프 크기 설정
    fig, ax = plt.subplots(figsize=(15, 15))

    x = normalize_df["gold_price"]
    y = normalize_df["silver_price"]
    
    # 선형 회귀 계산
    slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)

    # 선형 회귀선의 데이터 생성
    line = slope * x + intercept

    # 산점도 그리기
    scatter_plot = sns.scatterplot(data=normalize_df, x="gold_price", y="silver_price", ax=ax,
                                    label="Gold & Silver")

    # 선형 회귀선
    sns.lineplot(x=x, y=line, ax=ax, color='red')

    # x축 y축 레이블 설정
    x_label = 'GOLD'
    y_label = 'SILVER'
    plt.xlabel(x_label, fontsize=15)
    plt.ylabel(y_label, fontsize=15)

    # 제목 설정
    plt.title('Gold & Silver Price Comparison: 1-Year Scatter Plot with Linear Regression', fontsize=15)

    # 범례 위치 설정
    plt.legend(loc='best')

    # x축 및 y축 범위 설정
    scatter_plot.set(xlim=(-50, 100))
    scatter_plot.set(ylim=(-50, 100))

    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    
    visialization_png = buffer.getvalue()
    buffer.close()

    # 바이트 값을 base64로 인코딩
    graphic = base64.b64encode(visialization_png)
    # 인코딩된 값을 utf-8로 디코딩하여 문자열로 변환
    graphic = graphic.decode('utf-8')

    return graphic