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
    header, template, i = read_template("./data/ITWO_sablon3.csv")
    index = [x for x in range(1, i - 1)]
    df_target = pd.DataFrame(template, columns=header[0])
    df_target.set_index('TSZ')
    df = pd.read_excel('./data/b1.xlsx', header=0, sheet_name='Total', engine='openpyxl')
    #df_target = pd.read_excel('./data/ITWO_sablon2.xlsx', header=10, sheet_name='1_1', engine='openpyxl')
    col = indices[0]
    row = indices[1]
    target_row = indices[2]
    target_col = indices[3]
    row_index = 0
    for r in row:
        new_row = ["02.01.", "0", "0", "0", "0"]

        for c in col:
            x = df.iloc[r, c]
            new_row.append(x)
        print(new_row)
        target_index = row_index + target_row
        #renumber_rows(df_target, target_index)
        row_header = header[0][:len(new_row)]
        row_df = pd.DataFrame([new_row], columns=row_header, index=[target_index])
        #row_df.set_index('TSZ')
        df_target = pd.concat([df_target, row_df], join='inner')
        row_index += 1

    df_target.set_index('TSZ')
    #df_target.sort_index()
    #df_target.reset_index()
    #df_target.reset_index(drop=True)
    df_target.sort_values(by=['TSZ'])

    # Create a Pandas Excel writer using XlsxWriter as the engine.

    file = pathlib.Path(EXPORT_FILENAME)
    if file.exists():
        os.remove(EXPORT_FILENAME)

    writer = pd.ExcelWriter('pandas_simple.xlsx', engine='xlsxwriter', mode='w')

    # Convert the dataframe to an XlsxWriter Excel object.
    df_target.to_excel(writer, sheet_name='Sheet1')

    # Close the Pandas Excel writer and output the Excel file.
    writer.save()


    #print(df)
    # print column headers
    #print(df.columns.ravel())
    # print column
    #print(df['Work/\nMunkanem.1'].tolist())
    # print row
    #print(df.iloc[832])
    # lekérdezés sor
    #print(df.loc[(df["Quantity/\nmennyiség"] == 3.00) & (df["Materila unit price/\nanyag egység ár HUF"] == 0)])
    #df.to_excel("converted.xlsx")

    # https://xlsxwriter.readthedocs.io/worksheet.html#write_url




# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # [(oszlopok), (sorok), cél_sor, cél_oszlop]
    # 5 = F, 0-ról kezdődik az index

    foldmunka = [(6,), (5,6,7,8,9,10,), 5, 5]
    process(foldmunka)
