import openai
import os
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# OpenAI API 키 설정
openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_pleading(extracted_text, plaintiffs, defendants, search_results):
    # 원고 리스트와 피고 리스트를 하나의 문자열로 결합
    plaintiffs_str = ', '.join(plaintiffs)
    defendants_str = ', '.join(defendants)

    # 청구 원인 부분을 요약된 판례 요지를 사용하여 작성
    legal_reasons = "\n".join([f"{charge}: {summary}" for charge, summaries in search_results.items() for summary in summaries.values()])

    # 소장 템플릿
    template = f"""
    소   장
    원고: {plaintiffs_str}
    피고: {defendants_str}

    사건 내용:
    {extracted_text}

    청구 원인:
    {legal_reasons}

    이에 본 소를 제기합니다.
    """

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a legal assistant helping to draft a legal complaint."},
            {"role": "user", "content": f"다음 내용을 바탕으로 원고의 입장에서 소장을 작성해줘:\n\n{template}"}
        ],
        max_tokens=1500,
        n=1,
        stop=None,
        temperature=0.7
    )

    pleading = response.choices[0].message['content'].strip()
    return pleading

# 테스트 코드
if __name__ == "__main__":
    extracted_text = """
    원고: 친구와 친구의 아내
    피고: 셀프 손가락욕을 한 동창
    죄명 및 설명:
    1. 명예훼손: 피고가 원고의 결혼식에서 손가락욕을 하여 원고와 원고의 아내에게 심리적인 고통을 주었습니다. 
    이로 인해 원고의 아내는 정신과 병원을 다니게 되었습니다. 이는 원고와 원고의 아내의 사회적 평판을 훼손한 
    것으로, 명예훼손죄가 성립될 수 있습니다.
    2. 개인정보 침해: 피고가 손가락욕 사진을 통해 원고의 결혼식을 침해한 것으로 볼 수 있습니다. 결혼식은 개인의 
    사생활을 보호받을 권리가 있으므로 이를 침해한 행위로 개인정보 침해죄가 성립될 수 있습니다.
    3. 폭언 및 협박: 원고의 아내가 피고에게 반말을 하며 욕설을 퍼붓는 등의 행위를 한 것으로 보입니다. 이는 피고의 
    정신적 안정을 해치는 행위로 폭언 및 협박죄가 성립될 수 있습니다. 사건을 잘 해결하기 위해서는 변호인과 상담하는 
    것이 좋을 것 같습니다. 변호인은 상황을 평가하고, 적절한 권리구제 방안을 제안할 수 있습니다.
    """
    plaintiffs = ["친구와 친구의 아내"]
    defendants = ["셀프 손가락욕을 한 동창"]
    search_results = {
        "명예훼손": {"case1": "피고가 원고의 결혼식에서 손가락욕을 하여 원고와 원고의 아내에게 심리적인 고통을 주었습니다."},
        "개인정보 침해": {"case2": "피고가 손가락욕 사진을 통해 원고의 결혼식을 침해한 것으로 볼 수 있습니다."},
        "폭언 및 협박": {"case3": "피고가 원고의 아내에게 반말을 하며 욕설을 퍼붓는 등의 행위를 한 것으로 보입니다."}
    }

    pleading = generate_pleading(extracted_text, plaintiffs, defendants, search_results)
    print(pleading)
