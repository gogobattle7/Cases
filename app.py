from flask import Flask, request, redirect, url_for, send_from_directory, render_template
import os
from summary import extract_text_from_pdf, refine_text_with_form_gpt, save_text_to_pdf

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    return render_template('index.html')

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

        return send_from_directory(app.config['UPLOAD_FOLDER'], 'refined.pdf', as_attachment=True)
    return redirect(request.url)

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True)
