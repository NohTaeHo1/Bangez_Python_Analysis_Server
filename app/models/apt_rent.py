# 데이터베이스 모델 정의 예시
from pydantic import BaseModel

class RentData(BaseModel):
    # 여기에 필드 정의
    field1: str
    field2: int
