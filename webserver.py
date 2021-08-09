from typing import (Deque, Dict, FrozenSet, List, Optional, Sequence, Set, Tuple, Union)
from fastapi import FastAPI, File, UploadFile
from convert_excel import ConvertExcel

CACHE = "./cache/"

conv = ConvertExcel

Vector = List[int]

app = FastAPI()

@app.post("/upload/")
async def upload(file: UploadFile = File(...)):
    contents = await file.read()
    with open(CACHE + file.filename, 'w') as f_w:
        f_w.write(contents)
    return {"message": "File saved"}

@app.post("/convert/")
#async def root():
# TODO make it async
def convert(
        source_rows: Vector,
        source_cols: Vector,
        target_rows: Vector,
        target_cols: Vector):

    conv.process(source_rows,
                 source_cols,
                 target_rows,
                 target_cols,
                 './cache/tmp.xlsx')

    return {"message": "file is converted"}

