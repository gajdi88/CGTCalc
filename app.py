from flask import Flask, request, render_template, redirect, url_for
import pandas as pd
from ledger import Ledger
from csvloader import CSVLoader
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

ledger = Ledger()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
    if file:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)
        csv_loader = CSVLoader(ledger)
        csv_loader.load_csv(file_path, 'ii')
        return redirect(url_for('show_ledger'))
    return redirect(request.url)

@app.route('/ledger')
def show_ledger():
    transactions = ledger.transactions.to_html(classes='table table-striped')
    return render_template('ledger.html', tables=[transactions])

if __name__ == '__main__':
    app.run(debug=True)