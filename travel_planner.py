import argparse
from datetime import datetime


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


def main():
    args = parse_args()
    print(f"입력한 여행 날짜: {args.date}")


if __name__ == "__main__":
    main()