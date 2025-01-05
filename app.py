from flask import Flask, request, render_template, redirect, url_for
import pandas as pd
from ledger import Ledger
from csvloader import CSVLoader
import os
from cgt import cgt

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

ledger = Ledger()
# add multiple routes: /upload, /, /cgt
@app.route('/')
@app.route('/calculate_cgt')
def index():
    transactions = ledger.transactions.to_html(classes='table table-striped')
    # only calculate cgt if route is calculate_cgt
    cgt_calculator = cgt(ledger)
    if request.path == '/calculate_cgt': cgt_calculator.calculate_yearly_cgt_liability("2023/2024")
    cgt_tables = cgt_calculator.calcs.to_html(classes='table table-striped')
    return render_template('index.html', tables=transactions, cgt_tables=cgt_tables)

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
        # return redirect(url_for('index'))
        return redirect('/')
    return redirect(request.url)

if __name__ == '__main__':
    app.run(debug=True)