import psycopg2


class DBHelper():
    conn = psycopg2.connect(
        host="localhost",
        database="train_excel",
        user="postgres",
        password="@JbhNA;g.qW3S-8H")

    cur = conn.cursor()

    def insert_user(self, name):
        sql = """INSERT INTO users(name) VALUES(%s) RETURNING id;"""
        try:
            self.cur.execute(sql, (name,))
            user_id = self.cur.fetchone()[0]
            self.conn.commit()
        except(Exception, psycopg2.DatabaseError) as error:
            print(error)
            return None
        return user_id

    def insert_columns(self, columns, col_numbers, target_numbers, user_id):
        col_len = len(columns)
        assert col_len == len(col_numbers)
        assert col_len == target_numbers
        for i, column in enumerate(columns):
            id = self.insert_one_column(column, col_numbers[i], target_numbers[i], user_id)
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

    def get_columns_by_user(self, user_id):
        try:
            sql = f"SELECT * FROM columns WHERE user_id='{user_id}'"
            self.cur.execute(sql)
            rows = self.cur.fetchall()
            return rows
        except(Exception, psycopg2.DatabaseError) as error:
            print(error)
            return None


    def insert_one_column(self, column, col_number, target_number, user_id):
        sql = """INSERT INTO columns(text, column, target, user_id) VALUES(%s) RETURNING id;"""
        try:
            self.cur.execute(sql, (column, col_number, target_number, user_id,))
            column_id = self.cur.fetchone()[0]
            self.conn.commit()
        except(Exception, psycopg2.DatabaseError) as error:
            print(error)
            return None
        return column_id

    def insert_sentence_label(self, name, ordinal):
        sql = """INSERT INTO sentence_label(category, ordinal) VALUES(%s) RETURNING id;"""
        try:
            self.cur.execute(sql, (name,ordinal,))
            category_id = self.cur.fetchone()[0]
            self.conn.commit()
        except(Exception, psycopg2.DatabaseError) as error:
            print(error)
            return None
        return category_id

    def insert_token_label(self, name, category_id):
        sql = """INSERT INTO token_label(name, category_id) VALUES(%s) RETURNING id;"""
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

    def get_sentence_label_by_ordinal(self, ordinal):
        try:
            sql = f"SELECT * FROM sentence_label WHERE ordinal='{ordinal}'"
            self.cur.execute(sql)
            row = self.cur.fetchone()
            return row
        except(Exception, psycopg2.DatabaseError) as error:
            print(error)
            return None

    def save_sentences(self, data):
        # data: első oszlop sorszám, második oszlop szöveg
        # TODO token_labels -t is be kell szúrni!!!
        sql = """INSERT INTO sentence(text, label) VALUES(%s) RETURNING id;"""
        try:
            for row in data:
                ordinal = row[0]
                text = row[1]
                id, category, ordinal = self.get_sentence_label_by_ordinal(ordinal)
                if id:
                    self.cur.execute(sql, (text, id,))
                    sentence_id = self.cur.fetchone()[0]
                    self.conn.commit()
                else:
                    return None
        except(Exception, psycopg2.DatabaseError) as error:
            print(error)
            return None
        return sentence_id












