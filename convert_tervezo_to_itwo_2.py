import pandas as pd
import numpy as np
import xlsxwriter
import os
import csv
import pathlib


EXPORT_FILENAME = "pandas_simple.xlsx"

shifted_index = 0

def shift_index(x):
    if x >= shifted_index:
        return x + 1
    return x

def renumber_rows(df_target, target_index):
    global shifted_index
    shifted_index = target_index
    #indicies = df_target.index.tolist()
    if target_index in df_target.index:
        index = df_target.index.map(shift_index, na_action='ignore')
        df_target.index = index


def read_template(filename):
        res = []
        with open(filename, 'r', encoding='utf-8-sig') as csv_file:
            reader = csv.reader(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            index = 1
            for row in reader:
                res.append(row)
                index += 1
        return res[:1], res[1:], index

def process(indices):
    column_subset = [
        "TSZ",
        "ÁT",
        "Rövid szöveg"
        "Hosszú szöveg"
        "TJ - menny.",
        "VÁ - menny.",
        "ME",
        "Eá",
        "FE",
        "Óra",
        "Anyag",
        "Díj"
    ]
    col_num = len(column_subset)
    df_target = pd.read_csv(
    "./data/ITWO_sablon3.csv", dtype=str

    #usecols = column_subset,
    #nrows = 100   beolvasott sorok száma
         )

    df = pd.read_excel('./data/b1.xlsx', header=0, sheet_name='Total', engine='openpyxl')
    col = indices[0]
    row = indices[1]
    target_row = indices[2]
    target_col = indices[3]
    row_index = 0
    for r in row:
        new_row = ["02.01."]  # sorszám a kategória alapján kerül meghatározásra az MI által
        new_row.extend([None for x in range(target_col)])
        for c in col:
            x = df.iloc[r - 2, c]
            new_row.append(x)

        new_row.extend([None for x in range(col_num - len(new_row))])
        #ic(new_row)
        target_index = row_index + target_row
        renumber_rows(df_target, target_index)
        row_header = column_subset[:len(new_row)]
        row_df = pd.DataFrame([new_row], columns=row_header, index=[target_index], dtype=str)
        df_target = pd.concat([df_target, row_df], join='inner')
        row_index += 1

    #df_target.sort_values(by='TSZ', inplace=True) sorszám alapján rendezi
    #df_target.reset_index(inplace=True, drop=True) újragyártja az indexet
    df_target.sort_index(inplace=True)  # inplace: ezt az objektumot, dataframe-t rendezi

    # Create a Pandas Excel writer using XlsxWriter as the engine.

    file = pathlib.Path(EXPORT_FILENAME)
    if file.exists():
        os.remove(EXPORT_FILENAME)

    writer = pd.ExcelWriter('pandas_simple.xlsx', engine='xlsxwriter', mode='w')

    # Convert the dataframe to an XlsxWriter Excel object.
    df_target.to_excel(writer, sheet_name='Sheet1')

    # Close the Pandas Excel writer and output the Excel file.
    writer.save()


if __name__ == '__main__':
    # [(oszlopok), (sorok), cél_sor, cél_oszlop]
    # 5 = F, 0-ról kezdődik az index

    foldmunka = [(6,), (5,6,7,8,9,10,11,12,13,), 5, 5]
    process(foldmunka)
