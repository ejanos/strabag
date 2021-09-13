import psycopg2
import icecream as ic
from contextlib import contextmanager

ic = ic.IceCreamDebugger()
ic.disable()

HOST = "localhost"
TRAIN_EXCEL_TEST = "train_excel_test"
TRAIN_EXCEL = "train_excel"
USER = "postgres"

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


    def get_password(self):
        with open("./password.txt", 'r', encoding='utf-8') as f:
            self.password = f.read()

    def connect(self):
        if not self.password:
            self.get_password()
        if not self.cur:
            if self.test:
                self.conn = psycopg2.connect(
                    host=HOST,
                    database=TRAIN_EXCEL_TEST,
                    user=USER,
                    password=self.password)
            else:
                self.conn = psycopg2.connect(
                    host=HOST,
                    database=TRAIN_EXCEL,
                    user=USER,
                    password=self.password)
            self.cur = self.conn.cursor()

    def close_connection(self):
        self.conn.close()
        self.cur = None

    def insert_architect(self, name):
        sql = """INSERT INTO architects("name") VALUES(%s) RETURNING id;"""
        try:
            self.cur.execute(sql, (name,))
            architect_id = self.cur.fetchone()[0]
            self.conn.commit()
        except(Exception, psycopg2.DatabaseError) as error:
            print(error)
            return None
        return architect_id

    def update_architect(self, id, name, active):
        sql = """UPDATE architects SET "name" = %s, modified_date = CURRENT_DATE, active = %s WHERE id = %s RETURNING id;"""
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
            sql = f"SELECT * FROM architects ORDER BY id"
            self.cur.execute(sql)
            rows = self.cur.fetchall()
            return rows
        except(Exception, psycopg2.DatabaseError) as error:
            print(error)
            return None

    def get_architect_by_name(self, name):
        try:
            sql = f"SELECT * FROM architects WHERE name='{name}'"
            self.cur.execute(sql)
            row = self.cur.fetchone()
            return row
        except(Exception, psycopg2.DatabaseError) as error:
            print(error)
            return None

    def get_architect_by_id(self, id):
        try:
            sql = f"SELECT * FROM architects WHERE id='{id}'"
            self.cur.execute(sql)
            row = self.cur.fetchone()
            return row
        except(Exception, psycopg2.DatabaseError) as error:
            print(error)
            return None

    def get_all_category(self):
        try:
            sql = f"SELECT * FROM sentence_label ORDER BY id"
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

    def insert_sentence_label(self, name, ordinal):
        sql = """INSERT INTO sentence_label(category, ordinal) VALUES(%s,%s) RETURNING id;"""
        try:
            self.cur.execute(sql, (name,ordinal,))
            category_id = self.cur.fetchone()[0]
            self.conn.commit()
        except(Exception, psycopg2.DatabaseError) as error:
            print(error)
            return None
        return category_id

    def update_sentence_label(self, category, ordinal, id):
        sql = """UPDATE sentence_label SET category = %s, ordinal = %s, modified_date = CURRENT_DATE WHERE id = %s RETURNING id;"""
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
        sql = """INSERT INTO sentence(text, label, token_labels) VALUES(%s,%s,%s) RETURNING id;"""
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
            sql = f"SELECT * FROM sentence_label ORDER BY ordinal"
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
            sql = f"SELECT id, category, ordinal FROM sentence_label WHERE ordinal='{ordinal}'"
            self.cur.execute(sql)
            row = self.cur.fetchone()
            return row
        except(Exception, psycopg2.DatabaseError) as error:
            print(error)
            return None

    def __get_next_sentence__(self):
        try:
            sql = f"SELECT text, label, token_labels FROM sentence"
            self.cur.execute(sql)
            while True:
                row = self.cur.fetchone()
                yield row
        except(Exception, psycopg2.DatabaseError) as error:
            print(error)
            return None

    def get_sentence(self, sentence_id):
        try:
            sql = f"SELECT text, label, token_labels FROM sentence WHERE id='{sentence_id}'"
            self.cur.execute(sql)
            row = self.cur.fetchone()
            return row
        except(Exception, psycopg2.DatabaseError) as error:
            print(error)
            return None

    def get_sentence_label(self, category_id):
        try:
            sql = f"SELECT * FROM sentence_label WHERE id='{category_id}'"
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
