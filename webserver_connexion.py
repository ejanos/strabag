from typing import (Deque, Dict, FrozenSet, List, Optional, Sequence, Set, Tuple, Union)
from convert_excel import ConvertExcel
import os
import aiofiles
import requests
import os
import yaml
from db_helper import DBHelper
from training_dataset import TrainingDataset
from process_columns import ProcessColumns
import connexion

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
def compare(texts: str) -> {[str], [int], int }:
    #if request.method == 'POST':
    #form = request.form
    #texts = convert_string_list(form['texts'])
    target_columns, target_targets, user_id = process_columns.compare(texts)
    return {"target_columns": target_columns,
            "target_targets": target_targets,
            "user_id": user_id}



if __name__ == '__main__':
    app = connexion.FlaskApp(__name__, port=5000, specification_dir='openapi/')
    app.add_api('excel-api.yaml', arguments={'title': 'Excel Webserver'})
    app.run()