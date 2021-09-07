from typing import (Deque, Dict, FrozenSet, List, Optional, Sequence, Set, Tuple, Union)
from convert_excel import ConvertExcel
import aiofiles
import requests
from flask import Flask, request, jsonify, send_from_directory
import os
import yaml
from db_helper import DBHelper
from training_dataset import TrainingDataset
from process_columns import ProcessColumns
import json
from types import SimpleNamespace
import icecream as ic

ic = ic.IceCreamDebugger()
#ic.disable()

CACHE = "cache"
BUFFER = 50_000

if not os.path.isdir(CACHE):
    os.mkdir(CACHE)

Vector = List[int]

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = CACHE

conv = ConvertExcel()
db = DBHelper()
training = TrainingDataset()
process_columns = ProcessColumns()

@app.route("/compare/columns", methods=['POST'])
# TODO make it async
def compare():
    if request.method == 'POST':
        form = request.form
        texts = json.loads(form['texts'])
        target_columns, target_targets, architect_id, subset_id, header_rows = process_columns.compare(texts)
        return {"target_columns": target_columns,
                "target_targets": target_targets,
                "architect_id": architect_id,
                "subset_id": subset_id,
                "header_rows": header_rows}

@app.route("/save/columns", methods=['POST'])
# TODO make it async
def save_columns():
    if request.method == 'POST':
        form = request.form
        # texts: column headers
        texts = json.loads(form['texts'])
        columns = json.loads(form['columns'])
        targets = json.loads(form['targets'])
        header_row = json.loads(form['header_row'])
        ic(texts, columns, targets)
        architect_id = form['architect_id']
        result = db.insert_headers(texts, columns, targets, architect_id, header_row)
        return return_response(result)  # subset_id

@app.route("/save/architect", methods=['POST'])
# TODO make it async
def save_architect():
    if request.method == 'POST':
        form = request.form
        name = form['name']
        result = db.insert_architect(name)
        return return_response(result)

@app.route("/save/category", methods=['POST'])
# TODO make it async
def save_category():
    if request.method == 'POST':
        form = request.form
        name = form['name']
        ordinal = form['ordinal']
        result = db.insert_sentence_label(name, ordinal)
        return return_response(result)

@app.route("/save/tokenlabel", methods=['POST'])
# TODO make it async
def save_token_label():
    if request.method == 'POST':
        form = request.form
        name = form['name']
        category_id = form['category_id']
        result = db.insert_token_label(name, category_id)
        return return_response(result)

@app.route("/save/trainingdata", methods=['POST'])
# TODO make it async
def save_training_data():
    ic("save training data")
    if request.method == 'POST':
        form = request.form
        # integer
        content_column = json.loads(form['content_column'])
        source_rows = json.loads(form['source_rows'])
        target_categories = json.loads(form['target_categories'])
        token_labels = json.loads(form['token_labels'])
        f = request.files['file']
        filename = f.filename
        cwd = os.getcwd()
        file_path = os.path.join(cwd, CACHE, filename)
        f.save(file_path)
        result = training.save(content_column, source_rows, target_categories, token_labels, file_path)
        return return_response(result)

    return "invalid method"

@app.route("/convert", methods=['POST'])
# TODO make it async
def convert():
    if request.method == 'POST':
        file_path, source_cols, source_rows, target_categories, target_cols = get_convert_data()

        directory, file_name = conv.process(source_rows, source_cols, target_categories, target_cols, file_path)
        return send_from_directory(directory, file_name, as_attachment=True)

    return "invalid method"


@app.route("/convert/more/sheets", methods=['POST'])
# TODO make it async
def convert_more_sheets():
    if request.method == 'POST':
        file_path, source_cols, source_rows, target_categories, target_cols = get_convert_data()

        directory, file_name = conv.process_more_sheets_and_save(source_rows, source_cols, target_categories, target_cols, file_path)
        return send_from_directory(directory, file_name, as_attachment=True)

    return "invalid method"

@app.route("/convert/more/files", methods=['POST'])
# TODO make it async
def convert_more_files():
    if request.method == 'POST':
        form = request.form
        source_rows = json.loads(form['source_rows'])
        source_cols = json.loads(form['source_cols'])
        target_categories = json.loads(form['target_categories'])
        target_cols = json.loads(form['target_cols'])
        cached_files = []
        uploaded_files = request.files.getlist("file[]")
        print(uploaded_files)
        for file in uploaded_files:
            filename = file.filename
            cwd = os.getcwd()
            file_path = os.path.join(cwd, CACHE, filename)
            cached_files.append(file_path)
            file.save(file_path)
        directory, file_name = conv.process_more_files(source_rows, source_cols, target_categories, target_cols, cached_files)
        return send_from_directory(directory, file_name, as_attachment=True)
    return "invalid method"

@app.route("/convert/mi", methods=['POST'])
# TODO make it async
def convert_mi():
    if request.method == 'POST':
        form = request.form
        content_col = json.loads(form['content_col'])
        source_cols = json.loads(form['source_cols'])
        target_cols = json.loads(form['target_cols'])
        no_category_id = json.loads(form['no_category_id'])
        f = request.files['file']
        filename = f.filename
        cwd = os.getcwd()
        file_path = os.path.join(cwd, CACHE, filename)
        f.save(file_path)

        directory, file_name = conv.process_mi(content_col, source_cols, target_cols, file_path, no_category_id)
        return send_from_directory(directory, file_name, as_attachment=True)

    return "invalid method"

@app.route("/predict", methods=['POST'])
# TODO make it async
def predict_more_row():
    if request.method == 'POST':
        form = request.form
        content_col = json.loads(form['content_col'])
        source_rows = json.loads(form['source_rows'])
        no_category_id = json.loads(form['no_category_id'])
        f = request.files['file']
        filename = f.filename
        cwd = os.getcwd()
        file_path = os.path.join(cwd, CACHE, filename)
        f.save(file_path)

        target_categories = conv.process_more_row(
            content_col, source_rows, file_path, no_category_id)

        return target_categories
    return "invalid method"

@app.route("/start/training", methods=['GET'])
# TODO make it async
def start_training():
    if request.method == 'GET':
        from hubert_finetune import HubertFinetune
        model = HubertFinetune()
        model.train()
        #model = None
        return return_response(True)

def get_convert_data():
    form = request.form
    source_rows = json.loads(form['source_rows'])
    source_cols = json.loads(form['source_cols'])
    target_categories = json.loads(form['target_categories'])
    target_cols = json.loads(form['target_cols'])
    f = request.files['file']
    filename = f.filename
    cwd = os.getcwd()
    file_path = os.path.join(cwd, CACHE, filename)
    f.save(file_path)
    return file_path, source_cols, source_rows, target_categories, target_cols

def return_response(result):
    if result:
        return result
    else:
        return "Database error!"

if __name__ == "__main__":
    app.run(threaded=True, port=5000)