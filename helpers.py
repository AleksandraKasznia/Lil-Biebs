import json
import re
import random
from itertools import chain
import nltk


def calc_prob(dictionary: dict) -> dict:
    total = sum(dictionary.values())
    prob_dict = {k: v / total for k, v in dictionary.items()}
    return prob_dict


def prep_text(text: str) -> str:
    text = text.lower()
    return re.sub(r'[,*+=\-?)("\'.!;:]', '', text)


def get_weighted_random_key(dct: dict):
    return random.choices(list(dct.keys()), weights=list(dct.values()))[0]


def reverse_lines(text_file):
    for line in text_file:
        yield ' '.join(reversed(line.split()))


def get_unique_words(corpus) -> list:
    uniques = list(set(chain(*(line.split() for line in corpus if line))))
    return uniques


def tup2dict(tup, di):
    for a, b in tup:
        di.setdefault(a, []).append(b)

    return di


def init_cmu():
    nltk.download('cmudict')
    nltk.corpus.cmudict.ensure_loaded()
    cmu_entries = nltk.corpus.cmudict.entries()
    cmu_dict = dict()
    tup2dict(cmu_entries, cmu_dict)
    with open('./maps/cmu.json', 'w') as convert_file:
        convert_file.write(json.dumps(cmu_dict))


def require_rhyme_dict():
    try:
        jsonf = open('./maps/cmu.json', 'r')
    except:
        pass
    json_entries = dict(json.load(jsonf))
    jsonf.close()
    print('json_entries loaded.')
    return json_entries


def does_contain_same_word(word1, word2):
    if word1 in word2 or word2 in word1:
        return True
    else:
        return False


def is_rhyme(word1, word2, json_entries, level=1):
    if does_contain_same_word(word1, word2):
        return False
    word1_syllable_arrs = json_entries.get(word1)
    word2_syllables_arrs = json_entries.get(word2)
    if not word1_syllable_arrs or not word2_syllables_arrs:
        return False
    for a in word1_syllable_arrs:
        for b in word2_syllables_arrs:
            if a[-level:] == b[-level:]:
                return True
    return False


if __name__ == '__main__':
    print(prep_text("awa gh34, 232*+-='"))
    print(get_weighted_random_key({"a": 0.2, "b": 0.3, "c": 0.1}))
