import datetime
import json
import os

import pandas as pd
import requests
from bs4 import BeautifulSoup as bs
from dotenv import load_dotenv

from app.database.startup_database import start_save_officetel_rent

load_dotenv()
dir = os.path.dirname(__file__)
data_path = os.path.join(dir, '../../static_data/legal_info_b_seoul.csv')


async def officetel_rent_parsing(deal_ymd):

    df = pd.read_csv(data_path)

    LAWD_CD_list = df['법정동시군구코드'].unique()

    api_key = os.getenv('API_KEY')

    column_nm = ['갱신요구권사용', '건축년도', '계약구분', '계약기간', '년', '단지', '법정동',
                 '보증금', '시군구', '월', '월세', '일', '전용면적', '종전계약보증금',
                 '종전계약월세', '지번', '지역코드', '층']

    total = pd.DataFrame()

    for i in range(len(LAWD_CD_list)):
        url = 'http://openapi.molit.go.kr/OpenAPI_ToolInstallPackage/service/rest/RTMSOBJSvc/getRTMSDataSvcOffiRent'
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
                    df_raw.append('존재하지 않음')

            df = pd.DataFrame(df_raw).T
            df.columns = column_nm

            total = pd.concat([total, df])

    try:
        total.columns = column_nm
    except Exception as e:
        print('apt_rent colunm error')
    return total


async def officetel_rent_preprocess(parsing_data: pd.DataFrame):

    legal_info_b_seoul = pd.read_csv(data_path).astype({'법정동코드': str, '동리명': str})

    officetel_rent = parsing_data

    print(officetel_rent.head(2).T)
    officetel_rent = officetel_rent[
        ['건축년도', '계약기간', '법정동', '보증금', '시군구', '월세', '전용면적', '지번', '층', '지역코드', '년', '월', '일', '단지']]
    officetel_rent = officetel_rent.copy()
    officetel_rent.rename(columns={'지역코드': '법정동시군구코드'}, inplace=True)
    officetel_rent.rename(columns={'법정동': '읍면동명'}, inplace=True)

    officetel_rent = officetel_rent[officetel_rent['건축년도'].notnull()]
    officetel_rent = officetel_rent.astype({'읍면동명': str})

    officetel_rent_2 = pd.merge(officetel_rent, legal_info_b_seoul, on=['읍면동명'], how='left')

    officetel_rent_2 = officetel_rent_2.where(pd.notnull(officetel_rent_2), '')

    officetel_rent_2['시도명'] = officetel_rent_2['시도명'].str.strip()
    officetel_rent_2['시군구명'] = officetel_rent_2['시군구명'].str.strip()
    officetel_rent_2['읍면동명'] = officetel_rent_2['읍면동명'].str.strip()

    officetel_rent_2 = officetel_rent_2.where(pd.notnull(officetel_rent_2), '')
    officetel_rent_2['주소'] = officetel_rent_2['시도명'] + ' ' + officetel_rent_2['시군구명'] + ' ' + officetel_rent_2['읍면동명']

    officetel_rent_2['주소'] = officetel_rent_2['주소'].str.replace('  ', ' ')
    officetel_rent_2['주소'] = officetel_rent_2['주소'].str.strip()

    officetel_rent_2 = officetel_rent_2.replace('충청북도 청주시 상당구 북문로2가동', '충청북도 청주시 상당구 북문로2가')
    officetel_rent_2 = officetel_rent_2.replace('충청북도 청주시 상당구 북문로3가동', '충청북도 청주시 상당구 북문로3가')
    officetel_rent_2 = officetel_rent_2.replace('충청북도 청주시 상당구 남문로1가동', '충청북도 청주시 상당구 남문로1가')

    officetel_rent_2['계약날짜'] = pd.to_datetime(officetel_rent_2['년'] + officetel_rent_2['월'] + officetel_rent_2['일'],
                                              format='%Y%m%d').dt.strftime('%Y%m%d')

    return officetel_rent_2


async def officetel_rent_select_columns(preprocessed_data: pd.DataFrame):
    officetel_rent_final = preprocessed_data[['건축년도', '단지', '보증금', '월세', '계약날짜', '계약기간', '전용면적', '주소', '법정동코드', '층']]
    officetel_rent_final_copy = officetel_rent_final.copy()
    officetel_rent_final_copy.rename(columns={'건축년도': 'built_year', '단지': 'officetel_name', '보증금': 'security_deposit',
                                              '월세': 'monthly_rent', '계약날짜': 'contract_date',
                                              '계약기간': 'lease_term', '전용면적': 'net_leasable_area', '주소': 'address',
                                              '법정동코드': 'legal_code', '층': 'floor'}, inplace=True)
    officetel_rent_final_copy.astype(str)

    officetel_rent_final_copy[officetel_rent_final_copy.select_dtypes(include=['object']).columns] = officetel_rent_final_copy.select_dtypes(include=['object']).apply(
        lambda x: x.str.strip())

    return officetel_rent_final_copy


async def startup_officetel_rent():
    current = datetime.datetime.now()
    deal_y = int(current.strftime('%Y'))
    deal_m = int(current.strftime('%m'))

    for i in range(deal_m, 6, -1):
        deal_ymd = str(deal_y) + str(i).zfill(2)
        df = await officetel_rent_parsing(deal_ymd)
        df = await officetel_rent_preprocess(df)
        df = await officetel_rent_select_columns(df)
        total_json = json.loads(df.to_json(orient='records'))  # columns, records, index, values
        await start_save_officetel_rent(total_json)
        print(f'{deal_ymd} officetel_rent save success')


    for i in range(deal_y - 1, 2022, -1):
        for j in range(1, 2, 1): # 13을 2로 테스트...
            deal_ymd = str(i) + str(j).zfill(2)
            df = await officetel_rent_parsing(deal_ymd)
            df = await officetel_rent_preprocess(df)
            df = await officetel_rent_select_columns(df)

            total_json = json.loads(df.to_json(orient='records'))  # columns, records, index, values
            await start_save_officetel_rent(total_json)
            print(f'{deal_ymd} officetel_rent save success')

if __name__ == '__main__':
    print('test')
