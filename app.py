from flask import Flask, request, redirect, url_for, send_from_directory, render_template
import os
from summary import extract_text_from_pdf, refine_text_with_form_gpt, save_text_to_pdf, extract_charges
import subprocess

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'pdf'}

# 사용 가능한 죄명 리스트
available_charges = ["명예훼손", "모욕", "사기", "횡령"]

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    return render_template('index.html', available_charges=available_charges)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'pdf-file' not in request.files:
        return redirect(request.url)

    file = request.files['pdf-file']

    if file.filename == '':
        return redirect(request.url)

    if file and allowed_file(file.filename):
        filename = "uploaded.pdf"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # Step 2: PDF에서 텍스트 추출
        extracted_text = extract_text_from_pdf(file_path)

        # Step 3: 텍스트 수정
        refined_text = refine_text_with_form_gpt(extracted_text)

        # Step 4: 수정된 텍스트를 새로운 PDF로 저장
        output_pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], 'refined.pdf')
        save_text_to_pdf(refined_text, output_pdf_path)

        # Step 5: 죄명 추출
        charges = extract_charges(refined_text)

        return render_template('result.html', charges=charges, available_charges=available_charges, pdf_path='refined.pdf')
    return redirect(request.url)

@app.route('/precedent', methods=['POST'])
def get_precedent():
    # 선택된 체크박스 값을 가져옴
    selected_charges = request.form.getlist('charges[]')
    # 선택된 죄명들을 공백으로 구분된 문자열로 변환
    query = ' '.join(selected_charges)
    print(query)
    # getPrecedent.py 스크립트를 실행하여 결과를 가져옴
    result = subprocess.run(['python', 'getPrecedent.py', query], capture_output=True, text=True)

    return render_template('result.html', charges=selected_charges, available_charges=available_charges, pdf_path='refined.pdf', result=result.stdout)

@app.route('/uploads/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True)
