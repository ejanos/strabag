import psycopg2
import icecream as ic
from contextlib import contextmanager
import json

ic = ic.IceCreamDebugger()
ic.disable()

with open('connect_string.json', 'r', encoding='utf-8') as f:
    DATA = json.load(f)

class DBHelper:
    conn = ""
    cur = ""
    password = ""

    def __init__(self, test=False):
        self.test = test

    def open_connection(self):
        try:
            self.connect()
        finally:
            self.close_connection()

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close_connection()

    def connect(self):
        if not self.cur:
            if self.test:
                self.conn = psycopg2.connect(
                    host=DATA["HOST"],
                    database=DATA["TRAIN_EXCEL_TEST"],
                    user=DATA["USER"],
                    password=DATA["PASSWORD"])
            else:
                self.conn = psycopg2.connect(
                    host=DATA["HOST"],
                    database=DATA["TRAIN_EXCEL"],
                    user=DATA["USER"],
                    password=DATA["PASSWORD"])
            self.cur = self.conn.cursor()

    def close_connection(self):
        self.conn.close()
        self.cur = None

    def insert_architect(self, name):
        sql = """INSERT INTO PandasArchitect(ArchitectName) VALUES(%s) RETURNING PandasArchitectId;"""
        try:
            self.cur.execute(sql, (name,))
            architect_id = self.cur.fetchone()[0]
            self.conn.commit()
        except(Exception, psycopg2.DatabaseError) as error:
            print(error)
            return None
        return architect_id

    def insert_column(self, project_id, result_id, architect_id, content_value, content_text, quantity_value,
                quantity_text, unit_value, unit_text, material_value, material_text,
                wage_value, wage_text, sum_value, sum_text, column_row):
        sql = """INSERT INTO PandasColumn(PandasProjectId, PandasResultId, PandasArchitectId, ContentValue, ContentText, QuantityValue,
                QuantityText, UnitValue, UnitText, MaterialValue, MaterialText,
                WageValue, WageText, SumValue, SumText, ColumnRow) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s, %s,%s,%s,%s,%s,%s) RETURNING PandasColumnId;"""
        try:
            self.cur.execute(sql, (project_id, result_id, architect_id, content_value, content_text, quantity_value,
                quantity_text, unit_value, unit_text, material_value, material_text,
                wage_value, wage_text, sum_value, sum_text, column_row,))
            column_id = self.cur.fetchone()[0]
            self.conn.commit()
        except(Exception, psycopg2.DatabaseError) as error:
            print(error)
            return None
        return column_id

    def update_column(self, pandas_column_id, project_id, result_id, architect_id, content_value, content_text, quantity_value,
                quantity_text, unit_value, unit_text, material_value, material_text,
                wage_value, wage_text, sum_value, sum_text, column_row):
        sql = """UPDATE PandasColumn SET PandasColumnId=%s, PandasProjectId=%s, PandasResultId=%s, PandasArchitectId=%s, ContentValue=%s, ContentText=%s, QuantityValue=%s,
                QuantityText=%s, UnitValue=%s, UnitText=%s, MaterialValue=%s, MaterialText=%s,
                WageValue=%s, WageText=%s, SumValue=%s, SumText=%s, ColumnRow=%s WHERE PandasColumnId=%s RETURNING PandasColumnId;"""
        try:
            self.cur.execute(sql, (project_id, result_id, architect_id, content_value, content_text, quantity_value,
                quantity_text, unit_value, unit_text, material_value, material_text,
                wage_value, wage_text, sum_value, sum_text, column_row,pandas_column_id,))
            column_id = self.cur.fetchone()[0]
            self.conn.commit()
        except(Exception, psycopg2.DatabaseError) as error:
            print(error)
            return None
        return column_id

    def insert_sentence_label(self, category, ordinal, type_id, main_cat_id, sub_cat_id, category_order):
        sql = """INSERT INTO sentence_label(CategoryName, Ordinal, TypeId, MainCatId, SubCatId, CategoryOrder) VALUES(%s,%s,%s,%s,%s,%s) RETURNING PandasCategoryId;"""
        try:
            self.cur.execute(sql, (category, ordinal, type_id, main_cat_id, sub_cat_id, category_order,))
            sentence_label_id = self.cur.fetchone()[0]
            self.conn.commit()
        except(Exception, psycopg2.DatabaseError) as error:
            print(error)
            return None
        return sentence_label_id


    def insert_sentence(self, text, sentence_label_id, token_labels, result_id, user_id):
        sql = """INSERT INTO sentence(text, sentence_label_id, token_labels, PandasResultId, UserId) VALUES(%s,%s,%s,%s,%s) RETURNING id;"""
        try:
            self.cur.execute(sql, (text, sentence_label_id, token_labels, result_id, user_id,))
            sentence_id = self.cur.fetchone()[0]
            self.conn.commit()
        except(Exception, psycopg2.DatabaseError) as error:
            print(error)
            return None
        return sentence_id

    def insert_project(self, user_id, architect_id, project_name):
        sql = """INSERT INTO PandasProject(UserId, PandasArchitectId, PandasProjectName) VALUES(%s,%s,%s) RETURNING PandasProjectId;"""
        try:
            self.cur.execute(sql, (user_id, architect_id, project_name,))
            project_id = self.cur.fetchone()[0]
            self.conn.commit()
        except(Exception, psycopg2.DatabaseError) as error:
            print(error)
            return None
        return project_id

    def insert_result(self, project_id, file_id, result_name, result_count, result_finish, result_table):
        sql = """INSERT INTO PandasResult(PandasProjectId, PandasFileId, ResultName, ResultCount, ResultFinish, ResultTable) VALUES(%s,%s,%s,%s,%s,%s) RETURNING PandasResultId;"""
        try:
            self.cur.execute(sql, (project_id, file_id, result_name, result_count, result_finish, result_table,))
            result_id = self.cur.fetchone()[0]
            self.conn.commit()
        except(Exception, psycopg2.DatabaseError) as error:
            print(error)
            return None
        return result_id


    def update_result(self, result_id, project_id, file_id, result_name, result_count, result_finish, result_table):
        sql = """UPDATE PandasResult SET PandasProjectId=%s, PandasFileId=%s, ResultName=%s, ResultCount=%s, ResultFinish=%s, 
        ResultTable=%s WHERE PandasResultId=%s RETURNING PandasResultId;"""
        try:
            self.cur.execute(sql, (project_id, file_id, result_name, result_count, result_finish, result_table, result_id,))
            result_id = self.cur.fetchone()[0]
            self.conn.commit()
        except(Exception, psycopg2.DatabaseError) as error:
            print(error)
            return None
        return result_id

    def update_sentence(self, id, text, sentence_label_id, token_labels, result_id, user_id):
        sql = """UPDATE sentence SET text=%s, sentence_label=%s, token_labels=%s, PandasResultId=%s, UserId=%s WHERE id=%s RETURNING id;"""
        try:
            self.cur.execute(sql, (text, sentence_label_id, token_labels, result_id, user_id, id,))
            sentence_id = self.cur.fetchone()[0]
            self.conn.commit()
        except(Exception, psycopg2.DatabaseError) as error:
            print(error)
            return None
        return sentence_id

    def update_sentence_label(self, id, category, ordinal, type_id, main_cat_id, sub_cat_id, category_order):
        sql = """UPDATE sentence_label SET CategoryName=%s, Ordinal=%s, TypeId=%s, MainCatId=%s, SubCatId=%s, CategoryOrder=%s WHERE PandasCategoryId=%s RETURNING PandasCategoryId;"""
        try:
            self.cur.execute(sql, (category, ordinal, type_id, main_cat_id, sub_cat_id, category_order,id,))
            sentence_id = self.cur.fetchone()[0]
            self.conn.commit()
        except(Exception, psycopg2.DatabaseError) as error:
            print(error)
            return None
        return sentence_id





    def update_architect(self, id, name, active):
        sql = """UPDATE PandasArchitect SET ArchitectName = %s, ModifiedDate = CURRENT_DATE, Active = %s WHERE PandasArchitectId = %s RETURNING PandasArchitectId;"""
        try:
            self.cur.execute(sql, (name, active, id,))
            architect_id = self.cur.fetchone()[0]
            self.conn.commit()
        except(Exception, psycopg2.DatabaseError) as error:
            print(error)
            return None
        return architect_id

    def update_project(self, project_id, user_id, architect_id, project_name, active):
        sql = """UPDATE PandasProject SET UserId = %s, PandasArchitectId = %s, PandasProjectName = %s, 
        ModifyDate = CURRENT_DATE, Active = %s WHERE PandasProjectId = %s RETURNING PandasProjectId;"""
        try:
            self.cur.execute(sql, (user_id, architect_id, project_name, active, project_id,))
            project_id = self.cur.fetchone()[0]
            self.conn.commit()
        except(Exception, psycopg2.DatabaseError) as error:
            print(error)
            return None
        return project_id

    def insert_headers(self, columns, col_numbers, target_numbers, architect_id, header_row):
        try:
            subset_id = 1
            old_subset = self.get_header_subset_max_id(architect_id)
            if old_subset and old_subset[0]:
                subset_id = old_subset[0] + 1
            col_len = len(columns)
            assert col_len == len(col_numbers)
            assert col_len == len(target_numbers)
            for i, column in enumerate(columns):
                id = self.insert_one_header(column, col_numbers[i], target_numbers[i], architect_id, subset_id, header_row)
                if not id:
                    return None
        except(Exception, psycopg2.DatabaseError) as error:
            print(error)
            return None
        return subset_id

    def get_all_architect(self):
        try:
            sql = f"SELECT * FROM PandasArchitect"
            self.cur.execute(sql)
            rows = self.cur.fetchall()
            return rows
        except(Exception, psycopg2.DatabaseError) as error:
            print(error)
            return None

    def get_columns(self, project_id, result_id, architect_id):
        try:
            sql = f"SELECT * FROM PandasColumn WHERE PandasProjectId='{project_id}' AND PandasResultId='{result_id}' " \
                  f"AND PandasArchitectId='{architect_id}'"
            self.cur.execute(sql)
            rows = self.cur.fetchall()
            return rows
        except(Exception, psycopg2.DatabaseError) as error:
            print(error)
            return None


    def get_all_sentence_label(self):
        try:
            sql = f"SELECT * FROM sentence_label"
            self.cur.execute(sql)
            rows = self.cur.fetchall()
            return rows
        except(Exception, psycopg2.DatabaseError) as error:
            print(error)
            return None


    def get_projects(self, user_id):
        try:
            sql = f"SELECT * FROM PandasProject WHERE UserId='{user_id}'"
            self.cur.execute(sql)
            rows = self.cur.fetchall()
            return rows
        except(Exception, psycopg2.DatabaseError) as error:
            print(error)
            return None

    def get_results(self, project_id):
        try:
            sql = f"SELECT * FROM PandasResult WHERE PandasProjectId='{project_id}'"
            self.cur.execute(sql)
            rows = self.cur.fetchall()
            return rows
        except(Exception, psycopg2.DatabaseError) as error:
            print(error)
            return None



    def get_architect_by_name(self, name):
        try:
            sql = f"SELECT * FROM PandasArchitect WHERE ArchitectName = '{name}'"
            self.cur.execute(sql)
            row = self.cur.fetchone()
            return row
        except(Exception, psycopg2.DatabaseError) as error:
            print(error)
            return None

    def get_architect_by_id(self, id):
        try:
            sql = f"SELECT * FROM PandasArchitect WHERE PandasArchitectId ='{id}'"
            self.cur.execute(sql)
            row = self.cur.fetchone()
            return row
        except(Exception, psycopg2.DatabaseError) as error:
            print(error)
            return None

    def get_all_category(self):
        try:
            sql = f"SELECT * FROM sentence_label"
            self.cur.execute(sql)
            rows = self.cur.fetchall()
            return rows
        except(Exception, psycopg2.DatabaseError) as error:
            print(error)
            return None

    def get_headers_subset_ids(self, architect_id):
        try:
            sql = f'SELECT subset_id FROM headers WHERE architect_id={architect_id} GROUP BY subset_id'
            self.cur.execute(sql)
            rows = self.cur.fetchall()
            return rows
        except(Exception, psycopg2.DatabaseError) as error:
            print(error)
            return None


    def get_headers_by_architect_subset_id(self, architect_id, subset_id):
        try:
            sql = f"SELECT * FROM headers WHERE architect_id='{architect_id}' AND subset_id='{subset_id}'"
            self.cur.execute(sql)
            rows = self.cur.fetchall()
            return rows
        except(Exception, psycopg2.DatabaseError) as error:
            print(error)
            return None

    def delete_headers_by_architect_subset_id(self, architect_id, subset_id):
        try:
            sql = f"DELETE FROM headers WHERE architect_id='{architect_id}' AND subset_id='{subset_id}'"
            self.cur.execute(sql)
            return True
        except(Exception, psycopg2.DatabaseError) as error:
            print(error)
            return None

    def delete_column(self, pandas_column_id):
        try:
            sql = f"DELETE FROM PandasColumn WHERE PandasColumnId='{pandas_column_id}'"
            self.cur.execute(sql)
            return True
        except(Exception, psycopg2.DatabaseError) as error:
            print(error)
            return None

    def delete_all_column(self, project_id):
        try:
            sql = f"DELETE FROM PandasColumn WHERE PandasProjectId='{project_id}'"
            self.cur.execute(sql)
            return True
        except(Exception, psycopg2.DatabaseError) as error:
            print(error)
            return None

    def delete_sentence(self, id):
        try:
            sql = f"DELETE FROM sentence WHERE id='{id}'"
            self.cur.execute(sql)
            return True
        except(Exception, psycopg2.DatabaseError) as error:
            print(error)
            return None


    def delete_project(self, project_id):
        try:
            sql = f"DELETE FROM PandasProject WHERE PandasProjectId='{project_id}'"
            self.cur.execute(sql)
            return True
        except(Exception, psycopg2.DatabaseError) as error:
            print(error)
            return None

    def delete_result(self, result_id):
        try:
            sql = f"DELETE FROM PandasResult WHERE PandasResultId='{result_id}'"
            self.cur.execute(sql)
            return True
        except(Exception, psycopg2.DatabaseError) as error:
            print(error)
            return None

    def delete_all_result(self, project_id):
        try:
            sql = f"DELETE FROM PandasResult WHERE PandasProjectId='{project_id}'"
            self.cur.execute(sql)
            return True
        except(Exception, psycopg2.DatabaseError) as error:
            print(error)
            return None

    def get_headers_by_architect(self, architect_id):
        try:
            sql = f"SELECT * FROM headers WHERE architect_id='{architect_id}'"
            self.cur.execute(sql)
            rows = self.cur.fetchall()
            return rows
        except(Exception, psycopg2.DatabaseError) as error:
            print(error)
            return None

    def get_header_subset_max_id(self, architect_id):
        try:
            sql = f'SELECT MAX(subset_id) FROM headers WHERE architect_id={architect_id}'
            self.cur.execute(sql)
            row = self.cur.fetchone()
            return row
        except(Exception, psycopg2.DatabaseError) as error:
            print(error)
            return None


    def insert_one_header(self, header, col_number, target_number, architect_id, subset_id, header_row):
        sql = """INSERT INTO headers(text, column_num, target_num, architect_id, subset_id, header_row) VALUES(%s,%s,%s,%s,%s, %s) RETURNING id;"""
        try:
            self.cur.execute(sql, (header, col_number, target_number, architect_id, subset_id, header_row,))
            header_id = self.cur.fetchone()[0]
            self.conn.commit()
        except(Exception, psycopg2.DatabaseError) as error:
            print(error)
            return None
        return header_id

    def insert_sentence_label(self, name, ordinal, type_id, main_cat_id, sub_cat_id, category_order):
        sql = """INSERT INTO sentence_label(CategoryName, Ordinal, TypeId, MainCatId, SubCatId, CategoryOrder) VALUES(%s,%s,%s,%s,%s,%s) RETURNING PandasCategoryId;"""
        try:
            self.cur.execute(sql, (name,ordinal,type_id, main_cat_id, sub_cat_id, category_order,))
            category_id = self.cur.fetchone()[0]
            self.conn.commit()
        except(Exception, psycopg2.DatabaseError) as error:
            print(error)
            return None
        return category_id

    def update_sentence_label(self, category, ordinal, id):
        sql = """UPDATE sentence_label SET CategoryName = %s, Ordinal = %s, ModifiedDate = CURRENT_DATE WHERE PandasCategoryId = %s RETURNING PandasCategoryId;"""
        try:
            self.cur.execute(sql, (category, ordinal, id,))
            category_id = self.cur.fetchone()[0]
            self.conn.commit()
        except(Exception, psycopg2.DatabaseError) as error:
            print(error)
            return None
        return category_id

    def insert_sentences(self, data):
        # data: első oszlop kategória azonosító, második oszlop szöveg, 3. oszlop list of token_labels
        # TODO token_labels -t is be kell szúrni!!!
        sql = """INSERT INTO sentence(text, sentence_label_id, token_labels, PandasResultId, UserId) VALUES(%s,%s,%s) RETURNING id;"""
        ordinals = data[0]
        texts = data[1]
        token_labels = data[2]
        try:
            for i, ordinal in enumerate(ordinals):
                id, category, ordinal = self.get_sentence_label_by_ordinal(ordinal)
                if id:
                    self.cur.execute(sql, (texts[i], id, token_labels[i], ))
                    sentence_id = self.cur.fetchone()[0]
                    self.conn.commit()
                else:
                    return None
        except(Exception, psycopg2.DatabaseError) as error:
            print(error)
            return None
        return sentence_id

    def insert_token_label(self, name, category_id):
        sql = """INSERT INTO token_label("name", category_id) VALUES(%s,%s) RETURNING id;"""
        try:
            self.cur.execute(sql, (name, category_id,))
            token_label_id = self.cur.fetchone()[0]
            self.conn.commit()
        except(Exception, psycopg2.DatabaseError) as error:
            print(error)
            return None
        return token_label_id

    def update_token_label(self, name, category_id, id):
        sql = """UPDATE token_label SET "name" = %s, category_id = %s, modified_date = CURRENT_DATE WHERE id = %s RETURNING id;"""
        try:
            self.cur.execute(sql, (name, category_id, id,))
            token_label_id = self.cur.fetchone()[0]
            self.conn.commit()
        except(Exception, psycopg2.DatabaseError) as error:
            print(error)
            return None
        return token_label_id

    def get_all_categories(self):
        try:
            sql = f"SELECT * FROM sentence_label ORDER BY Ordinal"
            self.cur.execute(sql)
            rows = self.cur.fetchall()
        except(Exception, psycopg2.DatabaseError) as error:
            print(error)
            return None
        return rows

    def get_all_sentence_id(self):
        try:
            sql = f"SELECT id FROM sentence"
            self.cur.execute(sql)
            rows = self.cur.fetchall()
        except(Exception, psycopg2.DatabaseError) as error:
            print(error)
            return None
        return rows

    def get_sentence_label_by_ordinal(self, ordinal):
        try:
            sql = f"SELECT * FROM sentence_label WHERE Ordinal='{ordinal}'"
            self.cur.execute(sql)
            row = self.cur.fetchone()
            return row
        except(Exception, psycopg2.DatabaseError) as error:
            print(error)
            return None

    def __get_next_sentence__(self):
        try:
            sql = f"SELECT * FROM sentence"
            self.cur.execute(sql)
            while True:
                row = self.cur.fetchone()
                yield row
        except(Exception, psycopg2.DatabaseError) as error:
            print(error)
            return None

    def get_sentence(self, sentence_id):
        try:
            sql = f"SELECT * FROM sentence WHERE id='{sentence_id}'"
            self.cur.execute(sql)
            row = self.cur.fetchone()
            return row
        except(Exception, psycopg2.DatabaseError) as error:
            print(error)
            return None

    def get_sentence_label(self, category_id):
        try:
            sql = f"SELECT * FROM sentence_label WHERE PandasCategoryId='{category_id}'"
            self.cur.execute(sql)
            row = self.cur.fetchone()
            return row
        except(Exception, psycopg2.DatabaseError) as error:
            print(error)
            return None

    def get_token_label(self, token_id):
        try:
            sql = f"SELECT * FROM token_label WHERE id='{token_id}'"
            self.cur.execute(sql)
            row = self.cur.fetchone()
            return row
        except(Exception, psycopg2.DatabaseError) as error:
            print(error)
            return None

    def get_all_token_label(self):
        try:
            sql = f"SELECT * FROM token_label ORDER BY id"
            self.cur.execute(sql)
            rows = self.cur.fetchall()
            return rows
        except(Exception, psycopg2.DatabaseError) as error:
            print(error)
            return None