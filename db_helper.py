import psycopg2
import icecream as ic

ic = ic.IceCreamDebugger()
#ic.disable()


class DBHelper():

    def __init__(self, test=False):
        self.test = test
        if test:
            self.conn = psycopg2.connect(
                host="localhost",
                database="train_excel_test",
                user="postgres",
                password="@JbhNA;g.qW3S-8H")
        else:
            self.conn = psycopg2.connect(
                host="localhost",
                database="train_excel",
                user="postgres",
                password="@JbhNA;g.qW3S-8H")

        self.cur = self.conn.cursor()

    def insert_user(self, name):
        sql = """INSERT INTO users("name") VALUES(%s) RETURNING id;"""
        try:
            self.cur.execute(sql, (name,))
            user_id = self.cur.fetchone()[0]
            self.conn.commit()
        except(Exception, psycopg2.DatabaseError) as error:
            print(error)
            return None
        return user_id

    def insert_headers(self, columns, col_numbers, target_numbers, user_id):
        subset_id = 1
        old_subset = self.get_header_subset_max_id(user_id)
        if old_subset[0]:
            subset_id = old_subset[0] + 1
        col_len = len(columns)
        assert col_len == len(col_numbers)
        assert col_len == len(target_numbers)
        for i, column in enumerate(columns):
            id = self.insert_one_header(column, col_numbers[i], target_numbers[i], user_id, subset_id)
            if not id:
                return None
        return True

    def get_all_user(self):
        try:
            sql = f"SELECT * FROM users ORDER BY id"
            self.cur.execute(sql)
            rows = self.cur.fetchall()
            return rows
        except(Exception, psycopg2.DatabaseError) as error:
            print(error)
            return None

    def get_user_by_name(self, name):
        try:
            sql = f"SELECT * FROM users WHERE name='{name}'"
            self.cur.execute(sql)
            row = self.cur.fetchone()
            return row
        except(Exception, psycopg2.DatabaseError) as error:
            print(error)
            return None

    def get_headers_subset_ids(self, user_id):
        try:
            sql = f'SELECT subset_id FROM headers WHERE user_id={user_id} GROUP BY subset_id'
            self.cur.execute(sql)
            rows = self.cur.fetchall()
            return rows
        except(Exception, psycopg2.DatabaseError) as error:
            print(error)
            return None


    def get_headers_by_user_subset_id(self, user_id, subset_id):
        try:
            sql = f"SELECT * FROM headers WHERE user_id='{user_id}' AND subset_id='{subset_id}'"
            self.cur.execute(sql)
            rows = self.cur.fetchall()
            return rows
        except(Exception, psycopg2.DatabaseError) as error:
            print(error)
            return None

    def get_headers_by_user(self, user_id):
        try:
            sql = f"SELECT * FROM headers WHERE user_id='{user_id}'"
            self.cur.execute(sql)
            rows = self.cur.fetchall()
            return rows
        except(Exception, psycopg2.DatabaseError) as error:
            print(error)
            return None

    def get_header_subset_max_id(self, user_id):
        try:
            sql = f'SELECT MAX(subset_id) FROM headers WHERE user_id={user_id}'
            self.cur.execute(sql)
            row = self.cur.fetchone()
            return row
        except(Exception, psycopg2.DatabaseError) as error:
            print(error)
            return None


    def insert_one_header(self, header, col_number, target_number, user_id, subset_id):
        sql = """INSERT INTO headers(text, column_num, target_num, user_id, subset_id) VALUES(%s,%s,%s,%s,%s) RETURNING id;"""
        try:
            self.cur.execute(sql, (header, col_number, target_number, user_id, subset_id,))
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

    def insert_sentences(self, data):
        # data: első oszlop sorszám, második oszlop szöveg, 3. oszlop list of token_labels
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

    def get_all_categories(self):
        try:
            sql = f"SELECT * FROM sentence_label ORDER BY ordinal"
            self.cur.execute(sql)
            rows = self.cur.fetchall()
        except(Exception, psycopg2.DatabaseError) as error:
            print(error)
            return None
        return rows

    def get_all_token_labels(self):
        try:
            sql = f"SELECT * FROM token_label"
            self.cur.execute(sql)
            rows = self.cur.fetchall()
        except(Exception, psycopg2.DatabaseError) as error:
            print(error)
            return None
        return rows


    def get_sentence_label_by_ordinal(self, ordinal):
        try:
            sql = f"SELECT * FROM sentence_label WHERE ordinal='{ordinal}'"
            self.cur.execute(sql)
            row = self.cur.fetchone()
            return row
        except(Exception, psycopg2.DatabaseError) as error:
            print(error)
            return None













