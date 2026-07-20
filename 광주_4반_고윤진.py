"""
================================================================================
[실습 1] 자료구조 집계 · 컴프리헨션 · 제너레이터
================================================================================
#작성자: 고윤진
#작성목적 : Practice1 자료구조, 컴프리헨션, 제너레이터 실습
#작성일: 2026-07-20
#변경내역:
#    v1.0 (2026-07-20) 최초 작성(json 파일 수정)
================================================================================
"""
import json
#파일 받아오기
with open("Python_Practice1_Data.json", "r", encoding="utf-8") as f:
    Practice1 = json.load(f)
#1)리스트/딕셔너리 컴프리헨션
#1.amount >= 1000인 거래만 필터링
filtered = [x for x in Practice1 if x["amount"] >= 1000]
#2.지역별 총 매출 dict를 컴프리헨션으로 계산
region_total = {region: sum(x["amount"] for x in filtered if x["region"] == region ) for region in{x["region"] for x in filtered}}
print(region_total)

#2)Counter+defaultdict
from collections import Counter, defaultdict
#Counter로 지역별 거래 건수 집계
region_counts = Counter(x["region"] for x in Practice1)
print(region_counts)
#카테고리별 amount 리스트
category_amounts = defaultdict(list)
for x in Practice1:
    category_amounts[x["category"]].append(x["amount"])
print(category_amounts)

#3)제너레이터-메모리 비교
#제너레이터 작성
def gen(data):
    for x in data:
        if x["amount"] >= 1000:
            yield x

filtered_gen = gen(Practice1)
#리스트 버전과 메모리 비교
import sys

print(sys.getsizeof(filtered))
print(sys.getsizeof(filtered_gen))

#4)종합 - 월별 카테고리 매출 집계
#sales 데이터를 month category 기준으로 그룹핑
from dataclasses import dataclass, field
from typing import TypedDict, Optional


#총 매출 dict를 완성(컴프리헨션+defaultdict)
monthly_category_sales = defaultdict(lambda: defaultdict(int))

for x in Practice1:
    monthly_category_sales[x["month"]][x["category"]] += x["amount"]


#일반 dict 변환 (dict comprehension)
total_sales = {
    month: dict(category_sales)
    for month, category_sales in monthly_category_sales.items()
}

print(total_sales)

#top3 금액 내림차순
top3 = sorted(
    Practice1,
    key=lambda x: x["amount"],
    reverse=True
)[:3]

print(top3)
