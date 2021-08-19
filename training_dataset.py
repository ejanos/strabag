from db_helper import DBHelper
import pandas as pd
from convert_excel import ConvertExcel
from sentence_label import SentenceLabel
from helpers import Helpers

class TrainingDataset():
    NUMERIC = "01234567890.,"
    BUFFER_SIZE = 10
    db = DBHelper()
    conv = ConvertExcel()
    buffer = []


    def save(self, content_column, source_rows, target_categories, token_labels, file):
        df = pd.read_excel(file, header=0, sheet_name='Total', engine='openpyxl')

        result = self.extract_rows(content_column, df, source_rows, target_categories, token_labels)
        return result

    def extract_rows(self, content_column, df, source_rows, target_categories, token_labels):
        row_index = 0
        for j, r in enumerate(source_rows):
            text_content = df.iloc[r, content_column]
            # is success to save to DB?
            if not self.save_row(target_categories[j], text_content, token_labels[j]):
                return None
            row_index += 1

    def save_row(self, target_category, content, token_labels):
        sentence_id = 1
        if len(self.buffer) > self.BUFFER_SIZE:
            self.buffer.append((target_category, content, token_labels,))
            sentence_id = self.db.insert_sentences(self.buffer)
        else:
            self.buffer.append((target_category, content, token_labels,))
        return sentence_id







