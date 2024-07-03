from flask import Flask, request, redirect, url_for, send_from_directory, render_template
import os
from summary import extract_text_from_pdf, refine_text_with_form_gpt, save_text_to_pdf, extract_charges, extract_plaintiffs_defendants
import caseSearch
import gptlaw
from plaintiffs_pleading import generate_pleading

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'pdf'}
app.config['REFERENCE_FOLDER'] = 'references'

# 사용 가능한 죄명 리스트
available_charges = ["명예훼손", "모욕", "사기", "횡령"]

# 검색 결과를 저장할 전역 변수
search_results = {}
summarized_results = {}
case_details = {}
pleading=""


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
        plaintiffs, defendants = extract_plaintiffs_defendants(refined_text)
        charges = extract_charges(refined_text)

        print(plaintiffs)
        print(defendants)
        print(charges)
        
        global case_details
        case_details = {
            "plaintiffs": plaintiffs,
            "defendants": defendants,
            "charges": charges,
            "extracted_text": refined_text
        }

        return render_template('result.html', charges=charges, available_charges=available_charges, pdf_path='refined.pdf')
    return redirect(request.url)

@app.route('/precedent', methods=['POST'])
def precedent():
    selected_charges = request.form.getlist('charges[]')
    global search_results, summarized_results
    search_results = {charge: caseSearch.search_and_return_summaries(charge) for charge in selected_charges}
    
    summarized_results = {}
    for charge, details in search_results.items():
        summarized_results[charge] = gptlaw.summarize_case_details(details)
    return render_template('stored_results.html', results=summarized_results)

@app.route('/stored-results')
def stored_results():
    return render_template('stored_results.html', results=search_results)

@app.route('/uploads/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/pleading')
def pleading():
    global case_details, summarized_results, pleading
    extracted_text = case_details["extracted_text"]
    plaintiffs = case_details["plaintiffs"]
    defendants = case_details["defendants"]

    pleading = generate_pleading(extracted_text, plaintiffs, defendants, summarized_results)
    
    return render_template('pleading.html', pleading=pleading)



@app.route('/download-pleading-pdf')
def download_pleading_pdf():
    global case_details, summarized_results, pleading
    extracted_text = case_details["extracted_text"]
    plaintiffs = case_details["plaintiffs"]
    defendants = case_details["defendants"]

    full_text = f"Extracted Text:\n{extracted_text}\n\nPlaintiffs:\n{plaintiffs}\n\nDefendants:\n{defendants}\n\nSummarized Results:\n{summarized_results}\n\nPleading:\n{pleading}"

    output_pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], 'pleading.pdf')

    save_text_to_pdf(full_text, output_pdf_path)
    return send_from_directory(app.config['UPLOAD_FOLDER'], 'pleading.pdf')

@app.route('/defendant-response')
def defendant_response():
    # 피고의 답변서 생성 로직을 여기에 추가합니다.
    # 예: 답변서를 생성하고 사용자에게 보여주거나 다운로드할 수 있게 함
    return "피고의 답변서 내용이 여기에 표시됩니다."

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['REFERENCE_FOLDER'], exist_ok=True)
    app.run(debug=True)
