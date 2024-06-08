from bs4 import BeautifulSoup as bs
from urllib.request import urlopen
from urllib.parse import urlencode

# 요청 URL과 파라미터 설정
base_url = "http://www.law.go.kr/DRF/lawSearch.do"
params = {
    "OC": "gogobattle",      # 사용자 ID
    "target": "prec",        # 서비스 대상
    "type": "XML",           # 출력 형태
    "query": "명예훼손",       # 검색할 키워드
    "display": 20,           # 검색된 결과 개수 (기본값 20, 최대값 100)
    "page": 1                # 검색 결과 페이지 (기본값 1)
}

# URL 인코딩된 파라미터 추가
url_with_params = f"{base_url}?{urlencode(params, safe='=')}"

# URL 열기 및 응답 읽기
response = urlopen(url_with_params).read()

# BeautifulSoup을 사용하여 XML 파싱
soup = bs(response, "xml")

# 결과 출력 (예: 사건명과 판결요지 출력)
cases = soup.find_all("prec")
for case in cases:
    case_name = case.find("사건명").get_text() if case.find("사건명") else "N/A"
    case_summary = case.find("판결요지").get_text() if case.find("판결요지") else "N/A"
    print(f"사건명: {case_name}")
    print(f"판결요지: {case_summary}")
    print("-" * 50)
