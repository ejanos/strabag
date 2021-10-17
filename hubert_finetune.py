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

ic = ic.IceCreamDebugger()
#ic.disable()

DEBUG = False
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
BATCH_SIZE = 32  #32

LAST_EPOCH = 0

LEARNING_RATE = 1e-5
VALIDATE_EVERY = 500
GENERATE_EVERY = 50
MINIBATCH = 4

save_dir = "./model_bert/"
root_dir = "./"
data_dir = "finetuning_dataset/"


class TextSamplerDataset(Dataset):
    buffer = ""
    seek = 0
    position = 0
    save_conf = False
    data_ids = []

    def __init__(self, seq_len, device, tokenizer, test=False):
        super().__init__()
        self.tokenizer = tokenizer
        self.training_conf = {}
        self.seq_len = seq_len
        self.device = device
        self.test = test
        self.data_counter = 0
        self.BUFFER_LEN = 50000
        # self.data = []

        self.load_data_ids()

        self.pad_id = tokenizer.pad_token_id
        self.mask_id = tokenizer.mask_token_id
        self.pad_token_id = tokenizer.pad_token_id
        self.bos_token_id = tokenizer.sep_token_id
        self.eos_token_id = tokenizer.cls_token_id
        self.mask_token_id = tokenizer.mask_token_id

    def load_data_ids(self):
        with DBHelper() as db:
            rows = db.get_all_sentence_id()
            for row in rows:
                self.data_ids.append(row[0])
        random.shuffle(self.data_ids)

    def tokenize(self, txt):
        end = txt.find(" ", len(txt) - 100)
        tokenized = self.tokenizer.encode(txt[:end], return_tensors='pt')
        tokenized_ids = tokenized.ids
        return tokenized_ids

    def __len__(self):
        return len(self.data_ids)

    def __getitem__(self, idx):
        #sentence_id = self.data_ids[self.data_counter]
        sentence_id = self.data_ids[idx]
        #self.data_counter += 1
        #if self.data_counter >= self.__len__():
        #    self.data_counter = 0
        if DEBUG:
            row = [" ", "alma, körte felújítás.", 1, [1, 0, 2, 3, 0]]
        else:
            with DBHelper() as db:
                row = db.get_sentence(sentence_id)
        #ic(row)
        text = row[1]
        sen_class = row[2]
        token_class = row[3]
        return text, sen_class, token_class

