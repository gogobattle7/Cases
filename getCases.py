import requests
from bs4 import BeautifulSoup
import re

def search_case(query, max_cases=3):
    base_url = "https://casesearch.dev/search"
    params = {
        'q': query,
        'not': '',
        '_term': '1',
        '_court': '',
        '_event': '',
        '_nodong': ''
    }

    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        results = soup.find_all('div', class_='div_case')

        case_numbers = []
        for result in results:
            title = result.find('td', style="font-size:20px;color:#4EC5EF;font-weight:bold")
            if title:
                title_text = title.text.strip()
                match = re.search(r'(\d{4}도\d+|\d{4}다\d+|\d{4}노\d+)', title_text)
                if match:
                    case_numbers.append(match.group(1))
                if len(case_numbers) >= max_cases:
                    break

        return case_numbers
    else:
        return []

def get_case_summary(case_number):
    base_url = "https://casesearch.dev/case/"
    url = base_url + case_number
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        case_summary_start = soup.find('span', string=lambda text: text and '판결요지' in text)
        
        if case_summary_start:
            summary_content = []
            for element in case_summary_start.next_siblings:
                if element.name == 'a' and 'titleIndex_anchor' in element.get('class', []):
                    break
                summary_content.append(str(element).strip())
            return ''.join(summary_content)[:20000]  # 최대 20000자까지 출력
        else:
            return "No case summary found."
    else:
        return "Failed to retrieve the page."

def search_and_return_summaries(query):
    case_numbers = search_case(query)
    summaries = []
    if case_numbers:
        for case_number in case_numbers:
            summary = get_case_summary(case_number)
            summaries.append((case_number, summary))
    return summaries
