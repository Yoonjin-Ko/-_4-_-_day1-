"""
================================================================================
[종합 실습] 실무형 수집, 검증, 품질 파이프라인
================================================================================
#작성자: 고윤진
#작성목적 : 데이터 수집 미니 파이프라인
#작성일: 2026-07-20
#변경내역:
#    v1.0 (2026-07-20) 최초 작성
================================================================================
"""

# 1)환경 준비
# venv 생성 후 requirements.txt 설치

# 2)비동기 API 데이터 수집
import asyncio
import httpx
import os
import time
import pandas as pd
from pydantic import BaseModel, Field, ValidationError

async def fetch(client, url):

    response = await client.get(url)

    response.raise_for_status()

    return response.json()

async def main():

    urls = [
        "https://api.open-meteo.com/v1/forecast?latitude=37.5665&longitude=126.9780&hourly=temperature_2m,precipitation_probability&forecast_days=3&timezone=Asia/Seoul",
        "https://countries.dev/alpha/KOR",
        "http://ip-api.com/json/8.8.8.8"
    ]

    async with httpx.AsyncClient() as client:
        results = await asyncio.gather(
            fetch(client, urls[0]),
            fetch(client, urls[1]),
            fetch(client, urls[2])
        )

    for i, result in enumerate(results, start=1):

        print(f"{i}번 API 응답 성공")

    print("3개 API 모두 정상 수집 완료")

    return results

# API 실행
results = asyncio.run(main())

weather_json = results[0]
country_json = results[1]
ip_json = results[2]


# 3)스키마 검증
class WeatherSchema(BaseModel):
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    temperature: float = Field(ge=-100, le=60)
    precipitation_probability: int = Field(ge=0, le=100)

class CountrySchema(BaseModel):
    name: str
    capital: str
    population: int = Field(gt=0)

class IPSchema(BaseModel):
    country: str
    city: str
    timezone: str


def validate_schema(schema, data):
    try:
        result = schema(**data)
        print("검증 성공")
        print(result)
        return result

    except ValidationError as e:
        print("검증 실패")
        print(e)
        return None


weather_data = {
    "latitude": weather_json["latitude"],
    "longitude": weather_json["longitude"],
    "temperature":
        weather_json["hourly"]["temperature_2m"][0],
    "precipitation_probability":
        weather_json["hourly"]["precipitation_probability"][0]
}


country_data = {
    "name": country_json["name"],
    "capital": country_json["capital"],
    "population": country_json["population"]
}


ip_data = {
    "country": ip_json["country"],
    "city": ip_json["city"],
    "timezone": ip_json["timezone"]
}


# 검증 실행
weather_result = validate_schema(
    WeatherSchema,
    weather_data
)

country_result = validate_schema(
    CountrySchema,
    country_data
)

ip_result = validate_schema(
    IPSchema,
    ip_data
)


save_data = []


if weather_result and country_result and ip_result:

    df = pd.DataFrame([{
        "latitude": weather_result.latitude,
        "longitude": weather_result.longitude,
        "temperature": weather_result.temperature,
        "precipitation_probability": weather_result.precipitation_probability,
        "country_name": country_result.name,
        "capital": country_result.capital,
        "population": country_result.population,
        "ip_country": ip_result.country,
        "city": ip_result.city,
        "timezone": ip_result.timezone
    }])

else:

    print("검증 실패 데이터 저장하지 않음")


# 4) 저장

os.makedirs(
    "data",
    exist_ok=True
)

# CSV 저장 시간 측정
start = time.perf_counter()


df.to_csv(
    "data/result.csv",
    index=False,
    encoding="utf-8"
)

csv_write_time = time.perf_counter() - start

# Parquet 저장 시간 측정
start = time.perf_counter()


df.to_parquet(
    "data/result.parquet",
    index=False
)

parquet_write_time = time.perf_counter() - start

print("저장 완료")
print(df)

# 성능 비교

start = time.perf_counter()

pd.read_csv("data/result.csv")

csv_read_time = time.perf_counter() - start

start = time.perf_counter()

pd.read_parquet("data/result.parquet")

parquet_read_time = time.perf_counter() - start

print("===== 저장 성능 비교 =====")
print(f"CSV Write: {csv_write_time:.6f} sec")
print(f"Parquet Write: {parquet_write_time:.6f} sec")

print("\n===== 읽기 성능 비교 =====")
print(f"CSV Read: {csv_read_time:.6f} sec")
print(f"Parquet Read: {parquet_read_time:.6f} sec")
