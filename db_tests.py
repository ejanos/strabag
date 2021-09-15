from db_helper import DBHelper
import psycopg2
import icecream as ic
import random
import string
from datetime import date

ic = ic.IceCreamDebugger()
# ic.disable()

# choose from all lowercase letter
letters = string.ascii_lowercase

# HEADERS = {0: ["alma", "körte", "szilva", "barack", "káposzta", "kukorica", "dinnye"],
#           }
HEADERS = {0: [
    "TSZ",
    "ÁT",
    "Rövid szöveg",
    "Hosszú szöveg",
    "TJ-menny.",
    "VÁ-menny.",
    "ME",
    "Eá",
    "FE",
    "Óra",
    "Anyag",
    "Díj",
    "15.",
    "16.",
    "17.",
    "18.",
    "Maradék",
    "TÖ",
    "FE.1"]}
COL_NUMBERS = {0: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]}
TARGET_NUMBERS = {0: [5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23]}
TEXT = {0: "Felső talajréteghumusz  eltávolítása 60 cm vastagságban (tömör m3) 101,50 - től 100,90 mBf- ig - ",
         1: "felső talajréteg elhelyezése ideiglenes depóniában a területen",
         2: "Ideiglenes talaj depónia kezelése",
         3: "Humusz terítése a területen 40 cm vastagságban"}
TEXT2 = {0: "Felső talajréjhgfjgfteghumusz  eltávolítása 60 cm vastagságban (tömör m3) 101,50 - től 100,90 mBf- ig - ",
         1: "felső talajuztrutrréteg elhelyezése ideiglenes depóniában a területen",
         2: "Ideiuztrutrglenes talaj depónia kezelése",
         3: "Humusz teríuztruztrtése a területen 40 cm vastagságban"}

CATEGORY = {0: "Földmunka",
            1: "Betonozás",
            2: "Vasútépítés",
            3: "Magasépítés"}
CATEGORY2 = {0: "Tetőszerelés",
             1: "Villanyszerelés",
             2: "Útépítés",
             3: "Aszfeltozás"}
ORDINAL = {0: "02.01.",
           1: "03.02.",
           2: "04.01.",
           3: "05.01."}
ORDINAL2 = {0: "11.01.",
            1: "12.02.",
            2: "13.01.",
            3: "14.01."}


def get_password():
    with open("./password.txt", 'r', encoding='utf-8') as f:
        return f.read()

def initialize():
    password = get_password()
    # drop test database and create database
    conn = psycopg2.connect(
        host="localhost",
        database="train_excel_test",
        user="postgres",
        password=password)

    cur = conn.cursor()
    with open("create_test_db.sql", 'r') as f:
        sql = f.read()
    cur.execute(sql)
    conn.commit()
    conn.close()
    with DBHelper(test=True) as db:
        for key, sentence_label in ORDINAL2.items():
            db.insert_sentence_label(CATEGORY2[key], sentence_label)

def get_sentence_label_by_ordinal_test():
    with DBHelper(test=True) as db:
        label1 = get_random_string(15)
        label2 = get_random_string(15)
        ordinal1 = random.randint(0, 9999)
        category_id1 = db.insert_sentence_label(label1, str(ordinal1))
        ordinal2 = random.randint(0, 9999)
        category_id2 = db.insert_sentence_label(label2, str(ordinal2))
        sentence_label = db.get_sentence_label_by_ordinal(ordinal1)
        assert sentence_label[2] == str(ordinal1)


def get_all_token_labels_test():
    with DBHelper(test=True) as db:
        label1 = get_random_string(15)
        label2 = get_random_string(15)
        sen_label1 = get_random_string(15)
        sen_label2 = get_random_string(15)
        ordinal1 = random.randint(0, 9999)
        category_id1 = db.insert_sentence_label(sen_label1, str(ordinal1))
        ordinal2 = random.randint(0, 9999)
        category_id2 = db.insert_sentence_label(sen_label2, str(ordinal2))
        token_id1 = db.insert_token_label(label1, category_id1)
        token_id2 = db.insert_token_label(label2, category_id2)
        token_labels = db.get_all_token_label()
        assert len(token_labels) > 1
        for label in token_labels:
            if label[0] == token_id1:
                assert label[1] == label1
            if label[0] == token_id2:
                assert label[1] == label2


