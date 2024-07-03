import openai
import os
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# OpenAI API 키 설정
openai.api_key = os.getenv("OPENAI_API_KEY")

# AI를 통해 텍스트 요약
def summarize_case_details(case_details):
    # 각 판례 요지를 요약하여 반환
    summaries = {}
    for case_number, summary in case_details:
        formatted_text = f"내용:\n{summary}"
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": f"다음 내용의 판례 요지를 법리 위주로 최대한 간결하게 요약만 해주세요:\n\n{formatted_text}"}
            ],
            max_tokens=1500,
            n=1,
            stop=None,
            temperature=0.7
        )
        summarized_text = response.choices[0].message['content'].strip()
        summaries[case_number] = summarized_text
    return summaries
