from flask import Flask, request, render_template, send_from_directory
import os
from werkzeug.utils import secure_filename
from extract_invoice_info import get_genai_client, load_file, extract_invoice_info

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)



@app.route('/', methods=['GET', 'POST'])
def index():
    error = None
    result = None
    filename = None
    if request.method == 'POST':
        if 'file' not in request.files:
            error = 'No file part'
        else:
            file = request.files['file']
            if file.filename == '':
                error = 'No selected file'
            else:
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                try:
                    client = get_genai_client()
                    file_bytes = load_file(file_path)
                    details = extract_invoice_info(file_bytes, client, file_path)
                    result = details.model_dump()  # Pass as dict, not JSON string
                except Exception as e:
                    error = str(e)
    return render_template("index.html", error=error, result=result, filename=filename)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=False, host="0.0.0.0")
