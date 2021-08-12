from db_helper import DBHelper

class ProcessColumns:
    db = DBHelper()
    threshold = 0.6
    users = dict()  # key: user id, value: row from users table

    def __init__(self):
        self.get_users()
        # TODO if users == None raise Exception

    def get_users(self):
        users = self.db.get_all_user()
        for user in users:
            self.users[user[0]] = user[1]
        users.clear()

    def compare(self, texts):
        for key, value in self.users:
            data = self.db.get_columns_by_user(key)
            target_text = data[1]
            target_columns = data[2]
            target_targets = data[3]
            if self.is_greater_than_threshold(texts, target_text):
                user_id = data[4]
                return target_columns, target_targets, user_id
        return (None, None, None,)


    def is_greater_than_threshold(self, texts, target_text):
        scores = []
        for i, text in enumerate(texts):
            score = self.test_similarity(text, target_text[i])
            scores.append(score)
        return self.average(scores) > self.threshold


    def test_similarity(text, target):
        text = text.replace(" ", "")
        target = target.replace(" ", "")
        score = 0.0
        index = 0
        for i, c in enumerate(text):
            if c in target:
                w = target.find(c, i)
                x = target.find(c, index)
                if 0 < x < w:
                    score += index / x
                    index += 1
                elif w > 0:
                    score += i / w
                    index = i
                elif w == i or x == i:
                    score += 1
                    index = i
                elif x == index:
                    score += 1
                    index += 1
        return score

    @staticmethod
    def average(lst):
        return sum(lst) / len(lst)


if __name__ == '__main__':
    proc = ProcessColumns()
    header = ["Work/\nMunkanem", "Work/\nMunkanem", "Position/\ntétel", "Description", "Leírás", "Quantity/\nmennyiség ", "Unit/\negység", "Quantity modification from GC \n(if needed +/- )", "Materila unit price/\nanyag egység ár HUF", "Unit worker fees/\nmunka díj    egység ár   HUF", "Unit price sum/\nösszes egység ár   HUF", "Sum/\nÖsszesen\nHUF"]
    columns = [1,2,3,4,5,6,7,8,9,10,11]
    targets = [5,4,6,3,7,2,8,3,4,5,2]
    user_id = 1
    proc.compare(header, columns, targets, user_id)

