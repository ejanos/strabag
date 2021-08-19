import pandas as pd
import numpy as np
import xlsxwriter
import os
import csv
import pathlib
import icecream as ic
from db_helper import DBHelper
#from hubert_model import HubertModel
from helpers import Helpers
import numpy as np


ic = ic.IceCreamDebugger()
ic.disable()


EXPORT_FILENAME = "pandas_converted.xlsx"
SOURCE_FILE = './data/b1.xlsx'
NUMERIC = "0123456789"

class TopLevelCategory:
    ordinal = ""
    name = ""
    def __init__(self, ordinal=None, name=None):
        self.ordinal = ordinal
        self.name = name

class ConvertExcel():
    db = DBHelper()
    #model = HubertModel()
    test = False
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

    # test data, load_category() will overwrite these data
    cat_text = dict()
    cat_text['01'] = {'01': 'Földmunka'}
    cat_text['02'] = {'01': 'Betonozás',
                      '02': 'Zsaluzás',
                      '03': 'Betonacél'}
    cat_text['03'] = {'01': 'Felépítményi munkák'}
    cat_text['04'] = {'01': 'Vakolás'}
    cat_text['05'] = {'01': 'Vasúti pálya'}

    # test data, load_category() will overwrite these data
    cat_content = dict()
    cat_content['01'] = {'01': '0010'}
    cat_content['02'] = {'01': '0010',
                         '02': '0010',
                         '03': '0010'}
    cat_content['03'] = {'01': '0010'}
    cat_content['04'] = {'01': '0010'}
    cat_content['05'] = {'01': '0010'}

    top_level_categories = []

    category_by_index = dict()

    max_index = 0

    def __init__(self, test=False):
        self.test = test

    def load_categories(self):
        if self.test:
            return
        rows = self.db.get_all_categories()
        cat_content = dict()
        cat_text = dict()
        for row in rows:
            id = row[0]
            name = row[1]
            category = row[2]
            if category.contains(".") == 1 and len(category) < 4:
                top_level_cat = TopLevelCategory(name=name, ordinal=category)
                self.top_level_categories.append(top_level_cat)
                continue
            self.category_by_index[id] = category
            top, sub = self.split_top_sub(category)
            if top in cat_content:
                cat_content[top][sub] = '0010'
            else:
                cat_content[top] = {sub: '0010'}
            if top in cat_text:
                cat_text[top][sub] = name
            else:
                cat_text[top] = {sub: name}
        self.cat_content = cat_content
        self.cat_text = cat_text


    def split_top_sub(self, category):
        top = category[:2]
        sub = category[3:5]
        return top, sub


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
        self.load_categories()
        df_target = pd.read_csv("./data/ITWO_sablon3.csv", dtype=str)
        #usecols = column_subset,
        #nrows = 100   beolvasott sorok száma

        df = pd.read_excel(file, header=0, sheet_name=0, engine='openpyxl')
        try:
            df_target = self.insert_rows(source_cols, df, df_target, source_rows, target_cols, target_rows)
            df_target = self.insert_top_level_category_rows(df_target)
        except AssertionError as value_error:
            print(value_error)
        self.sort_dataframe(df_target)
        self.save(df_target)
        cwd = os.getcwd()
        return cwd, EXPORT_FILENAME

    def process_mi(self, source_cols, target_cols, file):
        self.load_categories()
        df_target = pd.read_csv("./data/ITWO_sablon3.csv", dtype=str)
        df = pd.read_excel(file, header=0, sheet_name=0, engine='openpyxl')

        rows = df.shape[0]
        max_rows = rows
        if max_rows > 15:
            max_rows = 15
        data_slice = df.loc[5:max_rows]

        ic(data_slice.values.tolist())
        # index of text row, which needs to be classified by the model
        txt_index = self.get_index_of_longest(data_slice.values.tolist())
        ic(txt_index)

        target_categories = []
        source_rows = []
        first_row = 1

        for i, txt in enumerate(df.iloc[first_row:,txt_index]):
            if txt and not np.isna(txt):
                # TODO felhasználni cat_prob valószínűségi értéket a blokkok értelmezéséhez
                # TODO plusz a tokenek értékét is erre lehet felhasználni
                # TODO token probability-t is fel lehet használni erre !!!
                #category, cat_prob, tokens = self.model.predict(txt)
                category, cat_prob, tokens = (0,0,0)
                if category and category[0] in self.category_by_index:
                    cat_name = self.category_by_index[category[0]]
                    target_categories.append(cat_name)
                    source_rows.append(i + first_row)

        try:
            df_target = self.insert_rows(source_cols, df, df_target, source_rows, target_cols, target_categories)
            df_target = self.insert_top_level_category_rows(df_target)
        except AssertionError as value_error:
            print(value_error)
        self.sort_dataframe(df_target)
        self.save(df_target)
        cwd = os.getcwd()
        return cwd, EXPORT_FILENAME


    def process_more_files(self, source_rows, source_cols, target_rows, target_cols, files):
        self.load_categories()
        df_target = pd.read_csv("./data/ITWO_sablon3.csv", dtype=str)
        try:
            for file in files:
                ic(file)
                df_target = self.process_more_sheets(source_rows, source_cols, target_rows, target_cols, file, df_target)
            df_target = self.insert_top_level_category_rows(df_target)
        except AssertionError as value_error:
            print(value_error)
        self.sort_dataframe(df_target)
        self.save(df_target)
        cwd = os.getcwd()
        return cwd, EXPORT_FILENAME

    def process_more_sheets_and_save(self, source_rows, source_cols, target_rows, target_cols, file, df_target):
        self.load_categories()
        df_target = pd.read_csv("./data/ITWO_sablon3.csv", dtype=str)
        try:
            df_target = self.process_more_sheets(source_rows, source_cols, target_rows, target_cols, file, df_target)
            df_target = self.insert_top_level_category_rows(df_target)
        except AssertionError as value_error:
            print(value_error)
        self.sort_dataframe(df_target)
        self.save(df_target)
        cwd = os.getcwd()
        return cwd, EXPORT_FILENAME

    def process_more_sheets(self, source_rows, source_cols, target_rows, target_cols, file, df_target):
        df_sheets = pd.read_excel(file, header=0, sheet_name=None, engine='openpyxl')
        sheets = df_sheets.keys()
        try:
            for sheet in sheets:
                df = pd.read_excel(file, header=0, sheet_name=sheet, engine='openpyxl')
                df_target = self.insert_rows(source_cols, df, df_target, source_rows, target_cols, target_rows)
        except ValueError as value_error:
            print(value_error)
        return df_target

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
        assert len(source_rows) == len(target_rows)
        assert len(source_cols) == len(target_cols)
        assert df_target.columns.size > max(target_cols)
        assert df.columns.size > max(source_cols)
        assert df.shape[0] > max(source_rows)
        assert df_target.columns.size > max(target_cols)

        assert self.are_valid_categories(target_rows)

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

    def insert_top_level_category_rows(self, df_target):
        row_header = []
        row_header.append(self.column_subset[0])
        row_header.append(self.column_subset[2])
        for top in self.top_level_categories:
            row_df = pd.DataFrame([[top.ordinal, top.name]], columns=row_header, dtype=str)
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

    def are_valid_categories(self, target):
        for t in target:
            top = t[:2]
            sub = t[3:5]
            if self.is_valid_target(t):
                ic(top, sub)
                if top in self.cat_content and sub in self.cat_content[top]:
                    continue
                else:
                    return False
            else:
                return False
        return True

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

    @staticmethod
    def get_index_of_longest(data):
        row_len = len(data[0])
        max_rows = len(data)
        # calculate score just small set of rows
        if max_rows > 10:
            max_rows = 10
        data_slice = data[0:max_rows]
        return Helpers.get_max_row_number(data_slice, row_len)


def test_process():
    global source_rows
    source_rows = (5, 6, 7, 8, 9, 10, 11, 12, 13,)
    source_cols = (5, 6,)
    target_rows = ("02.01.", "02.02.", "02.03.", "02.01.", "02.02.", "02.03.", "02.01.", "02.02.", "02.03.")
    target_cols = (2, 4,)
    conv.process(source_rows, source_cols, target_rows, target_cols, SOURCE_FILE)

def test_process_mi():
    source_cols = (5, 6,)
    target_cols = (2, 4,)
    conv.process_mi(source_cols, target_cols, SOURCE_FILE)


if __name__ == '__main__':
    # [(forrás oszlopok), (forrás sorok), cél_sor, cél_oszlop]
    # 5 = F, 0-ról kezdődik az index

    #conv = ConvertExcel(test=True)
    conv = ConvertExcel(test=False)
    #test_process()
    test_process_mi()
