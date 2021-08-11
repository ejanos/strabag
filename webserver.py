from typing import (Deque, Dict, FrozenSet, List, Optional, Sequence, Set, Tuple, Union)
from convert_excel import ConvertExcel
import os
import aiofiles
import requests
from flask import Flask, request, jsonify
import os
import yaml
from db_helper import DBHelper
from training_dataset import TrainingDataset
from process_columns import ProcessColumns

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

def convert_int_list(txt):
    result = []
    if txt:
        txt_split = txt.split(",")
    else:
        return None
    for token in txt_split:
        result.append(int(token))
    return result

def convert_string_list(txt):
    return txt.replace(" ", "").split(',')

@app.route("/compare/columns", methods=['POST'])
# TODO make it async
def compare():
    if request.method == 'POST':
        form = request.form
        texts = convert_string_list(form['texts'])
        target_columns, target_targets, user_id = process_columns.compare(texts)
        return {"target_columns": target_columns,
                "target_targets": target_targets,
                "user_id": user_id}

@app.route("/save/columns", methods=['POST'])
# TODO make it async
def save_columns():
    if request.method == 'POST':
        form = request.form
        texts = convert_string_list(form['texts'])
        columns = convert_string_list(form['columns'])
        targets = convert_string_list(form['targets'])
        user_id = form['user_id']
        db.insert_columns(texts, columns, targets, user_id)
        return "ok"

@app.route("/save/user", methods=['POST'])
# TODO make it async
def save_user():
    if request.method == 'POST':
        form = request.form
        name = form['name']
        db.insert_user(name)
        return "ok"

@app.route("/save/category", methods=['POST'])
# TODO make it async
def save_category():
    if request.method == 'POST':
        form = request.form
        name = form['name']
        ordinal = form['ordinal']
        db.insert_sentence_label(name, ordinal)
        return "ok"

@app.route("/save/tokenlabel", methods=['POST'])
# TODO make it async
def save_token_label():
    if request.method == 'POST':
        form = request.form
        name = form['name']
        category_id = form['category_id']
        db.insert_token_label(name, category_id)
        return "ok"


@app.route("/save/traindata", methods=['POST'])
# TODO make it async
def save_train_data():
    if request.method == 'POST':
        form = request.form
        source_rows = convert_int_list(form['source_rows'])
        source_cols = convert_int_list(form['source_cols'])
        target_categories = convert_string_list(form['target_categories'])
        target_cols = convert_int_list(form['target_cols'])
        f = request.files['file']
        filename = f.filename
        cwd = os.getcwd()
        file_path = os.path.join(cwd, CACHE, filename)
        f.save(file_path)

        training.save(source_rows, source_cols, target_categories, target_cols, file_path)
        return "ok"

    return "invalid method"

@app.route("/convert", methods=['POST'])
# TODO make it async
def convert():
    if request.method == 'POST':
        form = request.form
        source_rows = convert_int_list(form['source_rows'])
        source_cols = convert_int_list(form['source_cols'])
        target_categories = convert_string_list(form['target_categories'])
        target_cols = convert_int_list(form['target_cols'])
        f = request.files['file']
        filename = f.filename
        cwd = os.getcwd()
        file_path = os.path.join(cwd, CACHE, filename)
        f.save(file_path)

        conv.process(source_rows, source_cols, target_categories, target_cols, file_path)
        return "ok"

    return "invalid method"

if __name__ == "__main__":
    app.run(threaded=True, port=5000)