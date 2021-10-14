from db_helper import DBHelper
import psycopg2
import icecream as ic
import random
import string
from datetime import date
import json

ic = ic.IceCreamDebugger()
# ic.disable()

with open('connect_string.json', 'r', encoding='utf-8') as f:
    CONNECTION = json.load(f)

# choose from all lowercase letter
letters = string.ascii_lowercase

# HEADERS = {0: ["alma", "körte", "szilva", "barack", "káposzta", "kukorica", "dinnye"],
#           }
punctuation = [",", ".", ":", "?", ";", "!", "%", "(", ")", "/", "\\", "'", '"', "[", "]", "{", "}"]
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
        host=CONNECTION['HOST'],
        database=CONNECTION['TRAIN_EXCEL'],
        user=CONNECTION['USER'],
        password=CONNECTION['PASSWORD'])

    with DBHelper() as db:
        for key, sentence_label in ORDINAL.items():
            db.insert_sentence_label(CATEGORY[key], sentence_label)


def insert_token_label_test():
    with DBHelper() as db:
        for x in range(len(ORDINAL)):
            frontend_id = random.randint(0, 9999)
            ordinal = get_random_string(15)
            token_label = get_random_string(15)
            category = get_random_string(15)
            category_id = db.insert_sentence_label(category, ordinal)
            token_label_id = db.insert_token_label(frontend_id, token_label, ordinal)


def insert_sentences_test():
    with DBHelper() as db:
        ord = [ORDINAL[x] for x in range(4)]
        text = [TEXT[x] for x in range(4)]
        token_labels_len = []
        for key, value in TEXT.items():
            token_labels_len.append(count_tokens(value))

        token_labels = generate_token_labels(token_labels_len)
        data = [ord, text, token_labels]
        sentence_id = db.insert_sentences(data)

def count_tokens(text):
    splitted = text.split(" ")
    len_txt = 0
    for token in splitted:
        len_txt += 1
        for t in token:
            if t in punctuation:
                len_txt += 1
    return len_txt

def generate_token_labels(token_labels_len):
    with DBHelper() as db:
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
    with DBHelper() as db:
        category_id = db.insert_sentence_label(CATEGORY[0], ORDINAL[0])


def insert_one_header_test():
    with DBHelper() as db:
        header = get_random_string(15)
        architectname = get_random_string(15)
        architect_id = db.insert_architect(architectname)
        header_id = db.insert_one_header(header, 1, 3, architect_id, 1, 1)

def insert_architect_test():
    with DBHelper() as db:
        architectname = get_random_string(15)
        architect_id = db.insert_architect(architectname)
        assert architect_id > 0

def insert_headers_test():
    with DBHelper() as db:
        header = HEADERS[0]
        col_number = COL_NUMBERS[0]
        target_number = TARGET_NUMBERS[0]
        architectname = get_random_string(15)
        architect_id = db.insert_architect(architectname)
        column_id = db.insert_headers(header, col_number, target_number, architect_id, 1)
        assert column_id == True


def insert_headers_by_architect_id(architect_id):
    with DBHelper() as db:
        header = HEADERS[0]
        col_number = COL_NUMBERS[0]
        target_number = TARGET_NUMBERS[0]
        subset_id = db.insert_headers(header, col_number, target_number, architect_id, 1)
        assert subset_id >= 1


def insert_headers_architect_id_1_test():
    with DBHelper() as db:
        header = HEADERS[0]
        col_number = COL_NUMBERS[0]
        target_number = TARGET_NUMBERS[0]
        architectname = get_random_string(15)
        architect_id = db.insert_architect(architectname)
        subset_id = db.insert_headers(header, col_number, target_number, architect_id, 1)
        assert subset_id >= 1


def get_random_string(length):
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str

def get_random_ordinal():
    num1 = random.randint(15, 99)
    num2 = random.randint(15, 99)
    return str(num1) + "." + str(num2) + "."


initialize()
insert_token_label_test()
print("Test insert token label is OK")
insert_sentences_test()
print("Test insert sentences is OK")
insert_sentence_label_test
print("Test insert sentence label is OK")
insert_one_header_test()
print("Test insert one header is OK")
insert_architect_test()
print("Test insert architect is OK")
insert_headers_architect_id_1_test()
print("Test insert headers architect id=1 is OK'")
insert_headers_test()
print("Test insert headers is OK'")
