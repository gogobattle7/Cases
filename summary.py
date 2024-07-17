import openai
import pdfplumber
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from dotenv import load_dotenv
import os
import re

# 환경 변수 로드
load_dotenv()

# OpenAI API 키 설정
openai.api_key = os.getenv("OPENAI_API_KEY")

# PDF에서 텍스트 추출
def extract_text_from_pdf(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        full_text = []
        for page in pdf.pages:
            text = page.extract_text()
            full_text.append(text)
    return "\n".join(full_text)

# AI를 통해 텍스트 수정 (폼 형식 유지)
def refine_text_with_form_gpt(transcript_text):
    formatted_text = f"내용:\n{transcript_text}"
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"다음 내용에서 원고와 피고를 분리하고, 법적 쟁점이 성립할 수 있는 죄명과 함께 상세하게 정리해주세요. (참고로 형사재판에서는 검사vs피고인 이고 민사재판에서는 원고vs 피고입니다. 그리고 죄명:설명 이런식으로 정리해주세요) :\n\n{formatted_text}"}
        ],
        max_tokens=1500,
        n=1,
        stop=None,
        temperature=0.7
    )
    return response.choices[0].message['content'].strip()

# 죄명 추출 함수
def extract_charges(refined_text):
    charges = re.findall(r'\d+\.\s(.*?):', refined_text)
    return charges


# 원고와 피고 추출 함수
def extract_plaintiffs_defendants(refined_text):
    plaintiffs = re.findall(r'원고:\s*(.*?)\s*피고:', refined_text, re.DOTALL)
    defendants = re.findall(r'피고:\s*(.*?)(?:\n|$)', refined_text, re.DOTALL)

    return plaintiffs, defendants


# 수정된 텍스트를 PDF로 저장
def save_text_to_pdf(text, output_path):
    pdfmetrics.registerFont(TTFont("맑은고딕", "malgun.ttf"))
    pdf = canvas.Canvas(output_path)
    pdf.setFont("맑은고딕", 12)
    
    margin = 40
    width, height = pdf._pagesize
    max_width = width - 2 * margin
    y_position = height - margin
    
    lines = text.split('\n')
    for line in lines:
        while pdf.stringWidth(line) > max_width:
            split_index = 0
            for i in range(len(line)):
                if pdf.stringWidth(line[:i]) > max_width:
                    split_index = i
                    break
            pdf.drawString(margin, y_position, line[:split_index])
            line = line[split_index:]
            y_position -= 14
            if y_position < margin:
                pdf.showPage()
                pdf.setFont("맑은고딕", 12)
                y_position = height - margin
        pdf.drawString(margin, y_position, line)
        y_position -= 14
        if y_position < margin:
            pdf.showPage()
            pdf.setFont("맑은고딕", 12)
            y_position = height - margin

    pdf.save()
