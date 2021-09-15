from typing import (Deque, Dict, FrozenSet, List, Optional, Sequence, Set, Tuple, Union)

import flask

from convert_excel import ConvertExcel
import aiofiles
import requests
from flask import Flask, request, jsonify, send_from_directory,  make_response, stream_with_context
import datetime as dt
import os
import yaml
from db_helper import DBHelper
from training_dataset import TrainingDataset
from process_columns import ProcessColumns
import json
from types import SimpleNamespace
import icecream as ic
from custom_json_encoder import CustomJSONEncoder

ic = ic.IceCreamDebugger()
#ic.disable()

CACHE = "cache"
BUFFER = 50_000

if not os.path.isdir(CACHE):
    os.mkdir(CACHE)

Vector = List[int]

app = Flask(__name__)
app.json_encoder = CustomJSONEncoder
app.config['UPLOAD_FOLDER'] = CACHE

conv = ConvertExcel()
training = TrainingDataset()
process_columns = ProcessColumns()

@app.route("/compare/columns", methods=['POST'])
# TODO make it async
def compare():
    if request.method == 'POST':
        form = request.form
        texts = json.loads(form['texts'])
        target_columns, target_targets, architect_id, subset_id, header_rows = process_columns.compare(texts)
        return jsonify({"target_columns": target_columns,
                "target_targets": target_targets,
                "architect_id": architect_id,
                "subset_id": subset_id,
                "header_rows": header_rows})

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
        with DBHelper() as db:
            result = db.insert_headers(texts, columns, targets, architect_id, header_row)
        return return_response(result)  # subset_id

    #delete_headers_by_architect_subset_id

@app.route("/delete/columns", methods=['DELETE'])
# TODO make it async
def delete_columns():
    if request.method == 'POST':
        form = request.form
        architect_id = json.loads(form['architect_id'])
        subset_id = json.loads(form['subset_id'])
        with DBHelper() as db:
            result = db.delete_headers_by_architect_subset_id(architect_id, subset_id)
        return return_response(result)  # subset_id

@app.route("/save/architect", methods=['POST'])
# TODO make it async
def save_architect():
    if request.method == 'POST':
        form = request.form
        name = form['name']
        with DBHelper() as db:
            result = db.insert_architect(name)
        return return_response(result)

@app.route("/update/architect", methods=['POST'])
# TODO make it async
def update_architect():
    if request.method == 'POST':
        form = request.form
        id = form['architect_id']
        name = form['name']
        active = form['active']
        with DBHelper() as db:
            result = db.update_architect(id, name, active)
        return return_response(result)


@app.route("/read/all/architect", methods=['GET'])
# TODO make it async
def get_all_architect():
    if request.method == 'GET':
        with DBHelper() as db:
            architects = db.get_all_architect()
        result = []
        for row in architects:
             result.append({
                "architect_id": row[0],
                "name": row[1],
                "created_date": row[2],
                "modified_date": row[3],
                "active": row[4]})
        return return_response(result)

@app.route("/read/architect", methods=['GET'])
# TODO make it async
def get_architect():
    if request.method == 'GET':
        architect_id = request.args.get('id')
        with DBHelper() as db:
            architect = db.get_architect_by_id(architect_id)
        result = {
                "architect_id": architect[0],
                "name": architect[1],
                "created_date": architect[2],
                "modified_date": architect[3],
                "active": architect[4]}
        return return_response(result)

@app.route("/read/all/project", methods=['GET'])
# TODO make it async
def get_projects():
    if request.method == 'GET':
        user_id = request.args.get('user_id')
        with DBHelper() as db:
            rows = db.get_projects(user_id)
        result = []
        for row in rows:
            result.append({
                "project_id": row[0],
                "user_id": row[1],
                "architect_id": row[2],
                "project_name":  row[3],
                "created_date": row[4],
                "modified_date": row[5],
                "active": row[6],
            "ColumnRate": 15.1,
            "CategoryRate": 17.5})
        return return_response(result)

