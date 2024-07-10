import asyncio
import datetime
import json
import os

import pandas as pd
import requests
from bs4 import BeautifulSoup as bs
from dotenv import load_dotenv

from app.database.schedule_database import schedule_save_apt_rent


def apt_rent_parsing():
    load_dotenv()

    dir = os.path.dirname(__file__)
    data_path = os.path.join(dir, '../../static_data/legal_info_b_seoul.csv')

    df = pd.read_csv(data_path)

    current = datetime.datetime.now()
    deal_ymd = current.strftime('%Y%m')

    LAWD_CD_list = df['법정동시군구코드'].unique()

    api_key = os.getenv('API_KEY')

    column_nm = ['갱신요구권사용', '건축년도', '계약구분', '계약기간', '년', '법정동', '보증금액',
                 '아파트', '월', '월세금액', '일', '전용면적', '종전계약보증금', '종전계약월세',
                 '지번', '지역코드', '층']
    total = pd.DataFrame()

    for i in range(len(LAWD_CD_list)):
        url = 'http://openapi.molit.go.kr:8081/OpenAPI_ToolInstallPackage/service/rest/RTMSOBJSvc/getRTMSDataSvcAptRent'
        params = {'serviceKey': api_key, 'LAWD_CD': LAWD_CD_list[i], 'DEAL_YMD': deal_ymd}

        res = requests.get(url, params)
        soup = bs(res.text, 'xml')
        items = soup.find_all('item')

        for k in range(len(items)):
            df_raw = []
            for j in column_nm:
                try:
                    df_raw.append(items[k].find(j).text)
                except:
                    df_raw.append('')

            df = pd.DataFrame(df_raw).T
            df.columns = column_nm

            total = pd.concat([total, df])

    total.columns = column_nm

    return total

def apt_rent_preprocess(parsing_data: pd.DataFrame):
    dir = os.path.dirname(__file__)
    data_path = os.path.join(dir, '../../static_data/legal_info_b_seoul.csv')

    legal_info_b_seoul = pd.read_csv(data_path).astype({'법정동시군구코드': str, '동리명': str})

    apt_rent = parsing_data

    apt_rent.rename(columns={'지역코드': '법정동시군구코드'}, inplace=True)
    apt_rent.rename(columns={'법정동': '읍면동명'}, inplace=True)

    apt_rent = apt_rent[['건축년도', '계약기간', '읍면동명', '지번', '아파트', '보증금액', '월세금액', '전용면적', '층', '법정동시군구코드', '년', '월', '일']]

    apt_rent = apt_rent[apt_rent['건축년도'].notnull()]
    apt_rent = apt_rent.astype({'법정동시군구코드': str})

    apt_rent_2 = pd.merge(apt_rent, legal_info_b_seoul, on=['읍면동명'], how='left')

    apt_rent_2['시도명'] = apt_rent_2['시도명'].str.strip()
    apt_rent_2['시군구명'] = apt_rent_2['시군구명'].str.strip()
    apt_rent_2['동리명'] = apt_rent_2['동리명'].str.strip()

    apt_rent_2 = apt_rent_2.where(pd.notnull(apt_rent_2), '')
    apt_rent_2['주소'] = apt_rent_2['시도명'] + ' ' + apt_rent_2['시군구명'] + ' ' + apt_rent_2['읍면동명']

    apt_rent_2['주소'] = apt_rent_2['주소'].str.replace('  ', ' ')
    apt_rent_2['주소'] = apt_rent_2['주소'].str.strip()

    apt_rent_2 = apt_rent_2.replace('충청북도 청주시 상당구 북문로2가동', '충청북도 청주시 상당구 북문로2가')
    apt_rent_2 = apt_rent_2.replace('충청북도 청주시 상당구 북문로3가동', '충청북도 청주시 상당구 북문로3가')
    apt_rent_2 = apt_rent_2.replace('충청북도 청주시 상당구 남문로1가동', '충청북도 청주시 상당구 남문로1가')

    apt_rent_2['계약날짜'] = pd.to_datetime(apt_rent_2['년'] + apt_rent_2['월'] + apt_rent_2['일'],
                                        format='%Y%m%d').dt.strftime('%Y%m%d')
    apt_rent_2.astype(str)

    return apt_rent_2

def apt_rent_select_columns(preprocessed_data: pd.DataFrame):
    apt_rent_final = preprocessed_data[['건축년도', '아파트', '보증금액', '월세금액', '계약날짜', '계약기간', '전용면적', '주소', '법정동코드', '층']]
    apt_rent_final_copy = apt_rent_final.copy()
    apt_rent_final_copy.rename(columns={'건축년도': 'built_year', '아파트': 'apt_name', '보증금액': 'security_deposit',
                                        '월세금액': 'monthly_rent', '계약날짜': 'contract_date', '계약기간': 'lease_term',
                                        '전용면적': 'net_leasable_area',
                                        '주소': 'address', '법정동코드': 'legal_code', '층': 'floor'}, inplace=True)
    apt_rent_final_copy.astype(str)

    apt_rent_final_copy[apt_rent_final_copy.select_dtypes(include=['object']).columns] = apt_rent_final_copy.select_dtypes(include=['object']).apply(
        lambda x: x.str.strip())

    return apt_rent_final_copy


async def schedule_apt_rent():
    df = apt_rent_parsing()
    df = apt_rent_preprocess(df)
    df = apt_rent_select_columns(df)

    total_json = json.loads(df.to_json(orient='records'))

    await schedule_save_apt_rent(total_json)

if __name__ == '__main__':
    print('test')
    # df = apt_rent_parsing()
    # df = apt_rent_preprocess(df)
    # df = apt_rent_select_columns(df)
    #
    # total_json = json.loads(df.to_json(orient='records'))  # columns, records, index, values
    # print(total_json)
