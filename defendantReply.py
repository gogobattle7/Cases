import openai
import os
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# OpenAI API 키 설정
openai.api_key = os.getenv("OPENAI_API_KEY")

# AI를 통해 텍스트 요약
def makeDefendantReply(extracted_text, defendants, pleading,selected_charges):
    try:
        user_message_content = (
            f"사건 내용은{extracted_text} 입니다"
            f"사건의 피고는 {defendants} 입니다"
            f"소장의 내용은 {pleading} 입니다"
            f"{selected_charges}에 대해서만 반론하면 됩니다. 다른 죄명은 언급하지 말아주세요"
            "피고의 입장에서 소장에 대한 답변서를 작성해주세요"
        )

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a legal assistant helping to draft a legal complaint."},
                {"role": "user", "content": f"{user_message_content}"}
            ],
            max_tokens=3000,
            n=1,
            stop=None,
            temperature=0.7
        )

        pleading = response.choices[0].message['content'].strip()
        return pleading
    except Exception as e:
        print(f"Error generating pleading: {e}")
        return f"An error occurred: {e}"