@app.route("/add/project", methods=['POST'])
# TODO make it async
def add_project():
    if request.method == 'POST':
        form = request.form
        user_id = form['user_id']
        architect_id = form['architect_id']
        project_name = form['project_name']

        with DBHelper() as db:
            result = db.insert_project(
                user_id, architect_id, project_name)
        return return_response(result)

@app.route("/update/project", methods=['POST'])
# TODO make it async
def update_project():
    if request.method == 'POST':
        form = request.form
        project_id = form['project_id']
        user_id = form['user_id']
        architect_id = form['architect_id']
        project_name = form['project_name']
        active = form['active']
        with DBHelper() as db:
            result = db.update_project(project_id, user_id, architect_id, project_name, active)
        return return_response(result)

@app.route("/delete/project", methods=['DELETE'])
# TODO make it async
def delete_project():
    if request.method == 'DELETE':
        form = request.form
        project_id = form['project_id']
        with DBHelper() as db:
            result = db.delete_project(project_id)
        return return_response(result)

@app.route("/read/file", methods=['GET'])
# TODO make it async
def get_file():
    if request.method == 'GET':
        project_id = request.args.get('project_id')
        with DBHelper() as db:
            rows = db.get_projects(project_id)
        result = []
        for row in rows:
            result.append({
                "file_id": row[0],
                "project_id": row[1],
                "file_name": row[2],
                "file_size":  row[3],
                "file_type": row[4],
                "file_data": row[5]
            })

        response = make_response()
        response.headers["Content-type"] = "application/json"
        directory = "./cache/"
        file_name = "test.xlsx"
        return send_from_directory(directory, file_name, as_attachment=True)

@app.route("/read/results", methods=['GET'])
# TODO make it async
def get_results():
    if request.method == 'GET':
        project_id = request.args.get('project_id')
        with DBHelper() as db:
            rows = db.get_results(project_id)
        result = []
        for row in rows:
            result.append({
                "pandas_result_id": row[0],
                "project_id": row[1],
                "file_id": row[2],
                "result_name":  row[3],
                "result_count": row[4],
                "result_finish": row[5],
                "result_table": json.dumps(row[6])})
        return return_response(result)

@app.route("/add/result", methods=['POST'])
# TODO make it async
def add_result():
    if request.method == 'POST':
        form = request.form
        project_id = form['project_id']
        file_id = form['file_id']
        result_name = form['result_name']
        result_count = form['result_count']
        result_finish = form['result_finish']
        result_table = json.loads(form['result_table'])
        with DBHelper() as db:
            result = db.insert_result(
                project_id, file_id, result_name, result_count, result_finish, result_table)
        return return_response(result)

@app.route("/update/result", methods=['POST'])
# TODO make it async
def update_result():
    if request.method == 'POST':
        form = request.form
        result_id = form['pandas_result_id']
        project_id = form['project_id']
        file_id = form['file_id']
        result_name = form['result_name']
        result_count = form['result_count']
        result_finish = form['result_finish']
        result_table = json.loads(form['result_table'])
        with DBHelper() as db:
            result = db.update_result(
                result_id, project_id, file_id, result_name, result_count, result_finish, result_table)
        return return_response(result)

@app.route("/delete/result", methods=['DELETE'])
# TODO make it async
def delete_result():
    if request.method == 'DELETE':
        form = request.form
        result_id = form['pandas_result_id']
        with DBHelper() as db:
            result = db.delete_result(result_id)
        return return_response(result)

@app.route("/delete/all/result", methods=['DELETE'])
# TODO make it async
def delete_all_result():
    if request.method == 'DELETE':
        form = request.form
        project_id = form['project_id']
        with DBHelper() as db:
            result = db.delete_all_result(project_id)
        return return_response(result)

@app.route("/add/sentence", methods=['POST'])
# TODO make it async
def add_sentence():
    if request.method == 'POST':
        form = request.form
        text = form['text']
        sentence_label_id = form['sentence_label_id']
        token_labels = json.loads(form['token_labels'])
        result_id = form['result_id']
        user_id = form['user_id']
        with DBHelper() as db:
            result = db.insert_sentence(text, sentence_label_id, token_labels, result_id, user_id)
        return return_response(result)

