class Helpers:
    @staticmethod
    def get_max_row_number(data_slice, row_len):
        row_score = [0 for x in range(row_len)]
        for row in data_slice:
            for i, cell in enumerate(row):
                if cell and isinstance(cell, str):
                    row_score[i] += len(cell)
        max_index = 0
        max_score = 0
        #for i, score in enumerate(row_score[1:]):  # 0. oszlop a sorszám
        #    if score > max_score:
        #        max_index = i
        #return max_index
        max_index = row_score.index(max(row_score))
        return max_index