def get_all_categories_test():
    with DBHelper(test=True) as db:
        ordinal1 = random.randint(0, 9999)
        label1 = get_random_string(15)
        label2 = get_random_string(15)
        category_id1 = db.insert_sentence_label(label1, str(ordinal1))
        ordinal2 = random.randint(0, 9999)
        category_id2 = db.insert_sentence_label(label2, str(ordinal2))
        categories = db.get_all_categories()
        assert len(categories) > 1
        for category in categories:
            if category[0] == category_id1:
                assert category[2] == str(ordinal1)
            if category[0] == category_id2:
                assert category[2] == str(ordinal2)


def insert_token_label_test():
    with DBHelper(test=True) as db:
        sen_label = get_random_string(15)
        token_label = get_random_string(15)
        category = get_random_string(15)
        category_id = db.insert_sentence_label(category, sen_label)
        token_label_id = db.insert_token_label(token_label, category_id)
        assert token_label_id > 0

def update_token_label_test():
    with DBHelper(test=True) as db:
        sen_label = get_random_string(15)
        token_label = get_random_string(15)
        category = get_random_string(15)
        category_id = db.insert_sentence_label(category, sen_label)
        token_label_id = db.insert_token_label(token_label, category_id)
        updated_token_label_id = db.update_token_label("akarmi", category_id, token_label_id)
        assert token_label_id == updated_token_label_id
        row = db.get_token_label(updated_token_label_id)
        assert row[0] == updated_token_label_id
        assert row[1] == "akarmi"
        assert row[2] == category_id
        assert row[3] == date.today()
        assert row[4] == date.today()



def insert_sentences_test():
    with DBHelper(test=True) as db:
        for key, sentence_label in ORDINAL.items():
            db.insert_sentence_label(CATEGORY[key], sentence_label)
        ord = [ORDINAL[x] for x in range(4)]
        text = [TEXT[x] for x in range(4)]
        token_labels_len = []
        for key, value in TEXT.items():
            token_labels_len.append(len(value))

        token_labels = generate_token_labels(token_labels_len)
        data = [ord, text, token_labels]
        sentence_id = db.insert_sentences(data)
        assert sentence_id >= 1


def generate_token_labels(token_labels_len):
    with DBHelper(test=True) as db:
        token_labels = []
        token_list = []
        for x in token_labels_len:
            for y in range(x):
                if random.randint(0, 4) == 0:
                    token_list.append(random.randint(0, len(ORDINAL) - 1))
                else:
                    token_list.append(0)
            token_labels.append(token_list)
        return token_labels

def insert_sentence_label_test():
    with DBHelper(test=True) as db:
        category_id = db.insert_sentence_label(CATEGORY[0], ORDINAL[0])
        assert category_id >= 1

def update_sentence_label_test():
    with DBHelper(test=True) as db:
        category_id = db.insert_sentence_label(CATEGORY[0], ORDINAL[0])
        updated_id = db.update_sentence_label("akarmi", "09.09.", category_id)
        assert category_id == updated_id
        sentence_label_row = db.get_sentence_label(updated_id)
        assert sentence_label_row[1] == "akarmi"
        assert sentence_label_row[2] == "09.09."

def insert_one_header_test():
    with DBHelper(test=True) as db:
        header = get_random_string(15)
        architectname = get_random_string(15)
        architect_id = db.insert_architect(architectname)
        header_id = db.insert_one_header(header, 1, 3, architect_id, 1, 1)
        assert header_id > 0


