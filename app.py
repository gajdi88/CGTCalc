import pycharmpatch
from flask import Flask, request, render_template, redirect, url_for, g, flash
import pandas as pd
from ledger import Ledger
from csvloader import CSVLoader
import os
from cgt import cgt
import logging
from werkzeug.exceptions import HTTPException


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_ledger():
    if 'ledger' not in g:
        g.ledger = Ledger()
    return g.ledger

@app.before_request
def initialize_ledger():
    get_ledger()

# ledger = Ledger()  # Global state is dangerous
# add multiple routes: /upload, /, /cgt
@app.route('/')
@app.route('/calculate_cgt')
def index():
    ledger = get_ledger()
    transactions = ledger.transactions.to_html(classes='table table-striped')
    # only calculate cgt if route is calculate_cgt
    cgt_calculator = cgt(ledger)
    if request.path == '/calculate_cgt':
        cgt_calculator.calculate_yearly_cgt_liability()
    cgt_tables = cgt_calculator.calcs.to_html(classes='table table-striped')
    return render_template('index.html', tables=transactions, cgt_tables=cgt_tables)

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        ledger = get_ledger()
        if 'file' not in request.files:
            flash('No file selected')
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
    except Exception as e:
        logger.error(f"Error processing upload: {str(e)}", exc_info=True)
        flash('Error processing file')
        return redirect(request.url)

@app.errorhandler(Exception)
def handle_exception(e):
    if isinstance(e, HTTPException):
        return render_template('error.html', error=e), e.code
    
    # Log non-HTTP exceptions
    logger.error(f"Unhandled exception: {str(e)}", exc_info=True)
    return render_template('error.html', error="Internal Server Error"), 500

if __name__ == '__main__':
    app.run(debug=True)