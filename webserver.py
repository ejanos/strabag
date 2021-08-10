from typing import (Deque, Dict, FrozenSet, List, Optional, Sequence, Set, Tuple, Union)
from convert_excel import ConvertExcel
import os
import aiofiles
import requests
from flask import Flask, request
import os
import yaml

CACHE = "./cache/"
BUFFER = 50_000

conv = ConvertExcel()

Vector = List[int]

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = CACHE

def convert_int_list(txt):
    result = []
    if txt:
        txt_split = txt.split(",")
    else:
        return None
    for token in txt_split:
        result.append(int(token))
    return result

@app.route("/convert", methods=['POST'])
# TODO make it async
def convert():
    if request.method == 'POST':
        form = request.form
        source_rows = convert_int_list(form['source_rows'])
        print(source_rows)
        source_cols = convert_int_list(form['source_cols'])
        target_rows = convert_int_list(form['target_rows'])
        target_cols = convert_int_list(form['target_cols'])
        f = request.files['file']
        filename = f.filename
        cwd = os.getcwd()
        file_path = os.path.join(cwd, 'cache2', filename)
        print(file_path)
        f.save(file_path)

        conv.process(source_rows, source_cols, target_rows, target_cols, file_path)
        return "ok"

    return "invalid method"

if __name__ == "__main__":
    app.run(threaded=True, port=5000)