from flask import Flask, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import os
from utils.pdf import run_pdf_based_qa, run_pdf_based_analysis
import utils.db_conn as db_conn

app = Flask(__name__,  static_folder='static')
app.config['UPLOAD_FOLDER'] = 'data'  # Set the folder where PDF files will be stored
app.config['ALLOWED_EXTENSIONS'] = {'pdf'}  # Set the allowed file extensions for uploads


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


def delete_uploaded_files(filename):
    # Need to delete files that were already uploaded
    file_path = "data/" + filename
    try:
        os.remove(file_path)
    except OSError:
        print(f"Error deleting file: {file_path}")


@app.route('/upload_pdfs', methods=['POST'])
def upload_pdfs():
    if request.method == 'POST':
        if 'files[]' not in request.files:
            return jsonify({"error": "No files provided"}), 400

        files = request.files.getlist('files[]')
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            else:
                return jsonify({"error": f"Invalid file: {file.filename}"}), 400
        # Use run_pdf_based_qa if adding back the question bar
        if not db_conn.check_was_invoice_already_processed(filename):
            # Do check so we avoid double processing invoices
            run_pdf_based_analysis(filename)
        delete_uploaded_files(filename)
        res = db_conn.get_all_invoices()
        return jsonify({"answer": res.to_json(orient="records")})


@app.route('/_next/<path:path>')
def serve_next_assets(path):
    return send_from_directory('static/web/_next', path)


@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)


@app.route('/')
def index():
    return send_from_directory('static/web', 'index.html')


if __name__ == '__main__':
    db_conn.create_db()
    app.run(debug=True)
