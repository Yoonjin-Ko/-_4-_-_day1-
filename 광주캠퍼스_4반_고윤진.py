"""
================================================================================
[실습 2] 파일 I/O, 예외 처리, Pydantic 검증 파이프라인
================================================================================
#작성자: 고윤진
#작성목적 : 파일 I/O, 예외 처리, Pydantic 검증 파이프라인 실습
#작성일: 2026-07-20
#변경내역:
#    v1.0 (2026-07-20) 최초 작성
================================================================================
"""

#1)예외처리+파일읽기
import json, logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def safe_load_csv(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        logger.info("로딩 성공")
        return data
    except FileNotFoundError:
        logger.error("파일 없음")
        return None
    finally:
        print("로딩 종료")

Practice2 = safe_load_csv("Python_Practice2_Data.json")
result = safe_load_csv("없는파일.json")

assert result is None
print("파일 없음 체크 통과")


#2)Pydantic v2 스키마 정의
from pydantic import BaseModel, Field, ValidationError
from typing import Optional

class SalesRecord(BaseModel):
    month: str = Field(min_length=1)
    region: str = Field(min_length=1)
    amount: float = Field(gt=0)
    category: Optional[str] = None

#3) 검증 파이프라인 (valid / errors 분리)
def validate_records(data):
    valid, errors = [], []
    for i, row in enumerate(data):
        try:
            valid.append(SalesRecord(**row))
        except ValidationError as e:
            print(e)
            errors.append({"row": i, "error": str(e)})
    return valid, errors

valid, errors = validate_records(Practice2)
print(f"유효: {len(valid)}건, 오류: {len(errors)}건")

#4)결과 파일 저장 + 재로딩 확인
import csv
#valid to csv
def valid_to_csv(valid, path):
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["month", "region", "amount", "category"]
        )

        writer.writeheader()

        for record in valid:
            writer.writerow(record.model_dump())

valid_to_csv(valid, "valid.csv")

#errors to json
def errors_to_json(errors, path):
    Path(path).write_text(
    json.dumps(errors, ensure_ascii=False),
    encoding="utf-8"
)
errors_to_json(errors, "errors.json")


with open("valid.csv", encoding="utf-8") as f:
    valid_check = list(csv.DictReader(f))



with open("errors.json", encoding="utf-8") as f:
    errors_check = json.load(f)



test_data = [
    # valid 4건
    {"region": "서울", "category": "전자", "amount": 1500, "month": "2024-01"},
    {"region": "부산", "category": "의류", "amount": 800, "month": "2024-01"},
    {"region": "서울", "category": "의류", "amount": 1200, "month": "2024-02"},
    {"region": "대구", "category": "전자", "amount": 950, "month": "2024-01"},

    # errors 3건
    {"region": "대전", "category": "전자", "amount": -1100, "month": "2024-03"},
    {"region": "울산", "category": "의류", "amount": -890, "month": "2024-02"},
    {"region": "세종", "category": "전자", "amount": -1400, "month": "2024-03"},
]
test_valid, test_errors = validate_records(test_data)

assert len(test_valid) == 4
assert len(test_errors) == 3

valid_to_csv(test_valid, "valid.csv")
errors_to_json(test_errors, "errors.json")

with open("valid.csv", encoding="utf-8") as f:
    reloaded = list(csv.DictReader(f))

assert len(reloaded) == 4

print(f"valid={len(test_valid)}, errors={len(test_errors)}, reloaded={len(reloaded)}")