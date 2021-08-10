from db_helper import DBHelper
import pandas as pd
from convert_excel import ConvertExcel
from sentence_label import SentenceLabel

class TrainingDataset():
    NUMERIC = "01234567890.,"
    BUFFER_SIZE = 10
    db = DBHelper()
    conv = ConvertExcel()
    buffer = []
    buffer_count = 0
    sen_labels = dict()  # sentence_labels tábla tartalma

    def __init__(self):
        categories = self.db.get_all_categories()
        for cat in categories:
            self.sen_labels[cat.ordinal] = cat
        categories.clear()

    def save(self, source_rows, source_cols, target_rows, target_cols, file):
        df = pd.read_excel(file, header=0, sheet_name='Total', engine='openpyxl')

        df_target = self.extract_rows(source_cols, df, source_rows, target_cols, target_rows)

    def extract_rows(self, source_cols, df, source_rows, target_cols, target_rows):
        row_index = 0
        for j, r in enumerate(source_rows):
            new_row = [target_rows[j]]  # sorszám a kategória alapján kerül meghatározásra az MI által
            # TODO elmenteni oszlopok headert is az adatbázisba, melyik oszlop hova van bind-olva
            row_header = []
            row_header.append(self.conv.column_subset[0])
            for i, c in enumerate(source_cols):
                x = df.iloc[r, c]
                new_row.append(x)
                row_header.append(self.conv.column_subset[target_cols[i]])
                self.save_row(new_row)
            row_index += 1

    def save_row(self, row):
        row_len = len(row)
        if self.buffer_count > self.BUFFER_SIZE:
            self.save_buffer2database(row_len)

    def save_buffer2database(self, row_len):
        row_type = self.test_row_type(row_len)
        row_index = self.get_text_row_indicies(row_type)
        data = []
        for row in self.buffer:
            data_row = []
            for i in row_index:
                data_row.append(row[i])
            data.append(data_row)






    def get_text_row_indicies(self, row_type):
        row_index = [0]
        for i, is_text in enumerate(row_type):
            if i > 0 and is_text:
                row_index.append(i)
        return row_index

    def test_row_type(self, row_len):
        row_type = [False for x in range(len(row_len))]
        for row in self.buffer:
            for i, cell in enumerate(row):
                if self.is_cell_text(cell):
                    row_type[i] = True
        return row_type

    def is_cell_text(self, cell):
        if len(cell) > 4 and (not self.is_numeric()):
            return True
        return False

    def is_numeric(self, cell):
        for c in cell:
            if c in self.NUMERIC:
                continue
            else:
                return False
        return True



