import psycopg2


class DBHelper():
    conn = psycopg2.connect(
        host="localhost",
        database="train_excel",
        user="postgres",
        password="@JbhNA;g.qW3S-8H")

    def insert_row(self):
        pass

