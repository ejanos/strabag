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

device = torch.device('cuda')

save_dir = "./model_bert/"
root_dir = "./"
data_dir = "finetuning_dataset/"

logging.basicConfig(filename=root_dir + 'train.log', level=logging.DEBUG)

def cycle(loader, batch, seq_len, device, dataset_len):
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

        tokens = tokenizer(text_list, padding=True, pad_to_multiple_of=8, truncation=True, return_tensors="pt", return_offsets_mapping=True,
                           max_length=512)

        tok_class = torch.ones_like(tokens["input_ids"], dtype=torch.long) * -100
        tmp = torch.ones(tok_class.size(1)) * -100
        mask = tokens["attention_mask"]
        max_index = tok_class.size(1)
        sentence = torch.tensor(sen_list, dtype=torch.long)
        sentence = torch.unsqueeze(sentence, 1)
        offset_mapping = tokens["offset_mapping"]

        for i, elem in enumerate(tok_class_list):
            offset = offset_mapping[i][1:]

            index = (mask[i] == 0).nonzero(as_tuple=False)
            if (index.size(0) == 0):
                index = max_index - 1
            else:
                index = index[0, 0] - 1
                if index > len(elem) - 1:
                    index = len(elem) - 1
            tmp[:index] = torch.tensor(elem[:index])

            source = 1
            prev = -1
            for j, o in enumerate(offset):
                tok_class[i, j + 1] = tmp[source]
                if prev == o[0]:
                    prev = o[1]
                    continue
                prev = o[1]
                source += 1

        yield tokens["input_ids"].to(device), mask.to(device), sentence.to(device), tok_class.to(device)

class TextSamplerDataset(Dataset):
    buffer = ""
    seek = 0
    position = 0
    save_conf = False
    #text = []
    #sen_class = []
    #token_class = []
    data_ids = []


    def __init__(self, seq_len, device, tokenizer, db, test=False):
        super().__init__()
        self.db = db
        self.tokenizer = tokenizer
        self.training_conf = {}
        self.seq_len = seq_len
        self.device = device
        self.test = test
        self.data_counter = 0
        self.BUFFER_LEN = 50000
        #self.data = []

        self.load_data_ids()

        self.pad_id = tokenizer.pad_token_id
        self.mask_id = tokenizer.mask_token_id
        self.pad_token_id = tokenizer.pad_token_id
        self.bos_token_id = tokenizer.sep_token_id
        self.eos_token_id = tokenizer.cls_token_id
        self.mask_token_id = tokenizer.mask_token_id

    def load_data_ids(self):
        self.data_ids = db.get_all_sentence_id()
        random.shuffle(self.data_ids)

    def tokenize(self, txt):
        end = txt.find(" ", len(txt) - 100)
        tokenized = self.tokenizer.encode(txt[:end], return_tensors='pt')
        tokenized_ids = tokenized.ids
        return tokenized_ids

    def __len__(self):
        return len(self.data_ids)

    def __getitem__(self, idx):
        sentence_id = self.data_ids[self.data_counter]
        self.data_counter += 1
        if self.data_counter >= self.__len__():
            self.data_counter = 0
        row = db.get_sentence(sentence_id)
        ic(row)
        text = row[0]
        sen_class = row[1]
        token_class = row[2]
        return text, sen_class, token_class

def decode_tokens(tokens):
    return tokenizer.decode(tokens.tolist())

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

def get_sentence_labels():
    sentence_labels = []
    label_ids = []
    rows = db.get_all_categories()
    for row in rows:
        label_ids.append(row[0])
        sentence_labels.append(row[2])
    return label_ids, sentence_labels

def get_token_labels():
    token_labels = []
    label_ids = []
    rows = db.get_all_token_labels()
    for row in rows:
        label_ids.append(row[0])
        token_labels.append(row[1])
    return label_ids, token_labels

if LOAD_TOKENIZER:
    tokenizer = transformers.BertTokenizerFast(vocab_file=MODEL_PATH + "/vocab.txt", max_len=SEQ_LEN,
                                               padding_side='right', do_lower_case=True, strip_accents=False)

pad_token_id = tokenizer.pad_token_id
bos_token_id = tokenizer.sep_token_id
eos_token_id = tokenizer.cls_token_id
mask_token_id = tokenizer.mask_token_id

db = DBHelper()

sentence_ids, labels = get_sentence_labels()
token_ids, token_labels = get_token_labels()
print("Token labels count: ", len(token_labels))

train_dataset = TextSamplerDataset(SEQ_LEN, device, tokenizer, db)
#val_dataset = TextSamplerDataset(root_dir + data_dir + "valid.txt", SEQ_LEN, device, tokenizer, 0)
#test_dataset = TextSamplerDataset(root_dir + data_dir + "test.txt", SEQ_LEN, device, tokenizer, 0, test=True)
train_loader = cycle(train_dataset, BATCH_SIZE, SEQ_LEN, device, len(train_dataset))
#val_loader = cycle(iter(val_dataset), BATCH_SIZE, SEQ_LEN, device)
#test_loader = cycle(iter(test_dataset), 1, GENERATE_LENGTH, device)


def _mp_fn():

    best_loss = 1e25

    device = torch.device('cuda')

    config = transformers.BertConfig.from_json_file(MODEL_PATH + "/config.json")
    config.id2label = sentence_ids
    config.label2id = labels
    config.num_labels = len(labels)
    print(len(labels))
    for i , label in enumerate(labels):
        print(i, label)
    model = transformers.BertForSequenceAndTokenClassification.from_pretrained(
        MODEL_PATH, local_files_only=True, config=config, num_labels_token=len(token_labels))
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
        with autocast():
            out = model(input_ids=data, labels_sentence=target, labels_token=target_token, attention_mask=mask, return_dict=True)
            loss = out.loss
            scaler.scale(loss).backward()
        #print(f'loss: {loss}')
        training_loss.append(loss.item())
        scaler.unscale_(optim)
        scaler.step(optim)
        scaler.update()
        optim.zero_grad()
        lr_scheduler.step()

        if i % VALIDATE_EVERY == 0 and i != 0:
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

                    acc1, acc2 = get_accuracy(target, target_token, out.logits, out.logits_token)
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
            if val_loss < best_loss:
                best_loss = val_loss
                model.save_pretrained(save_dir + "best/")
                logging.info(f"Best model has saved, iteration: {i}")
            else:
                model.save_pretrained(save_dir + "last/")
                logging.info(f"Last model has saved, iteration: {i}")

        if i % GENERATE_EVERY == 0 and i != 0:
            optim.zero_grad()
            model.eval()
            data, mask, target, target_token = next(train_loader)

            for seq in data:
                prime = decode_tokens(seq)
                print(prime)
            print('*' * 100)

            with torch.no_grad():
                out = model(input_ids=data, attention_mask=mask, return_dict=True)

                pred_sen = torch.argmax(out.logits, dim=-1)
                pred_token = torch.argmax(out.logits_token, dim=-1)

                print(pred_sen)
                print(pred_token)
                for id in pred_sen.cpu():
                    if id < len(sentence_ids):
                        print(config.id2label[str(int(id))])

_mp_fn()
