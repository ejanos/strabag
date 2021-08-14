from db_helper import DBHelper
import psycopg2
import icecream as ic
import random
import string

ic = ic.IceCreamDebugger()
#ic.disable()

# choose from all lowercase letter
letters = string.ascii_lowercase
db = DBHelper()

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
        "FE.1",
        ]}

COL_NUMBERS = {0: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]}
TARGET_NUMBERS = {0: [5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23]}
TEXT = {0: "Felső talajréteghumusz  eltávolítása 60 cm vastagságban (tömör m3) 101,50 - től 100,90 mBf- ig - ",
        1: "felső talajréteg elhelyezése ideiglenes depóniában a területen",
        2: "Ideiglenes talaj depónia kezelése",
        3: "Humusz terítése a területen 40 cm vastagságban",
        4: "föld kiemelés (-0,60 szinttől)",
        5: "Helyszíni vasbeton munkák",
        6: "Kehelyalapok (előregyártott)",
        7: "Alábetonozás (C12/15)",
        8: "Helyszíni vasbeton munkák",
        9: "Mon. vb talpgerenda vasalással zsaluzással kompletten(C30/37)"}


CATEGORY = {0: "Földmunka",
            1: "Betonozás",
            2: "Vasútépítés",
            3: "Magasépítés",
            4: "Mélyépítés",
            5: "Szerelés",
            6: "Javítás",
            7: "Aszfaltozás",
            8: "Vakolás",
            9: "Tetőfedés",
            10: "Alapozás"}
ORDINAL = {0: "02.01.",
           1: "03.02.",
           2: "04.01.",
           3: "05.01.",
           4: "06.01.",
           5: "06.02.",
           6: "06.03.",
           7: "07.01.",
           8: "08.01.",
           9: "09.01."}

def insert_users(num):
    ic("insert users")
    user_ids = []
    for x in range(num):
        username = get_random_string(15)
        user_id = db.insert_user(username)
        user_ids.append(user_id)
    return user_ids

def insert_sentence_labels(num):
    ic("i sentence labels")
    category_ids = []
    for x in range(num):
        category_id = db.insert_sentence_label(CATEGORY[x], ORDINAL[x])
        category_ids.append(category_id)
    return category_ids

def insert_headers(num, user_id):
    ic("i headers")
    for x in range(num):
        header_id = db.insert_headers(HEADERS, COL_NUMBERS, TARGET_NUMBERS, user_id)

def insert_token_labels(num, category_ids):
    ic("i token labels")
    max_label = len(category_ids) - 1
    token_ids = []
    for x in range(num):
        category_id = category_ids[random.randint(0, max_label)]
        category_name = db.get_sentence_label(category_id)
        token_label_id = db.insert_token_label(category_name, category_id)
        token_ids.append(token_label_id)
    return token_ids

def insert_sentences(num):
    ic("i sentences")
    ord = [ORDINAL[x] for x in range(num)]
    text = [TEXT[x] for x in range(num)]
    token_labels_len = []
    for key, value in TEXT.items():
        token_labels_len.append(len(value))

    token_labels = generate_token_labels(token_labels_len)
    data = [ord, text, token_labels]
    sentence_id = db.insert_sentences(data)

def get_random_string(length):
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str

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

user_ids = insert_users(10)
category_ids = insert_sentence_labels(10)
header_id = insert_headers(10, user_ids[0])
token_ids = insert_token_labels(10, category_ids)
insert_sentences(10)