def get_header_subset_max_id_test():
    with DBHelper(test=True) as db:
        architectname = get_random_string(15)
        architect_id = db.insert_architect(architectname)
        insert_headers_by_architect_id(architect_id)
        insert_headers_by_architect_id(architect_id)
        max_id = db.get_header_subset_max_id(architect_id)
        assert max_id[0] >= 2


def get_headers_by_architect_test():
    with DBHelper(test=True) as db:
        architectname = get_random_string(15)
        architect_id = db.insert_architect(architectname)
        insert_headers_by_architect_id(architect_id)
        headers = db.get_headers_by_architect(architect_id)
        for i, header in enumerate(headers):
            assert header[1] == HEADERS[0][i]


def get_headers_by_architect_subset_id_test():
    with DBHelper(test=True) as db:
        architectname = get_random_string(15)
        architect_id = db.insert_architect(architectname)
        insert_headers_by_architect_id(architect_id)
        insert_headers_by_architect_id(architect_id)
        headers = db.get_headers_by_architect_subset_id(architect_id, 2)
        for i, header in enumerate(headers):
            assert header[1] == HEADERS[0][i]


def get_headers_subset_ids_test():
    with DBHelper(test=True) as db:
        architectname = get_random_string(15)
        architect_id = db.insert_architect(architectname)
        insert_headers_by_architect_id(architect_id)
        insert_headers_by_architect_id(architect_id)
        subset_ids = db.get_headers_subset_ids(architect_id)
        assert subset_ids == [(1,), (2,)]


def get_architect_by_name_test():
    with DBHelper(test=True) as db:
        architectname = get_random_string(15)
        architect_id = db.insert_architect(architectname)
        row = db.get_architect_by_name(architectname)
        assert architect_id > 0
        assert row[1] == architectname

def get_architect_by_id_test():
    with DBHelper(test=True) as db:
        architectname = get_random_string(15)
        architect_id = db.insert_architect(architectname)
        row = db.get_architect_by_id(architect_id)
        assert row[0] == architect_id
        assert row[1] == architectname
        assert row[2] == date.today()
        assert row[3] == date.today()
        assert row[4]

def get_all_architect_test():
    with DBHelper(test=True) as db:
        architectname1 = get_random_string(15)
        architectname2 = get_random_string(15)
        db.insert_architect(architectname1)
        db.insert_architect(architectname2)
        architects = db.get_all_architect()
        assert len(architects) >= 2


def insert_architect_test():
    with DBHelper(test=True) as db:
        architectname = get_random_string(15)
        architect_id = db.insert_architect(architectname)
        assert architect_id > 0

def update_architect_test():
    with DBHelper(test=True) as db:
        architectname = get_random_string(15)
        architect_id = db.insert_architect(architectname)
        architectname = get_random_string(15)
        architect_updated_id = db.update_architect(architect_id, architectname, True)
        assert architect_id == architect_updated_id
        row = db.get_architect_by_id(architect_id)
        assert row[1] == architectname

def insert_headers_test():
    with DBHelper(test=True) as db:
        header = HEADERS[0]
        col_number = COL_NUMBERS[0]
        target_number = TARGET_NUMBERS[0]
        architectname = get_random_string(15)
        architect_id = db.insert_architect(architectname)
        column_id = db.insert_headers(header, col_number, target_number, architect_id, 1)
        assert column_id == True


def insert_headers_by_architect_id(architect_id):
    with DBHelper(test=True) as db:
        header = HEADERS[0]
        col_number = COL_NUMBERS[0]
        target_number = TARGET_NUMBERS[0]
        subset_id = db.insert_headers(header, col_number, target_number, architect_id, 1)
        assert subset_id >= 1


def insert_headers_architect_id_1_test():
    with DBHelper(test=True) as db:
        header = HEADERS[0]
        col_number = COL_NUMBERS[0]
        target_number = TARGET_NUMBERS[0]
        architectname = get_random_string(15)
        architect_id = db.insert_architect(architectname)
        subset_id = db.insert_headers(header, col_number, target_number, architect_id, 1)
        assert subset_id >= 1


