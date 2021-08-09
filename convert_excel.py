import pandas as pd
import numpy as np
import xlsxwriter
import os
import csv
import pathlib


EXPORT_FILENAME = "pandas_converted.xlsx"
SOURCE_FILE = './data/b1.xlsx'

class ConvertExcel():
    column_subset = [
            "TSZ",
            "ÁT",
            "Rövid szöveg",
            "Hosszú szöveg",
            "TJ-menny.",
            "VÁ-menny.",
            "ME",
            "Eá",
            "FE",
            "Óra",
            "Anyag",
            "Díj",
        "15.",
        "16.",
        "17.",
        "18.",
        "Maradék",
        "TÖ",
        "FE.1",
        ]

    shifted_index = 0

    def sort_indicies(self, df_target):
        df_target.sort_values(by='TSZ', inplace=True)  # sorszám alapján rendezi
        df_target.reset_index(inplace=True, drop=True)   # újragyártja az indexet

    def shift_index(self, x):
        if x >= self.shifted_index:
            return x + 1
        return x

    def renumber_rows(self, df_target, target_index):
        global shifted_index
        shifted_index = target_index
        if target_index in df_target.index:
            index = df_target.index.map(self.shift_index, na_action='ignore')
            df_target.index = index


    def read_template(self, filename):
            res = []
            with open(filename, 'r', encoding='utf-8-sig') as csv_file:
                reader = csv.reader(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                index = 1
                for row in reader:
                    res.append(row)
                    index += 1
            return res[:1], res[1:], index

    def process(self, source_rows, source_cols, target_rows, target_cols, file):
        df_target = pd.read_csv("./data/ITWO_sablon3.csv", dtype=str)
        #usecols = column_subset,
        #nrows = 100   beolvasott sorok száma

        df = pd.read_excel(file, header=0, sheet_name='Total', engine='openpyxl')
        #source_col = indices[0]
        #source_row = indices[1]
        #target_row = indices[2]
        #target_col = indices[3]
        df_target = self.insert_rows(source_cols, df, df_target, source_rows, target_cols, target_rows)

        df_target.sort_index(inplace=True)  # inplace: ezt az objektumot, dataframe-t rendezi

        # Create a Pandas Excel writer using XlsxWriter as the engine.
        file = pathlib.Path(EXPORT_FILENAME)
        if file.exists():
            os.remove(EXPORT_FILENAME)

        writer = pd.ExcelWriter(EXPORT_FILENAME, engine='xlsxwriter', mode='w')

        # Convert the dataframe to an XlsxWriter Excel object.
        df_target.to_excel(writer, sheet_name='Sheet1')

        # Close the Pandas Excel writer and output the Excel file.
        writer.save()


    def insert_rows(self, source_cols, df, df_target, source_rows, target_cols, target_rows):
        row_index = 0
        for j, r in enumerate(source_rows):
            new_row = ["02.01."]  # sorszám a kategória alapján kerül meghatározásra az MI által
            row_header = []
            row_header.append(self.column_subset[0])
            for i, c in enumerate(source_cols):
                x = df.iloc[r - 2, c]
                new_row.append(x)
                row_header.append(self.column_subset[target_cols[i]])
            target_index = target_rows[j]
            self.renumber_rows(df_target, target_index)
            row_df = pd.DataFrame([new_row], columns=row_header, dtype=str, index=[target_index])
            df_target = pd.concat([df_target, row_df], join='outer')
            row_index += 1
        return df_target


if __name__ == '__main__':
    # [(forrás oszlopok), (forrás sorok), cél_sor, cél_oszlop]
    # 5 = F, 0-ról kezdődik az index

    conv = ConvertExcel()
    source_rows = (5,6,7,8,9,10,11,12,13,)
    source_cols = (5,6,)
    target_rows = (2,4,)
    target_cols  = (5,6,7,8,9,10,11,12,13,)
    conv.process(source_rows, source_cols, target_rows, target_cols, SOURCE_FILE)