@app.route("/update/sentence", methods=['POST'])
# TODO make it async
def update_sentence():
    if request.method == 'POST':
        form = request.form
        id = form['id']
        text = form['text']
        sentence_label_id = form['sentence_label_id']
        token_labels = json.loads(form['token_labels'])
        result_id = form['result_id']
        user_id = form['user_id']
        with DBHelper() as db:
            result = db.update_sentence(id, text, sentence_label_id, token_labels, result_id, user_id)
        return return_response(result)

@app.route("/delete/sentence", methods=['DELETE'])
# TODO make it async
def delete_sentence():
    if request.method == 'DELETE':
        form = request.form
        id = form['id']
        with DBHelper() as db:
            result = db.delete_sentence(id)
        return return_response(result)

@app.route("/add/sentencelabel", methods=['POST'])
# TODO make it async
def add_sentence_label():
    if request.method == 'POST':
        form = request.form
        category = form['category']
        ordinal = form['ordinal']
        type_id = form['type_id']
        main_cat_id = form['main_cat_id']
        sub_cat_id = form['sub_cat_id']
        category_order = form['category_order']
        with DBHelper() as db:
            result = db.insert_sentence_label(category, ordinal, type_id, main_cat_id, sub_cat_id, category_order)
        return return_response(result)

@app.route("/update/sentencelabel", methods=['POST'])
# TODO make it async
def update_sentence_label():
    if request.method == 'POST':
        form = request.form
        id = form['id']
        category = form['category']
        ordinal = form['ordinal']
        type_id = form['type_id']
        main_cat_id = form['main_cat_id']
        sub_cat_id = form['sub_cat_id']
        category_order = form['category_order']
        with DBHelper() as db:
            result = db.update_sentence_label(id, category, ordinal, type_id, main_cat_id, sub_cat_id, category_order)
        return return_response(result)

@app.route("/read/all/sentencelabel", methods=['GET'])
# TODO make it async
def get_all_sentence_label():
    if request.method == 'GET':
        with DBHelper() as db:
            sentence_labels = db.get_all_sentence_label()
        result = []
        for row in sentence_labels:
            result.append({
                "id": row[0],
                "category": row[1],
                "ordinal": row[2],
                "created_date": row[3],
                "modified_date": row[4],
                 "type_id": row[5],
                 "main_cat_id": row[6],
                 "sub_cat_id": row[7],
                 "category_order": row[8],
            })
        return return_response(result)

@app.route("/read/columns", methods=['GET'])
# TODO make it async
def get_columns():
    if request.method == 'GET':
        project_id = request.args.get('project_id')
        result_id = request.args.get('result_id')
        architect_id = request.args.get('architect_id')
        with DBHelper() as db:
            columns = db.get_columns(project_id, result_id, architect_id)
        result = []
        for row in columns:
            result.append({
                "pandas_column_id": row[0],
                "project_id": row[1],
                "result_id": row[2],
                "architect_id": row[3],
                "content_value": row[4],
                 "content_text": row[5],
                 "quantity_value": row[6],
                 "quantity_text": row[7],
                 "unit_value": row[8],
                "unit_text": row[9],
                "material_value": row[10],
                "material_text": row[11],
                "wage_value": row[12],
                "wage_text": row[13],
                "sum_value": row[14],
                "sum_text": row[15],
                "created_date": row[16],
                "column_row": row[17]
            })
        return return_response(result)

@app.route("/add/column", methods=['POST'])
# TODO make it async
def add_column():
    if request.method == 'POST':
        form = request.form
        project_id = form['project_id']
        result_id = form['result_id']
        architect_id = form['architect_id']
        content_value = form['content_value']
        content_text = form['content_text']
        quantity_value = form['quantity_value']
        quantity_text = form['quantity_text']
        unit_value = form['unit_value']
        unit_text = form['unit_text']
        material_value = form['material_value']
        material_text = form['material_text']
        wage_value = form['wage_value']
        wage_text = form['wage_text']
        sum_value = form['sum_value']
        sum_text = form['sum_text']
        column_row = form['column_row']
        with DBHelper() as db:
            result = db.insert_column(project_id, result_id, architect_id, content_value, content_text, quantity_value,
                                    quantity_text, unit_value, unit_text, material_value, material_text,
                                    wage_value, wage_text, sum_value, sum_text, column_row)
        return return_response(result)

