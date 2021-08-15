from typing import (Deque, Dict, FrozenSet, List, Optional, Sequence, Set, Tuple, Union)
from convert_excel import ConvertExcel
import aiofiles
import requests
from flask import Flask, request, jsonify
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
        target_columns, target_targets, user_id, subset_id = process_columns.compare(texts)
        return {"target_columns": target_columns,
                "target_targets": target_targets,
                "user_id": user_id,
                "subset_id": subset_id}

@app.route("/save/columns", methods=['POST'])
# TODO make it async
def save_columns():
    if request.method == 'POST':
        form = request.form
        # texts: column headers
        texts = json.loads(form['texts'])
        columns = json.loads(form['columns'])
        targets = json.loads(form['targets'])
        ic(texts, columns, targets)
        user_id = form['user_id']
        result = db.insert_headers(texts, columns, targets, user_id)
        return return_response(result)  # subset_id

@app.route("/save/user", methods=['POST'])
# TODO make it async
def save_user():
    if request.method == 'POST':
        form = request.form
        name = form['name']
        result = db.insert_user(name)
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
        source_rows = json.loads(form['source_rows'])
        source_cols = json.loads(form['source_cols'])
        target_categories = json.loads(form['target_categories'])
        target_cols = json.loads(form['target_cols'])
        token_labels = json.loads(form['token_labels'])
        f = request.files['file']
        filename = f.filename
        cwd = os.getcwd()
        file_path = os.path.join(cwd, CACHE, filename)
        f.save(file_path)
        result = training.save(source_rows, source_cols, target_categories, target_cols, token_labels, file_path)
        return return_response(result)

    return "invalid method"

@app.route("/convert", methods=['POST'])
# TODO make it async
def convert():
    if request.method == 'POST':
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

        conv.process(source_rows, source_cols, target_categories, target_cols, file_path)
        return "ok"

    return "invalid method"

def return_response(result):
    if result:
        return "ok"
    else:
        return "Database error!"

if __name__ == "__main__":
    app.run(threaded=True, port=5000)