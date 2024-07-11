import datetime
import json
import os

import pandas as pd
import requests
from bs4 import BeautifulSoup as bs
from dotenv import load_dotenv

from app.database.startup_database import start_save_apt_trade

load_dotenv()
dir = os.path.dirname(__file__)
data_path = os.path.join(dir, '../../static_data/legal_info_b_seoul.csv')


async def apt_trade_parsing(deal_ymd):

    df = pd.read_csv(data_path)

    LAWD_CD_list = df['법정동시군구코드'].unique()

    api_key = os.getenv('API_KEY')

    column_nm = ['거래금액', '거래유형', '건축년도', '년', '도로명', '도로명건물본번호코드', '도로명건물부번호코드',
                 '도로명시군구코드', '도로명일련번호코드', '도로명지상지하코드', '도로명코드', '동', '등기일자', '매도자', '매수자', '법정동', '법정동본번코드',
                 '법정동부번코드', '법정동시군구코드', '법정동읍면동코드', '법정동지번코드', '아파트', '월', '일', '일련번호', '전용면적',
                 '중개사소재지', '지번', '지역코드', '층']

    total = pd.DataFrame()

    for i in range(len(LAWD_CD_list)):
        url = 'http://openapi.molit.go.kr/OpenAPI_ToolInstallPackage/service/rest/RTMSOBJSvc/getRTMSDataSvcAptTradeDev'
        params = {'serviceKey': api_key, 'pageNo': '1', 'numOfRows': '1000000', 'LAWD_CD': LAWD_CD_list[i], 'DEAL_YMD': deal_ymd}

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


async def apt_trade_preprocess(parsing_data: pd.DataFrame):
    dir = os.path.dirname(__file__)
    data_path = os.path.join(dir, '../../static_data/legal_info_b_seoul.csv')

    legal_info_b = pd.read_csv(data_path).astype({'법정동코드': str})
    parsing_data['법정동코드'] = parsing_data['법정동시군구코드'].astype(str) + parsing_data['법정동읍면동코드'].astype(str)

    apt_trade = parsing_data[['거래금액', '거래유형', '건축년도', '전용면적', '법정동', '법정동코드', '아파트', '층', '년', '월', '일']]
    apt_trade = apt_trade.copy()

    apt_trade['계약날짜'] = pd.to_datetime(apt_trade['년'] + apt_trade['월'] + apt_trade['일'], format='%Y%m%d').dt.strftime('%Y%m%d')

    apt_trade_final = pd.merge(apt_trade, legal_info_b, on='법정동코드', how='left')

    return apt_trade_final


async def apt_trade_select_columns(preprocessed_data: pd.DataFrame):
    apt_trade_final = preprocessed_data[['건축년도', '아파트', '거래금액', '계약날짜', '전용면적', '주소', '법정동코드', '층']]
    apt_trade_final_copy = apt_trade_final.copy()
    apt_trade_final_copy.rename(columns={'건축년도': 'built_year', '아파트': 'apt_name', '거래금액': 'trade_price',
                                   '계약날짜': 'contract_date', '전용면적': 'net_leasable_area',
                                   '주소': 'address', '법정동코드': 'legal_code', '층': 'floor'}, inplace=True)
    apt_trade_final_copy['trade_price'].astype(float)
    apt_trade_final_copy['net_leasable_area'].astype(float)
    apt_trade_final_copy['price_per_area'] = apt_trade_final_copy['trade_price'] / apt_trade_final_copy['net_leasable_area']

    apt_trade_final_copy.astype(str)
    apt_trade_final_copy[apt_trade_final_copy.select_dtypes(include=['object']).columns] = apt_trade_final_copy.select_dtypes(include=['object']).apply(
        lambda x: x.str.strip())

    return apt_trade_final_copy


async def startup_apt_trade():
    current = datetime.datetime.now()
    deal_y = int(current.strftime('%Y'))
    deal_m = int(current.strftime('%m'))

    for i in range(deal_m, 6, -1):
        deal_ymd = str(deal_y) + str(i).zfill(2)
        df = await apt_trade_parsing(deal_ymd)
        df = await apt_trade_preprocess(df)
        df = await apt_trade_select_columns(df)
        total_json = json.loads(df.to_json(orient='records'))  # columns, records, index, values
        await start_save_apt_trade(total_json)
        print(f'{deal_ymd} apt_trade save success')


    for i in range(deal_y - 1, 2022, -1):
        for j in range(1, 2, 1): # 13을 2로 테스트...
            deal_ymd = str(i) + str(j).zfill(2)
            df = await apt_trade_parsing(deal_ymd)
            df = await apt_trade_preprocess(df)
            df = await apt_trade_select_columns(df)

            total_json = json.loads(df.to_json(orient='records'))  # columns, records, index, values
            await start_save_apt_trade(total_json)

            print(f'{deal_ymd} apt_trade save success')


if __name__ == '__main__':
    print('test')