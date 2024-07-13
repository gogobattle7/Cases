import openai
import os
from dotenv import load_dotenv
from summary import extract_text_from_pdf

# 환경 변수 로드
load_dotenv()

# OpenAI API 키 설정
openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_pleading(extracted_text, plaintiffs, defendants, summarized_results, selected_charges):
    try:
        # 원고 리스트와 피고 리스트를 하나의 문자열로 결합
        # print(summarized_results)
        # print("분리")
        # print(selected_charges)
        
        plaintiffs_str = ', '.join(plaintiffs)
        defendants_str = ', '.join(defendants)

        # # 각 청구 원인에 대한 상세 작성
        # legal_reasons = ""
        # for charge in selected_charges:
        #     if charge in summarized_results:
        #         summaries = summarized_results[charge]
        #         for summary in summaries:
        #             response = openai.ChatCompletion.create(
        #                 model="gpt-4",
        #                 messages=[
        #                     {"role": "system", "content": "You are a legal assistant providing legal reasoning for a complaint."},
        #                     {"role": "user", "content": f"사실 관계: {summary}\n이 사실 관계와 관련된 법적 쟁점과 판례 법리를 설명해 주세요. 법적 근거와 판례 법리를 포함하여 이 사실 관계가 어떻게 해당 법조항에 적용되는지 설명해 주세요. 이를 하나의 자연스러운 문단으로 연결하여 작성해 주세요."}
        #                 ],
        #                 max_tokens=500,
        #                 n=1,
        #                 stop=None,
        #                 temperature=0.7
        #             )

        #             legal_reasoning = response.choices[0].message['content'].strip()
        #             legal_reasons += f"{charge}:\n{legal_reasoning}\n\n"

        # 소장 템플릿
        template = f"""
        원고: {plaintiffs_str}
        피고: {defendants_str}
        
        법적 쟁점:
        {selected_charges}
        법조문:
        
        관련 판례:

        청구 원인:
        
        이에 본 소를 제기합니다.
        
        이 양식을 지켜주세요
        """
        user_message_content = (
            "아래의 정보를 포함한 소장을 작성해 주세요. "
            f"소장의 양식은 {template}를 반드시 지켜주세요"
            f"사건의 내용은 {extracted_text} 입니다"
            "원고: 주소가 반드시 포함되어야 합니다.\n\n"
            "피고: 피고는 각 피고별로 번호를 매겨서 적어 주세요. 주소가 반드시 포함되어야 합니다.\n\n"
            "한 칸 띄우고 등 법적 쟁점을 굵은 글씨로 붙여 주세요.\n\n"            
            f"법적 쟁점에는 {selected_charges}에 있는 죄명만 사용하여 주세요"
            "절대로 다른 죄명은 사용하지 마세요"
            f"법조문에는 {selected_charges}에 있는 죄명과 죄명에 대한 설명을 작성해주세요"
            "청구 원인:\n\n"
            "모든 문장은 경어체를 사용하여 작성해 주세요. "
            "원고, 피고, 법적 쟁점, 법조문, 관련 판례의 번호 및 각 판례의 법리를 작성해 주세요. "
            "청구 원인: "
            f"{selected_charges} 에 있는 죄명만 사용하여 주세요."
            "절대로 다른 죄명은 사용하지 마세요"
            f"판례의 법리는{summarized_results} 를 사용하면 됩니다."
            "청구 원인은 1. 사실 관계 2. 원고의 주장 3. 주장에 대한 법적 근거 - (1) 법조문 (2) 판례의 법리 (3) (1)과 (2)를 적용하여 2.의 주장을 뒷받침 4. 피고의 예상되는 항변 및 반박 등을 포함하여 하나의 문단으로 작성해 주세요. "
            "1.2.3.4. 와 같이 분리하지말고 꼭 하나의 문단으로 작성해주세요"
            "관련 계약, 부동산이 있을 경우 그에 대한 설명 등을 포함해 주세요. "
            "정보는 논리적이고 설득력 있게 제시되어야 합니다. "
            "소장 template으로 주어진 형식을 따르고 각 항목별로 구분이 확실히 되게 해주세요"
            "법적 쟁점, 법조문, 관련 판례 부분도 정리해주세요"
            "소장을 작성한 이후에는 새로운 문단으로 시작하여 상담자(피고)가 취해야 할 조치들을 변호사의 입장에서 최대한 자세하게 번호를 붙여가며 조언해 주세요. "
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
        '명예훼손': {'2021다270654': '언론매체가 공공의 이익을 위해 사실을 보도하여 개인의 명예를 훼손한 경우, 해당 사실이 진실이며 행위자가 그것을 진실로 믿고 믿을 상당한 이유가 있다면 위법성이 없다. 이에 대한 입증의 책임은 언론매체에 있다. 언론의 자유와 명예보호 사이의 한계는 피해자가 공적 인물인지, 사적 인물인지, 표현이 공적인 관심사인지, 사적인 영역에 속하는 사안인지 등에 따라 다르다. 특히 공직자에 대한 감시와 비판은 국민의 권리이며, 이는 악의적이거나 경솔한 공격으로 상당성을 잃지 않는 한 제한되어서는 안 된다.\n\n인터넷신문이 국정원 관련 의혹을 보도한 사안에서, 신문사가 사실 확인을 위한 충분한 소명자료를 제 시하지 않았으므로 정정보도를 명하였다. 하지만 해당 사건은 공직자의 직무수행에 관한 공적 관심사로, 정보의 유출 방식에 대한 의혹이 계속되었고, 이에 대한 보도의 목적이 공공의 이익을 위한 것이었으므로, 신문사의 보도 행위에 위법성이 없다는 판단이 가능하다. 그러나 원심은 이를 인정하지 않고 손해배상청구를 인용한 것에 법리 오해가 있다는 판단을 내렸다.', '2022도699': "'정보통신망 이용촉진 및 정보보호 등에 관한 법 률 제70조 제1항'에 따라, 비방 목적으로 다른 사람의 명예를 훼손하는 행위는 범죄로 보며, 비방의 의도는 표현의 성격, 범위, 방법 등을 통해 판단된다. 비방의 목적이 공공의 이익을 위한 경우는 예외로 보며, 이를  판단할 때는 공개된 사실이 공공의 이익에 관한 것인지, 행위자의 의도, 피해자의 성격 등을 종합적으로 고려한다.\n\n해당 사례에서 피고인들이 운영한 'Bad Fathers'라는 사이트에서 양육비 미지급자의 신상 정보를 공개한 행위는 양육비 미지급 문제에 대한 공적 관심을 끌어 일정 부분 공익에 기여하였다 하더라도, 이러한 행위의 주된 목적이 개별 양육비채무자를 압박하는 것이었고, 신상 정보 공개의 과정에서 피해자의 권리를 침해하는 정도가 크다는 점에서 비방의 목적이 인정되었다. 따라서, 피고인들에 대한 명예훼손 혐의는 유죄로 판단되었다.", '2022다280283': '명예훼손은 사실을 공개함으로써 인격적 가치의 사회적 평가를 침해하는 행위를 말하며, 이는 명시적으로 사실을 표현하거나, 묵시적으로 사실을 포함하는 의견이나 논평을 표현할 때도 해당됩니다. 그러나 순수한 의견 표현 자체로는 명예훼손이 성립되지 않습니다. 명예훼손으로 손해배상을 청구할 때, 주장된 사실이 허위인 것을 증명하는 책임은 원고에게 있습니다. 그러나 피고가 그 사실의 목적이 공공의 이익을 위한 것이며, 그 사실이 진실이거나 진실로 믿을 만한 이유가 있다고 주장할 경우, 이를 증명하는  책임은 피고에게 있습니다. 일본 강제징용 피해자를 상징하는 조각가 부부의 발언은 사실의 표시가 아니라 의견의 표현이나 의혹 제기로 볼 수 있으며, 그 발언이 공공의 이익과 관련된 것으로 볼 때, 진실한 사실에 기 초한 것이 아니라 하더라도 그 내용이 진실이라고 믿을 만한 이유가 있었다면 명예훼손으로 보지 않을 수 있습니다.'}
    }

    pleading = generate_pleading(extracted_text, plaintiffs, defendants, summarized_results, selected_charges=["명예훼손"])
    print(pleading)
