from typing import Optional, Any
import numpy as np
import torch
import logging
from torch.utils.data import Dataset
import logging
from tqdm import tqdm
import transformers
from torch.cuda.amp import GradScaler, autocast
import random
from db_helper import DBHelper
import icecream as ic
import csv

ic = ic.IceCreamDebugger()
ic.disable()

MODEL_PATH = "./hubert_wiki_lower"
MODEL_NAME = "best/"
DATASET_DIR = "finetuning_dataset/"
LOAD_MODEL = True
LOAD_PRETRAINED = True
LOAD_TRAINING_CONF = False
LOAD_TOKENIZER = True

VAL_LOSS_CYCLE = 20

punctuation = ".,:;!?"
SEQ_LEN = 512
GENERATE_LENGTH = 512
TEST_LENGTH = 128
BATCH_SIZE = 32  #4

LAST_EPOCH = 0
NUM_BATCHES = int(583 * 4)   # 3?
WARMUP = int(NUM_BATCHES * 0.06)
LEARNING_RATE = 1e-5
VALIDATE_EVERY = 100
GENERATE_EVERY = 100
MINIBATCH = BATCH_SIZE

save_dir = "./model_bert/"
root_dir = "./"
data_dir = "finetuning_dataset/"

class HubertModel:
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    model = None
    sentence_ids = None
    labels = None
    token_ids = None
    token_labels = None
    config = None

    tokenizer = transformers.BertTokenizerFast(vocab_file=MODEL_PATH + "/vocab.txt", max_len=SEQ_LEN,
                                               padding_side='right', do_lower_case=True, strip_accents=False)

    pad_token_id = tokenizer.pad_token_id
    bos_token_id = tokenizer.sep_token_id
    eos_token_id = tokenizer.cls_token_id
    mask_token_id = tokenizer.mask_token_id

    def __init__(self, test=False):
        #, number_categories, number_token_labels,
        self.CATEGORIES, self.TOKEN_LABELS = self.load_train_params()
        self.test = test

        #print(len(self.labels))
        #for i, label in enumerate(self.labels):
        #    print(i, label)
        # TODO elmenteni token labeleknek a számát, itt visszatölteni

    def load_csv(self, filename):
        res = dict()
        with open(filename, 'r', encoding='utf-8') as csv_file:
            reader = csv.reader(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            for row in reader:
                if len(row) > 0:
                    res[row[0]] = int(row[1])
        return res

    def decode_tokens(self, tokens):
        return self.tokenizer.decode(tokens.tolist())

    def get_sentence_labels(self):
        sentence_labels = []
        label_ids = []
        with DBHelper() as db:
            rows = db.get_all_categories()
        for row in rows:
            label_ids.append(row[0])
            sentence_labels.append(row[2])
        return label_ids, sentence_labels

    def get_token_labels(self, ):
        token_labels = []
        label_ids = []
        with DBHelper() as db:
            rows = db.get_all_token_label()
        for row in rows:
            label_ids.append(row[0])
            token_labels.append(row[1])
        return label_ids, token_labels

    def predict(self, sentence, number_categories, number_token_labels):
        if not self.model or self.CATEGORIES != number_categories or self.TOKEN_LABELS != number_token_labels:
            self.CATEGORIES = number_categories
            self.TOKEN_LABELS = number_token_labels
            self.sentence_ids, self.labels = self.get_sentence_labels()
            self.token_ids, self.token_labels = self.get_token_labels()
            print("Token labels count: ", len(self.token_labels))

            self.device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

            self.config = transformers.BertConfig.from_json_file(MODEL_PATH + "/config.json")
            self.config.id2label = self.sentence_ids
            self.config.label2id = self.labels
            self.config.num_labels = number_categories
            self.model = transformers.BertForSequenceAndTokenClassification.from_pretrained(
                save_dir + MODEL_NAME, local_files_only=True, config=self.config, num_labels_token=number_token_labels)
            self.model.eval()
            self.model.to(self.device)

        with torch.no_grad():
            #ic(sentence)
            tokenized = self.tokenizer.encode(sentence, return_tensors='pt').to(self.device)
            #  mask = torch.ones_like(tokenized, dtype=torch.long)
            out = self.model(input_ids=tokenized, return_dict=True)

            pred_sen = torch.argmax(out.logits, dim=-1)
            sen_prob = out.logits[0, pred_sen[0].item()]
            ic(sen_prob)
            pred_token = torch.argmax(out.logits_token, dim=-1)
            token_prob = self.get_token_probability(out.logits_token, pred_token)
            if not self.test:
                return pred_sen.cpu().tolist(), sen_prob.cpu().item(), pred_token.cpu().tolist(), token_prob
            self.print_test_params(pred_sen, pred_token)

    def load_train_params(self):
        train_param_dict = self.load_csv(save_dir + "trainparams.csv")
        number_categories = train_param_dict["categories"]
        number_token_labels = train_param_dict["tokens"]
        return number_categories, number_token_labels

    def get_token_probability(self, logits, tokens):
        token_prob = []
        for i, token in enumerate(tokens[0]):
            prob = logits[0, i, token.item()]
            token_prob.append(prob.item())
        return token_prob

    def print_test_params(self, pred_sen, pred_token):
        print(pred_sen)
        print(pred_token)
        for id in pred_sen.cpu():
            if id < len(self.sentence_ids):
                print(self.config.id2label[int(id)])

if __name__ == '__main__':
    model = HubertModel(test=True)
    while True:
        text = input("Please enter text!")
        model.predict(text)
