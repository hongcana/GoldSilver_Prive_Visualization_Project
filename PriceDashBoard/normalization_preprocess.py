from functools import reduce
import pandas as pd

def normalize_column(df, column: str):
    """
    DataFrame에서 특정 column을 정규화하는 메소드.
    :param column: 정규화할 column의 이름
    :return: 정규화된 column
    """

    # 정규화 공식(데이터를 일정한 범위로 조정한다)
    # 결과적으로 정규화된 값은 0과 1사이에 취하게 됨
    normalized_column = (df[column] - df[column].min()) / (df[column].max() - df[column].min())
    return normalized_column

# 풀이 내용 확인
# https://zambbon.tistory.com/entry/reduce%EC%99%80-lambda%EB%A5%BC-%ED%86%B5%ED%95%9C-%EB%8D%B0%EC%9D%B4%ED%84%B0%ED%94%84%EB%A0%88%EC%9E%84-merge-%ED%95%A8%EC%88%98
def merge_dataframes(df_list: list, merge_option: str, column: str):
    """
    여러 개의 DataFrame을 공통 column을 기준으로 병합하는 메소드.
    :param df_list: 병합할 DataFrame들의 리스트
    :param merge_option: 병합 옵션 ('inner', 'outer', 'left', 'right' 중 하나)
    :param column: 병합 기준이 되는 공통 column의 이름
    :return: 병합된 DataFrame
    """
    merged_df = reduce(lambda x, y: pd.merge(x, y, how=merge_option, on=column), df_list)
    return merged_df