def insert_sentences():
    with DBHelper(test=True) as db:
        ord = [ORDINAL2[x] for x in range(4)]
        text = [TEXT2[x] for x in range(4)]
        token_labels_len = []
        for key, value in TEXT2.items():
            token_labels_len.append(len(value))
        token_labels = generate_token_labels(token_labels_len)
        data = [ord, text, token_labels]
        sentence_id = db.insert_sentences(data)
        return sentence_id

def get_next_sentence_test():
    with DBHelper(test=True) as db:
        row = db.get_sentence(1)
        if not row:
            insert_sentences()
        count = 0
        for row in db.__get_next_sentence__():
            if not row:
                break
            count += 1
        db.close_connection()
        assert count == 4

def get_sentence_test():
    with DBHelper(test=True) as db:
        row = db.get_sentence(1)
        if not row:
            insert_sentences()
        row = db.get_sentence(1)
        assert len(row[0]) >= 10

def get_sentence_label_test():
    with DBHelper(test=True) as db:
        row = db.get_sentence(1)
        if not row:
            insert_sentences()
        sentence_label_row = db.get_sentence_label(1)
        assert sentence_label_row[1] == "Tetőszerelés"

def get_token_label_test():
    with DBHelper(test=True) as db:
        category = get_random_string(15)
        ordinal = get_random_ordinal()
        category_id = db.insert_sentence_label(category, ordinal)
        name = get_random_string(15)
        token_id = db.insert_token_label(name, category_id)
        row = db.get_token_label(token_id)
        assert row[0] == token_id
        assert row[1] == name
        assert row[2] == category_id
        assert row[3] == date.today()
        assert row[4] == date.today()

def get_all_token_label_test():
    with DBHelper(test=True) as db:
        rows1 = db.get_all_token_label()
        get_token_label_test()
        get_token_label_test()
        rows2 = db.get_all_token_label()
        assert len(rows2) - len(rows1) == 2

def get_random_string(length):
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str

def get_random_ordinal():
    num1 = random.randint(15, 99)
    num2 = random.randint(15, 99)
    return str(num1) + "." + str(num2) + "."


initialize()
get_architect_by_id_test()
print("Test get architect by id test")
update_token_label_test()
print("Test update token label test is OK!")
get_architect_by_name_test()
print("Test get architect by name is OK")
update_sentence_label_test()
print("Test update sentence label test is OK!")
update_architect_test()
print("Test update architect is OK!")
get_all_token_label_test()
print("Test get all token label test is OK!")
get_token_label_test()
print("Test get token label is OK!")
get_sentence_label_test()
print("Test get sentence label test is OK")
get_sentence_test()
print("Test get sentence test is OK")
get_next_sentence_test()
print("Test get next sentence test is OK")
get_sentence_label_by_ordinal_test()
print("Test get all sentence labels is OK")
get_all_token_labels_test()
print("Test get all token labels is OK")
get_all_categories_test()
print("Test get all categories is OK")
insert_token_label_test()
print("Test insert token label is OK")
insert_sentences_test()
print("Test insert sentences is OK")
insert_sentence_label_test
print("Test insert sentence label is OK")
insert_one_header_test()
print("Test insert one header is OK")
get_header_subset_max_id_test()
print("Test get headers subset max id is OK")
get_headers_by_architect_test()
print("Test get headers by architect id is OK")
get_headers_by_architect_subset_id_test()
print("Test get headers by architect subset id is OK")
get_headers_subset_ids_test()
print("Test get headers subset ids is OK")
get_all_architect_test()
print("Test get all architect is OK")
insert_architect_test()
print("Test insert architect is OK")
insert_headers_architect_id_1_test()
print("Test insert headers architect id=1 is OK'")
insert_headers_test()
print("Test insert headers is OK'")
