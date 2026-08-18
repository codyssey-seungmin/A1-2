import argparse
import os
from datetime import datetime

from dotenv import load_dotenv


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


def main():
    args = parse_args()
    gemini_api_key, kakao_rest_api_key = load_api_keys()

    print(f"입력한 여행 날짜: {args.date}")
    print("API 키 설정 확인 완료")


if __name__ == "__main__":
    main()