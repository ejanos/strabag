import pandas as pd
import numpy as np
import xlsxwriter
import os
import csv
import pathlib
import icecream as ic

ic = ic.IceCreamDebugger()
#ic.disable()


EXPORT_FILENAME = "pandas_converted.xlsx"
SOURCE_FILE = './data/b1.xlsx'
NUMERIC = "0123456789"

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

    cat_text = dict()
    cat_text['01'] = {'01': 'Földmunka'}
    cat_text['02'] = {'01': 'Betonozás',
                      '02': 'Zsaluzás',
                      '03': 'Betonacél'}
    cat_text['03'] = {'01': 'Felépítményi munkák'}
    cat_text['04'] = {'01': 'Vakolás'}
    cat_text['05'] = {'01': 'Vasúti pálya'}

    cat_content = dict()
    cat_content['01'] = {'01': '0010'}
    cat_content['02'] = {'01': '0010',
                         '02': '0010',
                         '03': '0010'}
    cat_content['03'] = {'01': '0010'}
    cat_content['04'] = {'01': '0010'}
    cat_content['05'] = {'01': '0010'}

    max_index = 0

    def sort_indicies(self, df_target):
        df_target.sort_values(by='TSZ', inplace=True)  # sorszám alapján rendezi
        df_target.reset_index(inplace=True, drop=True)   # újragyártja az indexet

    def top_index(self, x):
        if x == self.max_index:
            return -1
        return x

    def renumber_top_row(self, df_target):
        self.max_index = df_target[df_target['TSZ'] == "1"].index
        index = df_target.index.map(self.top_index, na_action='ignore')
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

        df = pd.read_excel(file, header=0, sheet_name=0, engine='openpyxl')
        df_target = self.insert_rows(source_cols, df, df_target, source_rows, target_cols, target_rows)
        self.sort_dataframe(df_target)
        self.save(df_target)

    def process_more_files(self, source_rows, source_cols, target_rows, target_cols, files):
        df_target = pd.read_csv("./data/ITWO_sablon3.csv", dtype=str)

        for file in files:
            df_target = self.process_more_sheets(source_rows, source_cols, target_rows, target_cols, file, df_target)

        self.sort_dataframe(df_target)

        self.save(df_target)


    def process_more_sheets(self, source_rows, source_cols, target_rows, target_cols, file, df_target):
        df_sheets = pd.read_excel(file, header=0, sheet_name=None, engine='openpyxl')
        sheets = df_sheets.keys()
        for sheet in sheets:
            df = pd.read_excel(file, header=0, sheet_name=sheet, engine='openpyxl')
            df_target = self.insert_rows(source_cols, df, df_target, source_rows, target_cols, target_rows)
        return df_target

    def process_and_save_sheets(self, source_rows, source_cols, target_rows, target_cols, file):
        df_target = pd.read_csv("./data/ITWO_sablon3.csv", dtype=str)
        #usecols = column_subset,
        #nrows = 100   beolvasott sorok száma

        df_sheets = pd.read_excel(file, header=0, sheet_name=None, engine='openpyxl')
        sheets = df_sheets.keys()
        for sheet in sheets:
            df = pd.read_excel(file, header=0, sheet_name=sheet, engine='openpyxl')
            df_target = self.insert_rows(source_cols, df, df_target, source_rows, target_cols, target_rows)

        self.sort_dataframe(df_target)

        self.save(df_target)

    def save(self, df_target):
        # Create a Pandas Excel writer using XlsxWriter as the engine.
        file = pathlib.Path(EXPORT_FILENAME)
        if file.exists():
            os.remove(EXPORT_FILENAME)
        writer = pd.ExcelWriter(EXPORT_FILENAME, engine='xlsxwriter', mode='w')
        # Convert the dataframe to an XlsxWriter Excel object.
        df_target.to_excel(writer, sheet_name='Sheet1')
        # Close the Pandas Excel writer and output the Excel file.
        writer.save()

    def sort_dataframe(self, df_target):
        self.sort_indicies(df_target)
        self.renumber_top_row(df_target)
        df_target.index += 1
        df_target.sort_index(inplace=True)
        df_target.set_index('TSZ', inplace=True)

    def insert_rows(self, source_cols, df, df_target, source_rows, target_cols, target_rows):
        for j, r in enumerate(source_rows):
            content_index = self.get_target_content(target_rows[j])
            self.increment_content_index(target_rows[j])
            new_row = [target_rows[j] + content_index]  # sorszám a kategória alapján kerül meghatározásra az MI által
            row_header = []
            row_header.append(self.column_subset[0])
            for i, c in enumerate(source_cols):
                x = df.iloc[r, c]
                new_row.append(x)
                row_header.append(self.column_subset[target_cols[i]])
            row_df = pd.DataFrame([new_row], columns=row_header, dtype=str)
            df_target = pd.concat([df_target, row_df], join='outer')
        return df_target

    def get_target_content(self, target):
        top = target[:2]
        sub = target[3:5]
        if self.is_valid_target(target):
            content_index = self.cat_content[top][sub]
        else:
            raise ValueError("invalid target value")
        return content_index + "."

    def increment_content_index(self, target):
        top = target[:2]
        sub = target[3:5]
        num = int(self.cat_content[top][sub])
        num += 10
        self.cat_content[top][sub] = self.extend_with_nulls(num)

    @staticmethod
    def extend_with_nulls(num):
        num = str(num)
        while len(num) < 4:
            num = "0" + num
        return num

    @staticmethod
    def increment(txt):
        num = int(txt)
        if num < 9:
            num += 1
            return "0" + str(num)
        elif num == 9:
            return "10"
        else:
            num += 1
            return str(num)

    @staticmethod
    def is_valid_target(target):
        if target[0] in NUMERIC and target[1] in NUMERIC and target[2] == "." and target[3] in NUMERIC and target[4] in NUMERIC and target[5] == ".":
            return True
        return False


if __name__ == '__main__':
    # [(forrás oszlopok), (forrás sorok), cél_sor, cél_oszlop]
    # 5 = F, 0-ról kezdődik az index

    conv = ConvertExcel()
    source_rows = (5,6,7,8,9,10,11,12,13,)
    source_cols = (5,6,)
    target_rows = ("02.01.", "02.02.", "02.03.", "02.01.", "02.02.", "02.03.", "02.01.", "02.02.", "02.03.")
    target_cols = (2,4,)
    conv.process(source_rows, source_cols, target_rows, target_cols, SOURCE_FILE)
