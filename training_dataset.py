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


    def save(self, source_rows, source_cols, target_rows, target_cols, token_labels, file):
        df = pd.read_excel(file, header=0, sheet_name='Total', engine='openpyxl')

        result = self.extract_rows(source_cols, df, source_rows, target_cols, target_rows, token_labels)
        return result

    def extract_rows(self, source_cols, df, source_rows, target_cols, target_rows, token_labels):
        row_index = 0
        for j, r in enumerate(source_rows):
            new_row = [target_rows[j]]  # sorszám a kategória alapján kerül meghatározásra az MI által
            row_header = []
            row_header.append(self.conv.column_subset[0])
            for i, c in enumerate(source_cols):
                x = df.iloc[r, c]
                new_row.append(x)
                row_header.append(self.conv.column_subset[target_cols[i]])
                # is success to save to DB?
                if not self.save_row(new_row, token_labels[j]):
                    return None
            row_index += 1

    def save_row(self, row, token_labels):
        row_len = len(row)
        sentence_id = 1
        if self.buffer_count > self.BUFFER_SIZE:
            self.buffer.append((row, token_labels,))
            sentence_id = self.save_buffer2database(row_len)
        else:
            self.buffer.append((row, token_labels,))
        return sentence_id

    def save_buffer2database(self, row_len):
        row_type = self.test_row_type(row_len)
        row_index = self.get_text_row_indicies(row_type)
        data = []

        for row, token_labels in self.buffer:
            data_row = []
            for i in row_index:
                data_row.append(row[i])
            data.append(data_row)
        max_index = self.get_index_of_longest(data)
        filtered_data = []
        for row, token_labels in self.buffer:
            filtered_data.append([row[0], row[max_index], token_labels])
        sentence_id = self.db.insert_sentences(filtered_data)
        return sentence_id

    def get_index_of_longest(data):
        row_len = len(data[0])
        row_score = [0 for x in range(row_len)]
        for row in data:
            for i, cell in enumerate(row):
                row_score[i] += len(cell)
        max_index = 0
        max_score = 0
        for i, score in enumerate(row_score[1:]):  # 0. oszlop a sorszám
            if score > max_score:
                max_index = i
        return max_index

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



