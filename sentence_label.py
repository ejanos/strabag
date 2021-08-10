class SentenceLabel:
    id = 0
    category = ""
    ordinal = ""

    def __init__(self, id=None, category=None, ordinal=None):
        if id and category and ordinal:
            self.id = id
            self.category = category
            ordinal = ordinal
        else:
            raise ValueError("Every parameter is needed!")