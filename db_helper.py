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

    def insert_sentence_label(self, category, ordinal):
        sql = """INSERT INTO sentence_label(CategoryName, Ordinal) VALUES(%s,%s) RETURNING PandasCategoryId;"""
        try:
            self.cur.execute(sql, (category, ordinal,))
            sentence_label_id = self.cur.fetchone()[0]
            self.conn.commit()
        except(Exception, psycopg2.DatabaseError) as error:
            print(error)
            return None
        return sentence_label_id


    def insert_sentence(self, text, sentence_label_id, token_labels):
        sql = """INSERT INTO sentence(text, sentence_label_id, token_labels) VALUES(%s,%s,%s) RETURNING id;"""
        try:
            self.cur.execute(sql, (text, sentence_label_id, token_labels))
            sentence_id = self.cur.fetchone()[0]
            self.conn.commit()
        except(Exception, psycopg2.DatabaseError) as error:
            print(error)
            return None
        return sentence_id


    def update_sentence(self, id, text, sentence_label_id, token_labels):
        sql = """UPDATE sentence SET text=%s, sentence_label_id=%s, token_labels=%s WHERE id=%s RETURNING id;"""
        try:
            self.cur.execute(sql, (text, sentence_label_id, token_labels, id,))
            sentence_id = self.cur.fetchone()[0]
            self.conn.commit()
        except(Exception, psycopg2.DatabaseError) as error:
            print(error)
            return None
        return sentence_id

    def update_sentence_label(self, id, category, ordinal):
        sql = """UPDATE sentence_label SET CategoryName=%s, Ordinal=%s WHERE PandasCategoryId=%s RETURNING PandasCategoryId;"""
        try:
            self.cur.execute(sql, (category, ordinal,))
            sentence_id = self.cur.fetchone()[0]
            self.conn.commit()
        except(Exception, psycopg2.DatabaseError) as error:
            print(error)
            return None
        return sentence_id


    def update_architect(self, id, name, active):
        sql = """UPDATE PandasArchitect SET ArchitectName = %s, ModifyDate = CURRENT_DATE, Active = %s WHERE PandasArchitectId = %s RETURNING PandasArchitectId;"""
        try:
            self.cur.execute(sql, (name, active, id,))
            architect_id = self.cur.fetchone()[0]
            self.conn.commit()
        except(Exception, psycopg2.DatabaseError) as error:
            print(error)
            return None
        return architect_id

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
            sql = f"SELECT * FROM PandasArchitect WHERE Active = true ORDER BY ArchitectName ASC"
            self.cur.execute(sql)
            rows = self.cur.fetchall()
            return rows
        except(Exception, psycopg2.DatabaseError) as error:
            print(error)
            return None

    def get_project_trained(self, project_id):
        try:
            sql = f"SELECT Trained FROM TrainedProjects WHERE  TrainedProjectId={project_id}"
            self.cur.execute(sql)
            is_trained = self.cur.fetchone()[0]
            return is_trained
        except(Exception, psycopg2.DatabaseError) as error:
            print(error)
            return None

    def insert_project(self, project_id, trained):
        sql = """INSERT INTO TrainedProjects(TrainedProjectId, Trained) VALUES(%s, %s) RETURNING TrainedProjectId;"""
        try:
            self.cur.execute(sql, (project_id, trained,))
            project_id = self.cur.fetchone()[0]
            self.conn.commit()
        except(Exception, psycopg2.DatabaseError) as error:
            print(error)
            return None
        return project_id

    def update_project(self, project_id, trained):
        sql = """UPDATE TrainedProjects SET Trained=%s WHERE TrainedProjectId=%s RETURNING TrainedProjectId;"""
        try:
            self.cur.execute(sql, (trained, project_id,))
            project_id = self.cur.fetchone()[0]
            self.conn.commit()
        except(Exception, psycopg2.DatabaseError) as error:
            print(error)
            return None
        return project_id


    def get_all_sentence_label(self):
        try:
            sql = f"SELECT * FROM sentence_label"
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
            sql = f"SELECT * FROM PandasArchitect WHERE PandasArchitectId ={id}"
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

    def get_category_id_by_ordinal(self, ordinal):
        try:
            sql = f"SELECT pandascategoryid FROM sentence_label WHERE ordinal='{ordinal}'"
            self.cur.execute(sql)
            category_id = self.cur.fetchone()[0]
            return category_id
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
            sql = f"SELECT * FROM headers WHERE architect_id={architect_id} AND subset_id={subset_id}"
            self.cur.execute(sql)
            rows = self.cur.fetchall()
            return rows
        except(Exception, psycopg2.DatabaseError) as error:
            print(error)
            return None

    def delete_headers_by_architect_subset_id(self, architect_id, subset_id):
        try:
            sql = f"DELETE FROM headers WHERE architect_id={architect_id} AND subset_id={subset_id}"
            self.cur.execute(sql)
            return True
        except(Exception, psycopg2.DatabaseError) as error:
            print(error)
            return None

    def delete_sentence(self, id):
        try:
            sql = f"DELETE FROM sentence WHERE id={id}"
            self.cur.execute(sql)
            return True
        except(Exception, psycopg2.DatabaseError) as error:
            print(error)
            return None



    def get_headers_by_architect(self, architect_id):
        try:
            sql = f"SELECT * FROM headers WHERE architect_id={architect_id}"
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

    def insert_sentence_label(self, name, ordinal):
        sql = """INSERT INTO sentence_label(CategoryName, Ordinal) VALUES(%s,%s) RETURNING PandasCategoryId;"""
        try:
            self.cur.execute(sql, (name,ordinal,))
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
        sql = """INSERT INTO sentence(text, sentence_label_id, token_labels) VALUES(%s,%s,%s) RETURNING id;"""
        ordinals = data[0]
        texts = data[1]
        token_labels = data[2]
        try:
            for i, ordinal in enumerate(ordinals):
                id, category, ordinal, created_date, modified_date = self.get_sentence_label_by_ordinal(ordinal)
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

    def insert_token_label(self, frontend_id, name, category_ordinal):
        sql = """INSERT INTO token_label(frontend_id, "name", category_id) VALUES(%s, %s,%s) RETURNING id;"""
        try:
            category_id = self.get_category_id_by_ordinal(category_ordinal)
            self.cur.execute(sql, (frontend_id, name, category_id,))
            token_label_id = self.cur.fetchone()[0]
            self.conn.commit()
        except(Exception, psycopg2.DatabaseError) as error:
            print(error)
            return None
        return token_label_id

    def update_token_label(self, name, category_ordinal, frontend_id):
        sql = """UPDATE token_label SET "name" = %s, category_id = %s, modified_date = CURRENT_DATE WHERE frontend_id = %s RETURNING id;"""
        try:
            category_id = self.get_category_id_by_ordinal(category_ordinal)
            self.cur.execute(sql, (name, category_id, frontend_id,))
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

    def get_sentence_label_id_by_ordinal(self, ordinal):
        try:
            sql = f"SELECT PandasCategoryId FROM sentence_label WHERE Ordinal='{ordinal}'"
            self.cur.execute(sql)
            category_id = self.cur.fetchone()[0]
            return category_id
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
            sql = f"SELECT * FROM sentence WHERE id={sentence_id}"
            self.cur.execute(sql)
            row = self.cur.fetchone()
            return row
        except(Exception, psycopg2.DatabaseError) as error:
            print(error)
            return None

    def get_sentence_id_by_text(self, text):
        try:
            sql = f"SELECT id FROM sentence WHERE text='{text}'"
            self.cur.execute(sql)
            row = self.cur.fetchone()
            return row
        except(Exception, psycopg2.DatabaseError) as error:
            print(error)
            return None

    def get_sentence_label(self, category_id):
        try:
            sql = f"SELECT * FROM sentence_label WHERE PandasCategoryId={category_id}"
            self.cur.execute(sql)
            row = self.cur.fetchone()
            return row
        except(Exception, psycopg2.DatabaseError) as error:
            print(error)
            return None

    def get_token_label(self, token_id):
        try:
            sql = f"SELECT * FROM token_label WHERE id={token_id}"
            self.cur.execute(sql)
            row = self.cur.fetchone()
            return row
        except(Exception, psycopg2.DatabaseError) as error:
            print(error)
            return None

    def get_all_token_label(self):
        try:
            sql = f"SELECT * FROM token_label"
            self.cur.execute(sql)
            rows = self.cur.fetchall()
            return rows
        except(Exception, psycopg2.DatabaseError) as error:
            print(error)
            return None

        def get_all_token_label_frontend_ids(self):
            try:
                sql = f"SELECT frontend_id FROM token_label"
                self.cur.execute(sql)
                rows = self.cur.fetchall()
                return rows
            except(Exception, psycopg2.DatabaseError) as error:
                print(error)
                return None