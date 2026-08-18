import argparse
import json
import os
from datetime import datetime

import requests

from dotenv import load_dotenv
from google import genai
from google.genai import types


def validate_date(value):
    try:
        datetime.strptime(value, "%Y-%m-%d")
        return value
    except ValueError:
        raise argparse.ArgumentTypeError(
            '날짜는 "YYYY-MM-DD" 형식으로 입력해야 합니다.'
        )


def parse_args():
    parser = argparse.ArgumentParser(
        description="국내 여행지 추천 프로그램"
    )

    parser.add_argument(
        "-date",
        "--date",
        dest="date",
        required=True,
        type=validate_date,
        help='여행 날짜를 "YYYY-MM-DD" 형식으로 입력하세요.',
    )

    return parser.parse_args()


def load_api_keys():
    load_dotenv()

    gemini_api_key = os.getenv("GEMINI_API_KEY")
    kakao_rest_api_key = os.getenv("KAKAO_REST_API_KEY")

    missing_keys = []

    if not gemini_api_key:
        missing_keys.append("GEMINI_API_KEY")

    if not kakao_rest_api_key:
        missing_keys.append("KAKAO_REST_API_KEY")

    if missing_keys:
        print("[오류] 다음 API 키가 설정되지 않았습니다:")
        for key_name in missing_keys:
            print(f"  - {key_name}")

        print("\n.env 파일에 API 키를 설정한 뒤 다시 실행하세요.")
        raise SystemExit(1)

    return gemini_api_key, kakao_rest_api_key


def generate_recommendation(date, gemini_api_key):
    response_schema = {
        "type": "object",
        "properties": {
            "recommended_city": {
                "type": "string"
            },
            "weather": {
                "type": "string"
            },
            "events": {
                "type": "array",
                "items": {
                    "type": "string"
                }
            },
            "reason": {
                "type": "string"
            },
        },
        "required": [
            "recommended_city",
            "weather",
            "events",
            "reason",
        ],
        "additionalProperties": False,
    }

    prompt = f"""
여행 날짜는 {date}입니다.

해당 시기에 국내에서 여행하기 좋은 지역 한 곳을 추천하세요.
날씨는 정확한 예보가 아니라 해당 시기의 일반적인 날씨를 설명하세요.
행사나 축제 후보는 1개에서 3개를 제시하세요.
추천 이유는 2문장에서 4문장으로 작성하세요.
모든 내용은 한국어로 작성하세요.
"""

    client = genai.Client(api_key=gemini_api_key)

    try:
        for attempt in range(2):
            try:
                response = client.models.generate_content(
                    model="gemini-3.5-flash-lite",
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_json_schema=response_schema,
                    ),
                )

                return json.loads(response.text)

            except json.JSONDecodeError:
                if attempt == 0:
                    prompt += (
                        "\n이전 응답을 JSON으로 해석할 수 없었습니다. "
                        "필수 키만 포함한 올바른 JSON으로 다시 출력하세요."
                    )
                    print("  - JSON 파싱 실패, 1회 재시도합니다.")
                    continue

                raise RuntimeError(
                    "Gemini 응답을 JSON으로 변환하지 못했습니다."
                )
    finally:
        client.close()

def to_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def search_restaurants(city, kakao_rest_api_key):
    url = "https://dapi.kakao.com/v2/local/search/keyword.json"

    headers = {
        "Authorization": f"KakaoAK {kakao_rest_api_key}"
    }

    params = {
        "query": f"{city} 맛집",
        "size": 5,
    }

    response = requests.get(
        url,
        headers=headers,
        params=params,
        timeout=10,
    )

    response.raise_for_status()

    documents = response.json().get("documents", [])
    restaurants = []

    for document in documents:
        restaurant = {
            "name": document.get("place_name", ""),
            "address": (
                document.get("road_address_name")
                or document.get("address_name", "")
            ),
            "category": document.get("category_name", ""),
            "url": document.get("place_url", ""),
            "x": to_float(document.get("x")),
            "y": to_float(document.get("y")),
        }

        restaurants.append(restaurant)

    return restaurants

def generate_report(
    date,
    recommendation,
    restaurants,
    errors,
    gemini_api_key,
):
    input_data = {
        "date": date,
        "recommendation": recommendation,
        "restaurants": restaurants,
        "errors": errors,
    }

    prompt = f"""
아래 JSON 데이터를 바탕으로 국내 여행 추천 리포트를 작성하세요.

{json.dumps(input_data, ensure_ascii=False, indent=2)}

반드시 Markdown 형식으로 작성하고 다음 순서를 지키세요.

# {date} 국내 여행 추천 리포트
## 추천 지역
## 추천 이유
## 날씨 요약
## 행사/축제
## 맛집 추천
## 1일 일정 제안
### 오전
### 오후
### 저녁
## 오류 요약(errors)

작성 규칙:
- 제공된 JSON 데이터만 활용하세요.
- 맛집 목록이 비어 있으면 "데이터 없음"이라고 작성하세요.
- 맛집의 이름, 주소, 카테고리, URL을 보기 좋게 정리하세요.
- 오류 목록이 비어 있으면 "없음"이라고 작성하세요.
- 새로운 맛집이나 실제 행사 일정을 임의로 추가하지 마세요.
- 전체 내용은 한국어로 작성하세요.
"""

    client = genai.Client(api_key=gemini_api_key)

    try:
        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=prompt,
        )

        if not response.text:
            raise RuntimeError("Gemini가 빈 리포트를 반환했습니다.")

        return response.text
    finally:
        client.close()

def main():
    args = parse_args()
    gemini_api_key, kakao_rest_api_key = load_api_keys()
    errors = []

    print("[1/3] 1차 추천 생성 중(Gemini)...")

    try:
        recommendation = generate_recommendation(
            args.date,
            gemini_api_key,
        )
    except Exception as error:
        print(f"  - 오류: Gemini 추천 생성 실패: {error}")
        raise SystemExit(1)

    city = recommendation["recommended_city"]
    print(f'  - recommended_city: "{city}"')

    print("[2/3] 맛집 검색 중(Kakao)...")

    try:
        restaurants = search_restaurants(
            city,
            kakao_rest_api_key,
        )

        if restaurants:
            print(f"  - 맛집 {len(restaurants)}곳 검색 완료")
        else:
            print("  - 검색 결과 0건, 데이터 없음으로 진행합니다.")
            errors.append(
                {
                    "step": "place_search",
                    "type": "EMPTY_RESULT",
                    "message": f"0 results for query={city} 맛집",
                }
            )

    except requests.RequestException as error:
        restaurants = []

        status_code = (
            error.response.status_code
            if error.response is not None
            else None
        )

        error_type = (
            "AUTH_ERROR"
            if status_code in (401, 403)
            else "API_ERROR"
        )

        errors.append(
            {
                "step": "place_search",
                "type": error_type,
                "message": (
                    f"HTTP {status_code}"
                    if status_code
                    else str(error)
                ),
            }
        )

        print(f"  - 오류: Kakao 장소 검색 실패: {error}")
        print("  - 맛집은 데이터 없음으로 처리하고 계속 진행합니다.")

    print("[3/3] 최종 리포트 생성 중(Gemini)...")

    try:
        report = generate_report(
            args.date,
            recommendation,
            restaurants,
            errors,
            gemini_api_key,
        )
        print("  - 리포트 생성 완료")

    except Exception as error:
        errors.append(
            {
                "step": "report_generation",
                "type": "API_ERROR",
                "message": str(error),
            }
        )

        print(f"  - 오류: 최종 리포트 생성 실패: {error}")
        raise SystemExit(1)

if __name__ == "__main__":
    main()