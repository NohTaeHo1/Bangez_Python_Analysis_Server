import datetime
import json
import os

import pandas as pd
import requests
from bs4 import BeautifulSoup as bs
from dotenv import load_dotenv

from app.database.startup_database import start_save_school

load_dotenv()

async def school_parsing():
    load_dotenv()

    api_key = os.getenv('NEIS_API_KEY')

    column_nm = ['시도교육청코드', '시도교육청명', '행정표준코드', '학교명', '영문학교명', '학교종류명', '시도명',
                 '관할조직명', '설립명', '도로명우편번호', '도로명주소', '도로명상세주소', '전화번호', '홈페이지주소',
                 '남녀공학구분명', '팩스번호', '고등학교구분명', '산업체특별학급존재여부', '고등학교일반전문구분명', '특수목적고등학교계열명', '입시전후기구분명',
                 '주야구분명', '설립일자', '개교기념일', '수정일자']
    schools = ["초등학교", "중학교", "고등학교"]

    for i in range(3):
        total = pd.DataFrame()

        url = 'https://open.neis.go.kr/hub/schoolInfo'
        pIndex = 1

        while True:
            params = {'KEY': api_key, 'Type': 'xml', 'pIndex': f'{pIndex}', 'pSize': '1000',
                      'SCHUL_KND_SC_NM': schools[i], 'LCTN_SC_NM': '서울특별시'}

            res = requests.get(url, params)

            soup = bs(res.text, 'xml')
            items = soup.find_all('row')

            if not items:
                break

            for k in range(len(items)):
                df_list = items[k].find_all()
                df_raw = []

                for l in range(len(df_list)):
                    df_raw.append(df_list[l].text)
                df = pd.DataFrame(df_raw).T

                df.columns = column_nm
                total = pd.concat([total, df])
            pIndex += 1

    try:
        total.columns = column_nm
    except Exception as e:
        print('apt_rent colunm error')

    return total


async def school_select_columns(parsing_data: pd.DataFrame):
    school_final = parsing_data[['학교명', '학교종류명', '도로명주소', '홈페이지주소']]
    school_final = school_final.copy()
    school_final.rename(columns={'학교명': 'school_name', '학교종류명': 'school_type', '도로명주소': 'address',
                                 '홈페이지주소': 'homepage'}, inplace=True)
    school_final.astype(str)
    school_final[
        school_final.select_dtypes(include=['object']).columns] = school_final.select_dtypes(
        include=['object']).apply(lambda x: x.str.strip())

    return school_final

async def startup_school():
    df = await school_parsing()
    df = await school_select_columns(df)

    total_json = json.loads(df.to_json(orient='records'))  # columns, records, index, values
    await start_save_school(total_json)

    print(f'school save success')

if __name__ == '__main__':
    print('test')