@app.route("/update/column", methods=['POST'])
# TODO make it async
def update_column():
    if request.method == 'POST':
        form = request.form
        pandas_column_id = form['pandas_column_id']
        project_id = form['project_id']
        result_id = form['result_id']
        architect_id = form['architect_id']
        content_value = form['content_value']
        content_text = form['content_text']
        quantity_value = form['quantity_value']
        quantity_text = form['quantity_text']
        unit_value = form['unit_value']
        unit_text = form['unit_text']
        material_value = form['material_value']
        material_text = form['material_text']
        wage_value = form['wage_value']
        wage_text = form['wage_text']
        sum_value = form['sum_value']
        sum_text = form['sum_text']
        column_row = form['column_row']
        with DBHelper() as db:
            result = db.update_column(pandas_column_id, project_id, result_id, architect_id, content_value, content_text, quantity_value,
                                    quantity_text, unit_value, unit_text, material_value, material_text,
                                    wage_value, wage_text, sum_value, sum_text, column_row)
        return return_response(result)

@app.route("/delete/column", methods=['DELETE'])
# TODO make it async
def delete_column():
    if request.method == 'DELETE':
        form = request.form
        pandas_column_id = form['pandas_column_id']
        with DBHelper() as db:
            result = db.delete_column(pandas_column_id)
        return return_response(result)

@app.route("/delete/all/column", methods=['DELETE'])
# TODO make it async
def delete_all_column_from_project():
    if request.method == 'DELETE':
        form = request.form
        project_id = form['project_id']
        with DBHelper() as db:
            result = db.delete_all_column(project_id)
        return return_response(result)


@app.route("/save/category", methods=['POST'])
# TODO make it async
def save_category():
    if request.method == 'POST':
        form = request.form
        name = form['name']
        ordinal = form['ordinal']
        with DBHelper() as db:
            result = db.insert_sentence_label(name, ordinal)
        return return_response(result)

@app.route("/update/category", methods=['POST'])
# TODO make it async
def update_category():
    if request.method == 'POST':
        form = request.form
        id = form['id']
        name = form['name']
        ordinal = form['ordinal']
        with DBHelper() as db:
            result = db.update_sentence_label(name, ordinal, id)
        return return_response(result)

@app.route("/read/all/category", methods=['GET'])
# TODO make it async
def read_all_category():
    if request.method == 'GET':
        with DBHelper() as db:
            categories = db.get_all_category()
        result = []
        for row in categories:
            result.append({
                "id": row[0],
                "category": row[1],
                "ordinal": row[2]
            })
        return return_response(result)

@app.route("/save/tokenlabel", methods=['POST'])
# TODO make it async
def save_token_label():
    if request.method == 'POST':
        form = request.form
        name = form['name']
        category_id = form['category_id']
        with DBHelper() as db:
            result = db.insert_token_label(name, category_id)
        return return_response(result)

@app.route("/update/tokenlabel", methods=['POST'])
# TODO make it async
def update_tokenlabel():
    if request.method == 'POST':
        form = request.form
        id = form['id']
        name = form['name']
        category_id = form['category_id']
        with DBHelper() as db:
            result = db.update_token_label(name, category_id, id)
        return return_response(result)

@app.route("/read/all/tokenlabel", methods=['GET'])
# TODO make it async
def read_all_tokenlabel():
    if request.method == 'GET':
        with DBHelper() as db:
            token_labels = db.get_all_token_label()
        result = []
        for row in token_labels:
            result.append({
                "id": row[0],
                "name": row[1],
                "category_id": row[2],
                "created_date": row[3],
                "modified_date": row[4]
            })
        return jsonify(result)

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
        return jsonify(result)
    else:
        return "Database error!"

if __name__ == "__main__":
    app.run(threaded=True, port=3000)