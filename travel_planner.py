import argparse
import json
import os
from datetime import datetime

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


def main():
    args = parse_args()
    gemini_api_key, kakao_rest_api_key = load_api_keys()

    print("[1/3] 1차 추천 생성 중(Gemini)...")

    try:
        recommendation = generate_recommendation(
            args.date,
            gemini_api_key,
        )
    except Exception as error:
        print(f"  - 오류: Gemini 추천 생성 실패: {error}")
        raise SystemExit(1)

    print(
        f'  - recommended_city: '
        f'"{recommendation["recommended_city"]}"'
    )

    print("\n1차 추천 JSON:")
    print(
        json.dumps(
            recommendation,
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()