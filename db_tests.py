from db_helper import DBHelper
import psycopg2
import icecream as ic
import random
import string

ic = ic.IceCreamDebugger()
#ic.disable()

# choose from all lowercase letter
letters = string.ascii_lowercase
db = DBHelper(test=True)

HEADERS = {0: ["alma", "körte", "szilva", "barack"],
           }
COL_NUMBERS = {0: [1, 2, 3, 4]}
TARGET_NUMBERS = {0: [5, 6, 7, 8]}
TEXT = {0: "Felső talajréteghumusz  eltávolítása 60 cm vastagságban (tömör m3) 101,50 - től 100,90 mBf- ig - ",
        1: "felső talajréteg elhelyezése ideiglenes depóniában a területen",
        2: "Ideiglenes talaj depónia kezelése",
        3: "Humusz terítése a területen 40 cm vastagságban"}
CATEGORY = {0: "Földmunka",
            1: "Betonozás",
            2: "Vasútépítés",
            3: "Magasépítés"}
ORDINAL = {0: "02.01.",
           1: "03.02.",
           2: "04.01.",
           3: "05.01."}

def initialize():
    conn = psycopg2.connect(
        host="localhost",
        database="train_excel_test",
        user="postgres",
        password="@JbhNA;g.qW3S-8H")

    cur = conn.cursor()
    with open("create_test_db.sql", 'r') as f:
        sql = f.read()
    cur.execute(sql)
    conn.commit()
    conn.close()

def get_sentence_label_by_ordinal_test():
    label1 = "twrjghfewz"
    label2 = "bvciuztxgfd"
    ordinal1 = random.randint(0, 9999)
    category_id1 = db.insert_sentence_label(label1, str(ordinal1))
    ordinal2 = random.randint(0, 9999)
    category_id2 = db.insert_sentence_label(label2, str(ordinal2))
    sentence_label = db.get_sentence_label_by_ordinal(ordinal1)
    assert sentence_label[2] == str(ordinal1)

def get_all_token_labels_test():
    label1 = "kjhguzjhgjmnbv"
    label2 = "kjhertetxycvdguzjhgjmnbv"
    ordinal1 = random.randint(0, 9999)
    category_id1 = db.insert_sentence_label("nbvcbvc", str(ordinal1))
    ordinal2 = random.randint(0, 9999)
    category_id2 = db.insert_sentence_label("iuztkjhg", str(ordinal2))
    token_id1 = db.insert_token_label(label1, category_id1)
    token_id2 = db.insert_token_label(label2, category_id2)
    token_labels = db.get_all_token_labels()
    assert len(token_labels) > 1
    for label in token_labels:
        if label[0] == token_id1:
            assert label[1] == label1
        if label[0] == token_id2:
            assert label[1] == label2

def get_all_categories_test():
    ordinal1 = random.randint(0, 9999)
    category_id1 = db.insert_sentence_label("trewtrew", str(ordinal1))
    ordinal2 = random.randint(0, 9999)
    category_id2 = db.insert_sentence_label("uztruztr", str(ordinal2))
    categories = db.get_all_categories()
    assert len(categories) > 1
    for category in categories:
        if category[0] == category_id1:
            assert category[2] == str(ordinal1)
        if category[0] == category_id2:
            assert category[2] == str(ordinal2)

def insert_token_label_test():
    rnd = random.randint(0,11)
    category_id = db.insert_sentence_label("sdfgs", str(rnd))
    token_label_id = db.insert_token_label("sfgsdfg", category_id)
    assert token_label_id > 0

def insert_sentences_test():
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
    category_id = db.insert_sentence_label(CATEGORY[0], ORDINAL[0])
    assert category_id >= 1

def insert_one_header_test():
    username = get_random_string(15)
    user_id = db.insert_user(username)
    header_id = db.insert_one_header("gjhgfjg", 1, 3, user_id, 1)
    assert header_id > 0

def get_header_subset_max_id_test():
    username = get_random_string(15)
    user_id = db.insert_user(username)
    insert_headers_by_user_id(user_id)
    insert_headers_by_user_id(user_id)
    max_id = db.get_header_subset_max_id(user_id)
    assert max_id[0] >= 2


def get_headers_by_user_test():
    username = get_random_string(15)
    user_id = db.insert_user(username)
    insert_headers_by_user_id(user_id)
    headers = db.get_headers_by_user(user_id)
    for i, header in enumerate(headers):
        assert header[1] == HEADERS[0][i]

def get_headers_by_user_subset_id_test():
    username = get_random_string(15)
    user_id = db.insert_user(username)
    insert_headers_by_user_id(user_id)
    insert_headers_by_user_id(user_id)
    headers = db.get_headers_by_user_subset_id(user_id, 2)
    for i, header in enumerate(headers):
        assert header[1] == HEADERS[0][i]

def get_headers_subset_ids_test():
    username = get_random_string(15)
    user_id = db.insert_user(username)
    insert_headers_by_user_id(user_id)
    insert_headers_by_user_id(user_id)
    subset_ids = db.get_headers_subset_ids(user_id)
    assert subset_ids == [(1,), (2,)]

def get_user_by_name_test():
    username = get_random_string(15)
    user_id = db.insert_user(username)
    row = db.get_user_by_name(username)
    assert user_id > 0
    assert row[1] == username

def get_all_user_test():
    username1 = get_random_string(15)
    username2 = get_random_string(15)
    db.insert_user(username1)
    db.insert_user(username2)
    users = db.get_all_user()
    assert len(users) >= 2


def insert_user():
    username = get_random_string(15)
    user_id = db.insert_user(username)
    assert user_id > 0


def insert_headers():
    header = HEADERS[0]
    col_number = COL_NUMBERS[0]
    target_number = TARGET_NUMBERS[0]
    username = get_random_string(15)
    user_id = db.insert_user(username)
    column_id = db.insert_headers(header, col_number, target_number, user_id)
    assert column_id == True

def insert_headers_by_user_id(user_id):
    header = HEADERS[0]
    col_number = COL_NUMBERS[0]
    target_number = TARGET_NUMBERS[0]
    column_id = db.insert_headers(header, col_number, target_number, user_id)
    assert column_id == True

def insert_headers_user_id_1():
    header = HEADERS[0]
    col_number = COL_NUMBERS[0]
    target_number = TARGET_NUMBERS[0]
    username = get_random_string(15)
    user_id = db.insert_user(username)
    column_id = db.insert_headers(header, col_number, target_number, user_id)
    assert column_id == True

def get_random_string(length):
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str

initialize()
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
get_headers_by_user_test()
print("Test get headers by user id is OK")
get_headers_by_user_subset_id_test()
print("Test get headers by user subset id is OK")
get_headers_subset_ids_test()
print("Test get headers subset ids is OK")
get_user_by_name_test()
print("Test get user by name is OK")
get_all_user_test()
print("Test get all user is OK")
insert_user()
print("Test insert user is OK")
insert_headers_user_id_1()
print("Test insert headers user id=1 is OK'")
insert_headers()
print("Test insert headers is OK'")