class HubertFinetune:
    sentence_label_ids = None
    cat_labels = None
    token_ids = None
    token_labels = None
    token_cat_ids = None

    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

    logging.basicConfig(filename=root_dir + 'train.log', level=logging.DEBUG)

    tokenizer = transformers.BertTokenizerFast(vocab_file=MODEL_PATH + "/vocab.txt", max_len=SEQ_LEN,
                                               padding_side='right', do_lower_case=True, strip_accents=False)
    pad_token_id = tokenizer.pad_token_id
    bos_token_id = tokenizer.sep_token_id
    eos_token_id = tokenizer.cls_token_id
    mask_token_id = tokenizer.mask_token_id
    sentence_ids = []

    def get_sentence_ids(self):
        with DBHelper() as db:
            rows = db.get_all_sentence_id()
            for row in rows:
                self.sentence_ids.append(row[0])

    def check_database_consistency(self):
        if DEBUG:
            return
        with DBHelper() as db:
            index = 0
            ic("Check database consistency")
            for sen_id in tqdm(self.sentence_ids):
                row = db.get_sentence(sen_id)
                text = row[1]
                sen_label_id = row[2]
                token_labels = row[3]
                token_labels, corrupted = self.filter_token_labels(token_labels)
                if corrupted:
                    db.update_sentence(sen_id, text, sen_label_id, token_labels)
                    ic("corrupted token label in sentence:", text)


    def filter_token_labels(self, token_labels):
        result = []
        corrupted = False
        for token in token_labels:
            if token == 0 or token in self.token_ids :
                result.append(token)
            else:
                result.append(0)
                corrupted = True
        return result, corrupted


    def cycle(self, loader, batch, seq_len, device, dataset_len):
        while True:
            text_list = []
            sen_list = []
            tok_class_list = []
            for i in range(batch):
                rnd = random.randint(0, dataset_len - 1)
                text, sen_class, token_class = loader.__getitem__(rnd)
                text_list.append(text)
                sen_list.append(sen_class)
                tok_class_list.append(token_class)

            tokens = self.tokenizer(text_list, padding=True, pad_to_multiple_of=8, truncation=True, return_tensors="pt",
                                    return_offsets_mapping=True, max_length=512)

            input_ids = tokens["input_ids"]

            tokens2 = tokens["input_ids"].tolist()
            max_seq_len = len(tokens2[0]) - 1

            #for t in tokens2[0]:
            #    t2 = self.tokenizer.decode(t)
            #    print(t, t2)

            tok_class = torch.ones_like(input_ids, dtype=torch.long) * -100
            tmp = torch.ones(tok_class.size(1), dtype=torch.long) * -100
            mask = tokens["attention_mask"]
            sentence = torch.tensor(sen_list, dtype=torch.long)
            sentence = torch.unsqueeze(sentence, 1)
            #offset_mapping = tokens["offset_mapping"]

            ic("tok class list",len(tok_class_list))

            for i, elem in enumerate(tok_class_list):
                ic("külső ciklus",i)
                max_index = len(elem) - 1
                if max_index > max_seq_len:
                    max_index = max_seq_len

                index = (mask[i] == 0).nonzero(as_tuple=False)
                if (index.size(0) == 0):
                    index = max_index
                else:
                    index = index[0, 0]
                    if index > max_index:
                        index = max_index
                ic(tmp.size(), len(elem))

                tmp[:index] = torch.tensor(elem[:index], dtype=torch.long)
                #for k, e in enumerate(elem[:index]):
                #    tmp[k] = e

                source = 0
                tok_class[i, 1] = tmp[0]
                for j, token in enumerate(input_ids[i, 2:-1]):
                    #ic(j, self.tokenizer.decode(token.item())[0])
                    if self.tokenizer.decode(token.item())[0] != "#":
                        source += 1
                    tok_class[i, j + 2] = tmp[source]

            print(input_ids.size())
            print(mask.size())
            print( sentence.size())
            print( tok_class.size())
            yield input_ids.to(device), mask.to(device), sentence.to(device), tok_class.to(device)


    def decode_tokens(self, tokens):
        return self.tokenizer.decode(tokens.tolist())

    @staticmethod
    def get_accuracy(target, target_token, logits, logits_token):
        target_sen = target.squeeze()

        num_sen = target_sen.numel()
        num_token = target_token.numel()

        pred_sen = torch.argmax(logits, dim=-1)
        pred_token = torch.argmax(logits_token, dim=-1)

        acc_sen = torch.eq(pred_sen, target_sen)
        acc_token = torch.eq(pred_token, target_token)

        res_sen = acc_sen.count_nonzero()
        res_token = acc_token.count_nonzero()

        ac1 = res_sen / num_sen
        ac2 = res_token / num_token
        return ac1, ac2

    def get_sentence_labels(self):
        sentence_labels = []
        label_ids = []
        with DBHelper() as db:
            rows = db.get_all_categories()
        for row in rows:
            label_ids.append(row[0])
            sentence_labels.append(row[2])
        return label_ids, sentence_labels

    def get_token_labels(self):
        token_labels = []
        label_ids = []
        token_cat_ids = []
        with DBHelper() as db:
            rows = db.get_all_token_labels()
        for row in rows:
            label_ids.append(row[0])
            token_labels.append(row[2])
            token_cat_ids.append(row[3])
        return label_ids, token_labels, token_cat_ids

    def config_label_dict(self, ids, labels):
        result_dict = dict()
        for key, value in zip(ids, labels):
            result_dict[key] = value
        return result_dict

    def train(self):
        self.get_sentence_ids()

        NUM_BATCHES = len(self.sentence_ids) * 1 #4
        ic("batches",NUM_BATCHES)
        WARMUP = int(NUM_BATCHES * 0.06)

        self.sentence_label_ids, self.cat_labels = self.get_sentence_labels()
        self.token_ids, self.token_labels, self.token_cat_ids = self.get_token_labels()

        print("Token labels count: ", len(self.token_labels))
        train_dataset = TextSamplerDataset(SEQ_LEN, self.device, self.tokenizer)
        # val_dataset = TextSamplerDataset(root_dir + data_dir + "valid.txt", SEQ_LEN, device, tokenizer, 0)
        # test_dataset = TextSamplerDataset(root_dir + data_dir + "test.txt", SEQ_LEN, device, tokenizer, 0, test=True)
        train_loader = self.cycle(train_dataset, BATCH_SIZE, SEQ_LEN, self.device, len(train_dataset))
        # val_loader = cycle(iter(val_dataset), BATCH_SIZE, SEQ_LEN, device)
        # test_loader = cycle(iter(test_dataset), 1, GENERATE_LENGTH, device)

        #sentence_ids
        self.check_database_consistency()

        best_loss = 1e25

        device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

        config = transformers.BertConfig.from_json_file(MODEL_PATH + "/config.json")
        config.id2label = self.config_label_dict(self.sentence_label_ids, self.cat_labels)
        config.label2id = self.config_label_dict(self.cat_labels, self.sentence_label_ids)
        config.num_labels = len(self.sentence_label_ids)+1
        print(len(self.sentence_label_ids))
        for i , label in enumerate(self.cat_labels):
            print(i, label)
        model = transformers.BertForSequenceAndTokenClassification.from_pretrained(
            MODEL_PATH, local_files_only=True, config=config, num_labels_token=len(self.token_labels)+1)
        model.eval()

        model.to(device)

        scaler = GradScaler()

        optim = torch.optim.Adam(model.parameters(), lr=LEARNING_RATE, weight_decay=0.01, betas=(0.9, 0.98), eps=1e-06)
        optim.param_groups[0]['initial_lr'] = LEARNING_RATE
        optim.zero_grad()

        lr_lambda = lambda epoch: 1 / WARMUP * (epoch + 1) if epoch < WARMUP else 1

        lr_scheduler = torch.optim.lr_scheduler.LambdaLR(optim, lr_lambda, last_epoch=LAST_EPOCH, verbose=False)
        if LAST_EPOCH:
            batch_start = LAST_EPOCH
        else:
            batch_start = 0
        for i in tqdm(range(batch_start, NUM_BATCHES), mininterval=10., desc='training'):
            model.train()

            training_loss = []
            data, mask, target, target_token = next(train_loader)
            ic(data.size(), mask.size(), target.size(), target_token.size())
            with autocast():
                out = model(input_ids=data, labels_sentence=target, labels_token=target_token, attention_mask=mask, return_dict=True)
                loss = out.loss
                scaler.scale(loss).backward()
            print(f'loss: {loss}')
            training_loss.append(loss.item())
            scaler.unscale_(optim)
            scaler.step(optim)
            scaler.update()
            optim.zero_grad()
            lr_scheduler.step()

            if i == (NUM_BATCHES - 1) or (i % VALIDATE_EVERY == 0 and i != 0):
                optim.zero_grad()
                ac_mean1 = []
                ac_mean2 = []
                val_loss = 0.
                for _ in range(VAL_LOSS_CYCLE):
                    model.eval()
                    with torch.no_grad():
                        # TODO val_loader
                        data, mask, target, target_token = next(train_loader)
                        out = model(input_ids=data, labels_sentence=target, labels_token=target_token, attention_mask=mask,
                                    return_dict=True)
                        loss = out.loss
                        val_loss += loss
                        print(f'validation loss: {loss}')

                        acc1, acc2 = self.get_accuracy(target, target_token, out.logits, out.logits_token)
                        print("accuracy", acc1.item(), acc2.item())
                        ac_mean1.append(acc1.item())
                        ac_mean2.append(acc2.item())

                val_loss /= VAL_LOSS_CYCLE
                training_loss_mean = np.array(training_loss).mean()
                ac_sen_mean = np.array(ac_mean1).mean()
                ac_token_mean = np.array(ac_mean2).mean()
                print(f'validation loss: {val_loss}, iteration: {i}')
                print(f'training loss: {training_loss_mean}')
                logging.info(f'validation loss: {val_loss}')
                logging.info(f'training loss: {training_loss_mean}')
                logging.info(f'Accuracy sentence: {ac_sen_mean}  Accuracy token: {ac_token_mean}')
                if not DEBUG and val_loss < best_loss:
                    best_loss = val_loss
                    # TODO elmenteni token labeleknek a számát, a predict-nél visszatölteni
                    model.save_pretrained(save_dir + "best/")
                    logging.info(f"Best model has saved, iteration: {i}")
                elif not DEBUG:
                    # TODO elmenteni token labeleknek a számát, a predict-nél visszatölteni
                    model.save_pretrained(save_dir + "last/")
                    logging.info(f"Last model has saved, iteration: {i}")

            if i % GENERATE_EVERY == 0 and i != 0:
                optim.zero_grad()
                model.eval()
                data, mask, target, target_token = next(train_loader)

                for seq in data:
                    prime = self.decode_tokens(seq)
                    print(prime)
                print('*' * 100)

                with torch.no_grad():
                    out = model(input_ids=data, attention_mask=mask, return_dict=True)

                    pred_sen = torch.argmax(out.logits, dim=-1)
                    pred_token = torch.argmax(out.logits_token, dim=-1)

                    print(pred_sen)
                    print(pred_token)
                    for id in pred_sen.cpu():
                        if id < len(self.sentence_ids):
                            print(config.id2label[str(int(id))])

if __name__ == '__main__':
    DEBUG = False
    model = HubertFinetune()
    model.train()
