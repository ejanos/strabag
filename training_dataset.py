from db_helper import DBHelper
import pandas as pd
from convert_excel import ConvertExcel
from sentence_label import SentenceLabel
from helpers import Helpers

class TrainingDataset():
    NUMERIC = "01234567890.,"
    BUFFER_SIZE = 10
    conv = ConvertExcel()
    buffer = []
    token_label_ids = []

    def get_token_label_ids(self):
        with DBHelper() as db:
            self.token_label_ids = db.get_all_token_label_frontend_ids()

    def filter_token_labels(self, token_labels):
        result = []
        for token in token_labels:
            if token in self.token_label_ids:
                result.append(token)
            else:
                result.append(0)
        return result

    def save(self, content_column, source_rows, target_categories, token_labels, file):
        self.get_token_label_ids()
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
        sentence_id = self.process_buffer()
        return sentence_id

    def save_row(self, target_category, content, token_labels):
        token_labels = self.filter_token_labels(token_labels)
        sentence_id = 1
        if len(self.buffer) > self.BUFFER_SIZE:
            self.buffer.append((target_category, content, token_labels,))
            with DBHelper() as db:
                sentence_id = db.insert_sentences(self.buffer)
            self.buffer.clear()
        else:
            self.buffer.append((target_category, content, token_labels,))
        return sentence_id

    def process_buffer(self):
        if len(self.buffer):
            with DBHelper() as db:
                sentence_id = db.insert_sentences(self.buffer)
                return sentence_id
        return 1

    def save_one_row(self, target_category, content, token_labels):
        with DBHelper() as db:
            category_id = db.get_sentence_label_id_by_ordinal(target_category)
            if category_id:
                sentence_id = db.insert_sentence(content, category_id, token_labels)
                return sentence_id
            return 0

    def update_one_row(self, target_category, content, token_labels):
        with DBHelper() as db:
            category_id = db.get_sentence_label_id_by_ordinal(target_category)
            sentence_id = db.get_sentence_id_by_text(content)
            if category_id and sentence_id:
                sentence_id = db.update_sentence(sentence_id, content, category_id, token_labels)
                return sentence_id
            return 0








