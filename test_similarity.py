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


text = "alma"
target = "alba"
print(test_similarity(text, target))
text = "alma"
target = "lma"
print(test_similarity(text, target))
text = "alma"
target = "lmaa"
print(test_similarity(text, target))
text = "almaa"
target = "alm"
print(test_similarity(text, target))
text = "almaaa"
target = "almba"
print(test_similarity(text, target))
text = "alma"
target = "amla"
print(test_similarity(text, target))
text = "alma"
target = "blma"
print(test_similarity(text, target))
text = "alma"
target = "ama"
print(test_similarity(text, target))
text = "alma"
target = "alxma"
print(test_similarity(text, target))


