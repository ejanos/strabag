from db_helper import DBHelper

class ProcessColumns:
    db = DBHelper()
    threshold = 0.6

    # megnézi, az adatbázisban már található ilyen header összeállítás?
    def compare(self, texts):
        result = dict()
        users = self.db.get_all_user()
        for user_id, _ in users:
            scores = []
            subset_ids = self.db.get_headers_subset_ids(user_id)
            if not subset_ids:
                continue
            for subset in subset_ids:
                rows = self.db.get_headers_by_user_subset_id(user_id, subset[0])
                target_text = self.get_column_from_rows(rows, 1)
                target_columns = self.get_column_from_rows(rows, 2)
                target_targets = self.get_column_from_rows(rows, 3)

                score = self.get_header_similarity_score(texts, target_text)
                if score > self.threshold:
                    scores.append(score)
                    if score not in result:
                        result[score] = (target_columns, target_targets, user_id, subset,)
        if scores:
            scores.sort(reverse=True)
            return result[scores[0]]
        return (None, None, None,)

    def get_column_from_rows(self, rows, column):
        target_text = []
        for row in rows:
            target_text.append(row[column])
        return target_text



    def is_greater_than_threshold(self, texts, target_text):
        scores = []
        for i, text in enumerate(texts):
            score = self.test_similarity(text, target_text[i])
            scores.append(score)
        return self.average(scores) > self.threshold

    def get_header_similarity_score(self, texts, target_text):
        scores = []
        for i, text in enumerate(texts):
            score = self.test_similarity(text, target_text[i])
            scores.append(score)
        return self.average(scores)


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

