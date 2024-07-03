import openai
import os
from dotenv import load_dotenv
from summary import extract_text_from_pdf

# 환경 변수 로드
load_dotenv()

# OpenAI API 키 설정
openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_pleading(extracted_text, plaintiffs, defendants, summarized_results):
    try:
        # 원고 리스트와 피고 리스트를 하나의 문자열로 결합
        plaintiffs_str = ', '.join(plaintiffs)
        defendants_str = ', '.join(defendants)

        # 청구 원인 부분을 요약된 판례 요지를 사용하여 작성
        legal_reasons = "\n".join([f"{charge}: {summary}" for charge, summaries in summarized_results.items() for summary in summaries])
        
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

        user_message_content = (
            "제공된 문서의 내용을 분석하여 아래의 정보를 포함한 소장을 작성해 주세요. "
            "소장은 다음과 같은 세부 사항을 포함해야 합니다. 모든 문장은 경어체를 써서 작성해 주세요. "
            "청구 취지의 각 번호별로 해당하는 청구원인을 적어서 작성해 주세요. 예상되는 항변 및 반박에서 "
            "각 피고별로 번호를 매겨서 항변을 해주세요. 목차의 번호를 정확하게 매겨서 작성해 주세요.:\n\n"
            "제공된 문서의 정보를 사용하여 다음 섹션을 포함한 소장을 작성해 주세요:\n\n"
            "원고: 주소가 반드시 포함되어야 합니다.\n\n"
            "피고: 피고는 각 피고별로 번호를 매겨서 적어 주세요. 주소가 반드시 포함되어야 합니다.\n\n"
            "한 칸 띄우고 등 청구의 소를 굵은 글씨로 붙여 주세요.\n\n"
            "청구 취지:\n\n"
            "각 피고에 대해 원고가 청구하는 구체적인 구제 내용을 작성해 주세요.\n"
            "문서 내용에 따라 손해배상, 재산 회복, 기타 구제 요구를 포함해 주세요.\n"
            "항목 중에 소송비용은 피고들이 부담한다. 를 꼭 넣어 주세요.\n"
            "항목 중에 가집행할 수 있는 것만 가집행할 수 있다고 넣어주세요.\n"
            "마지막 부분에 마지막 항목에서 한 칸 띄우고\n"
            "라는 판결을 구합니다.\n"
            "라는 문구를 꼭 넣어주세요.\n\n"
            "청구 원인:\n\n"
            "모든 문장은 경어체를 사용하여 작성해 주세요.\n"
            "피고별로 사실 관계, 법적 근거, 예상되는 항변 및 이러한 항변에 대한 반박의 순서대로 항목에 번호를 "
            "붙여서 작성해 주고 이 때 반박 논리를 제공하여 원고의 입장을 강화해 주세요.\n"
            "각 피고에 대한 원고의 청구를 뒷받침하는 사실 관계를 상세히 기술해 주세요.\n"
            "관련 계약, 부동산 설명 등을 포함해 주세요.\n"
            "각 청구에 대해 원고의 요구를 뒷받침하는 법적 근거를 명시해 주세요.\n"
            "이 외에도 원고의 입장을 뒷받침하는 관련 법률이나 규정을 참조해 주세요.\n"
            "각 피고에 대한 각 청구의 마지막 항목으로 소결 항목을 번호를 붙여서 넣어 주세요.\n\n"
            "소장은 잘 구성되고 명확하게 작성되어야 하며, 법원에 제출하기에 적합한 형식을 따라야 합니다. "
            "정보는 논리적이고 설득력 있게 제시되어야 합니다.\n\n"
            "참고 문서 형식은 형식만 참고하고 내용은 소장에 언급하지 말아주세요 "
        )

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a legal assistant helping to draft a legal complaint."},
                {"role": "user", "content": f"{user_message_content}\n\n{template}"}
            ],
            max_tokens=1500,
            n=1,
            stop=None,
            temperature=0.7
        )

        pleading = response.choices[0].message['content'].strip()
        return pleading
    except Exception as e:
        print(f"Error generating pleading: {e}")
        return f"An error occurred: {e}"

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
    summarized_results = {
        "명예훼손": ["피고가 원고의 결혼식에서 손가락욕을 하여 원고와 원고의 아내에게 심리적인 고통을 주었습니다."],
        "개인정보 침해": ["피고가 손가락욕 사진을 통해 원고의 결혼식을 침해한 것으로 볼 수 있습니다."],
        "폭언 및 협박": ["피고가 원고의 아내에게 반말을 하며 욕설을 퍼붓는 등의 행위를 한 것으로 보입니다."]
    }

    pleading = generate_pleading(extracted_text, plaintiffs, defendants, summarized_results)
    print(pleading)