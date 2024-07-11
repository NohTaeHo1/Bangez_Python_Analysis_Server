import datetime
import json
import os

import pandas as pd
import requests
from bs4 import BeautifulSoup as bs
from dotenv import load_dotenv

from app.database.startup_database import start_save_city_park


async def city_park_parsing():
    load_dotenv()

    api_key = os.getenv('API_KEY')
    url = 'http://api.data.go.kr/openapi/tn_pubr_public_cty_park_info_api'
    params = {'serviceKey': api_key, 'pageNo': '0', 'numOfRows': '1000000', 'type': 'xml'}
    column_nm = ['manageNo', 'parkNm', 'parkSe', 'rdnmadr', 'lnmadr', 'latitude', 'longitude',
                 'parkAr', 'appnNtfcDate', 'institutionNm', 'phoneNumber', 'referenceDate', 'insttCode']

    res = requests.get(url, params)
    soup = bs(res.text, 'xml')
    items = soup.find_all('item')
    total = pd.DataFrame()

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


async def city_park_preprocess(parsing_data: pd.DataFrame):
    city_park = parsing_data
    city_park['parkNm'] = city_park['parkNm'].str.replace('&amp;lt;', '<').str.replace('&amp;gt;', '>')

    city_park['lnmadr'] = city_park['lnmadr'].fillna('')

    city_park_seoul = city_park[city_park['lnmadr'].str.startswith('서울특별시')]
    return city_park_seoul


async def city_park_select_columns(preprocessed_data: pd.DataFrame):
    city_park_seoul = preprocessed_data[preprocessed_data['institutionNm'].notnull()]

    city_park_seoul_final = city_park_seoul[['parkNm', 'parkSe', 'lnmadr', 'latitude', 'longitude', 'parkAr']]
    city_park_seoul_final = city_park_seoul_final.copy()

    city_park_seoul_final.rename(columns={'parkNm': 'park_name', 'parkSe': 'park_type', 'lnmadr': 'address',
                                          'parkAr': 'area'}, inplace=True)
    city_park_seoul_final.astype(str)
    city_park_seoul_final[
        city_park_seoul_final.select_dtypes(include=['object']).columns] = city_park_seoul_final.select_dtypes(
        include=['object']).apply(lambda x: x.str.strip())

    return city_park_seoul_final


async def startup_city_park():
    df = await city_park_parsing()
    df = await city_park_preprocess(df)
    df = await city_park_select_columns(df)

    total_json = json.loads(df.to_json(orient='records'))  # columns, records, index, values
    await start_save_city_park(total_json)
    print(f'city_park save success')


if __name__ == '__main__':
    print('test')
