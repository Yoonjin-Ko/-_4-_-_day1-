import pytest
from pydantic import ValidationError
from 종합실습 import WeatherSchema


# 정상 데이터 테스트
def test_weather_success():

    data = WeatherSchema(
        latitude=37.55,
        longitude=127.0,
        temperature=23.2,
        precipitation_probability=50
    )

    assert data.latitude == 37.55
    assert data.temperature == 23.2



# 온도 범위 오류 테스트
def test_temperature_fail():

    with pytest.raises(ValidationError):

        WeatherSchema(
            latitude=37.55,
            longitude=127.0,
            temperature=200,
            precipitation_probability=50
        )



# 강수확률 범위 오류 테스트
def test_probability_fail():

    with pytest.raises(ValidationError):

        WeatherSchema(
            latitude=37.55,
            longitude=127.0,
            temperature=20,
            precipitation_probability=150
        )
