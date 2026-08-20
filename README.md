# 국내 여행지 추천 프로그램

사용자가 입력한 여행 날짜를 바탕으로 Gemini API가 국내 여행 지역을 추천하고, Kakao Local API로 해당 지역의 맛집을 검색한 뒤 최종 여행 리포트를 생성하는 CLI 기반 Python 프로그램입니다.

## 주요 기능

- `argparse`를 이용한 여행 날짜 입력
- `YYYY-MM-DD` 날짜 형식과 실제 날짜 유효성 검사
- Gemini API를 이용한 추천 지역·날씨·행사 정보 생성
- Gemini 응답을 JSON으로 구조화하여 다음 API 입력으로 활용
- Kakao Local API를 이용한 추천 지역 맛집 5곳 검색
- Gemini API를 이용한 최종 Markdown 여행 리포트 생성
- 원본 JSON과 최종 Markdown 파일 저장
- API 인증·네트워크·검색 결과 없음·JSON 파싱 오류 처리
- `.env`를 이용한 API 키 관리
- 같은 날짜의 저장된 결과가 있으면 API 호출을 생략하는 결과 캐싱

## 프로그램 처리 흐름

1. 사용자가 `-date` 옵션으로 여행 날짜를 입력합니다.
2. Gemini가 추천 지역, 일반적인 날씨, 행사 후보, 추천 이유를 JSON으로 생성합니다.
3. JSON의 `recommended_city` 값을 Kakao Local API의 검색어로 사용합니다.
4. Kakao Local API가 해당 지역의 맛집 5곳을 검색합니다.
5. Gemini가 추천 정보와 맛집 목록을 종합하여 Markdown 리포트를 생성합니다.
6. 결과를 `results/` 폴더에 JSON과 Markdown으로 저장합니다.

## 개발 환경

- Python 3.10 이상
- Python 3.14.7에서 개발 및 테스트
- Gemini API
- Kakao Local REST API

## 설치 방법

### 1. 저장소 복제

```bash
git clone https://github.com/codyssey-seungmin/A1-2.git
cd A1-2
```

### 2. 가상환경 생성

```bash
python -m venv .venv
```

Windows PowerShell에서 가상환경을 활성화합니다.

```powershell
.\.venv\Scripts\Activate.ps1
```

PowerShell 실행 정책으로 활성화가 차단되면 현재 터미널에서만 임시 허용합니다.

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

macOS 또는 Linux에서는 다음 명령을 사용합니다.

```bash
source .venv/bin/activate
```

### 3. 라이브러리 설치

```bash
python -m pip install -r requirements.txt
```

## API 키 설정

프로젝트 최상위에 `.env` 파일을 만들고 다음 환경변수를 설정합니다.

```env
GEMINI_API_KEY=YOUR_GEMINI_API_KEY
KAKAO_REST_API_KEY=YOUR_KAKAO_REST_API_KEY
```

- Gemini API 키는 Google AI Studio에서 발급받을 수 있습니다.
- Kakao REST API 키는 Kakao Developers의 애플리케이션 관리 화면에서 확인할 수 있습니다.
- Kakao Local API를 사용하려면 해당 애플리케이션의 `제품 설정 → 카카오맵 → 사용 설정`을 활성화해야 합니다.

## API 키 보안 주의사항

- 실제 API 키를 Python 코드에 직접 작성하지 않습니다.
- 실제 키가 들어 있는 `.env`는 GitHub에 올리지 않습니다.
- `.env.example`에는 환경변수 이름과 예시값만 작성합니다.
- 터미널 출력, README, 결과 JSON과 Markdown에도 실제 키를 포함하지 않습니다.
- 키가 공개되면 즉시 기존 키를 폐기하고 새 키를 발급받아야 합니다.

`.env`와 가상환경 등은 `.gitignore`로 Git 추적에서 제외됩니다.

## 실행 방법

```bash
python travel_planner.py -date "2026-09-15"
```

다음처럼 긴 옵션도 사용할 수 있습니다.

```bash
python travel_planner.py --date "2026-09-15"
```

## 정상 실행 예시

```text
[1/3] 1차 추천 생성 중(Gemini)...
  - recommended_city: "강원도 강릉"
[2/3] 맛집 검색 중(Kakao)...
  - 맛집 5곳 검색 완료
[3/3] 최종 리포트 생성 중(Gemini)...
  - 리포트 생성 완료

완료! 원본 데이터: results\2026-09-15_travel_data.json
완료! 여행 리포트: results\2026-09-15_travel_plan.md
```

## 결과물 확인

프로그램을 실행하면 `results/` 폴더에 다음 파일이 생성됩니다.

```text
results/
├── 2026-09-15_travel_data.json
└── 2026-09-15_travel_plan.md
```

### 원본 JSON

원본 JSON에는 다음 데이터가 포함됩니다.

- 입력 날짜
- Gemini 1차 추천 결과
- Kakao 맛집 검색 결과
- 오류 요약 `errors`

### Markdown 리포트

최종 Markdown 리포트에는 다음 항목이 포함됩니다.

- 추천 지역
- 추천 이유
- 날씨 요약
- 행사·축제
- 맛집 추천
- 오전·오후·저녁 1일 일정
- 오류 요약

## 결과 캐싱

프로그램을 실행하면 날짜별 JSON과 Markdown 결과가 `results/` 폴더에 저장됩니다.

같은 날짜로 다시 실행할 경우 저장된 결과 파일을 캐시로 사용하며, Gemini API와 Kakao Local API를 다시 호출하지 않습니다. 이를 통해 API 사용량과 실행 시간을 줄일 수 있습니다.

```bash
python travel_planner.py --date "2026-08-24"

## 오류 처리

- API 키가 없으면 설정 방법을 안내하고 즉시 종료합니다.
- 잘못된 날짜를 입력하면 사용법과 오류 메시지를 출력합니다.
- Gemini JSON 파싱에 실패하면 최대 한 번만 재요청합니다.
- Kakao API 인증·네트워크·쿼터 오류가 발생하면 맛집을 `데이터 없음`으로 처리합니다.
- Kakao 검색 결과가 0건이면 오류 목록에 `EMPTY_RESULT`를 기록합니다.
- Kakao API가 실패해도 최종 여행 리포트 생성은 계속 진행합니다.

## 사용 API와 HTTP 메서드

- Gemini API: 생성 요청을 서버에 전달하므로 `POST` 방식으로 처리됩니다.
- Kakao Local API: 장소 데이터를 조회하므로 `GET` 방식으로 처리됩니다.

`GET`은 주로 서버의 데이터를 조회할 때 사용하고, `POST`는 데이터를 서버에 전달해 새로운 처리나 생성을 요청할 때 사용합니다.

## 프로젝트 구조

```text
A1-2/
├── results/
│   ├── 2026-09-15_travel_data.json
│   └── 2026-09-15_travel_plan.md
├── .env
├── .env.example
├── .gitignore
├── README.md
├── requirements.txt
└── travel_planner.py
```

실제 API 키가 포함된 `.env`와 가상환경 `.venv/`는 GitHub 저장소에 포함되지 않습니다.