import pickle
from collections import defaultdict
import nltk

from custom_errors import TokenNotFound, RhymeNotFound
from helpers import *
from verse import Verse

BEGIN = '__BEGIN__'
END = '__END__'
json_entries = None


class MarkovModel:

    def __init__(self, corpus, n: int):
        self.base = n
        self.corpus = corpus
        self.model = defaultdict(dict)
        self.json_entries = require_rhyme_dict()

    def prepare_sentence(self, sentence: str) -> list:
        sentence = prep_text(sentence)
        return [*[BEGIN] * self.base, *sentence.split(), *[END] * self.base]

    def fit_model(self) -> None:
        for line in self.corpus:
            sentence = self.prepare_sentence(line)
            for i in range(len(sentence)):
                *key, value = sentence[i:i + self.base + 1]
                key = tuple(key)
                self.model[key][value] = self.model[key].get(value, 0) + 1

        for key in self.model:
            self.model[key] = calc_prob(self.model[key])

    def get_next_token(self, token: tuple) -> str:
        try:
            choices = self.model[token]
        except KeyError:
            raise TokenNotFound("Token wasn't found in the corpus")

        return get_weighted_random_key(choices)

    def get_random_token(self) -> str:
        random_key = random.choice(list(self.model.keys()))
        return get_weighted_random_key(self.model[random_key])

    def get_random_start_token(self) -> str:
        return get_weighted_random_key(self.model[(BEGIN, )*self.base])

    def fit_rhymes(self) -> defaultdict:
        found_rhymes = defaultdict(set)
        unique_words = get_unique_words(self.corpus)

        for i, word in enumerate(unique_words):
            found_rhymes[word] = set([ rhyming_word for rhyming_word in unique_words if is_rhyme(word, rhyming_word,
                                                                                                 self.json_entries)])

        found_rhymes = dict(found_rhymes)

        for key in found_rhymes:
            found_rhymes[key] = list(found_rhymes[key])

        return found_rhymes


class SongWriter:
    def __init__(self, base: int, forward_model: MarkovModel, backward_model: MarkovModel, rhymes):
        self.base = base
        self.models = {
            'forward': forward_model,
            'backward': backward_model
        }
        self.rhymes = rhymes

    def get_rhyming_word(self, word) -> str:
        choices = []

        for last_n_words in reversed(range(2,6)):
            key = word[-last_n_words:]
            if self.rhymes.get(key):
                choices.extend({random.choice(self.rhymes[key]) for w in range(last_n_words)})

        if choices:
            return random.choice(choices)
        else:
            raise RhymeNotFound

    def write_verse(self, mode, first_word=None, max_tries=3, max_words=8) -> Verse:
        verses = []
        for i in range(max_tries):
            new_verse = self.generate_verse(mode=mode, first_word=first_word, max_words=max_words)
            verses.append(new_verse)

        distribution = {k: len(k) for k in verses}
        distribution = calc_prob(distribution)

        return get_weighted_random_key(distribution)

    def generate_verse(self, mode='forward', first_word=None, max_words=15):
        model = self.models[mode]
        verse = Verse()

        for _ in range(self.base):
            verse.append(BEGIN)

        if not first_word:
            first_word = model.get_random_start_token()

        verse.append(first_word)

        for i in range(max_words):
            token = verse.get_last_n_words(self.base)
            try:
                next_token = model.get_next_token(token)
            except TokenNotFound:
                next_token = model.get_random_start_token()

            verse.append(next_token)

            if END in next_token:
                break

        verse = verse.clear()
        if mode == 'backward':
            return verse.revert()

        return verse

    def generate_rhyming_lines(self, num_lines: int, max_tries=50) -> list:
        rhyme = None

        for _ in range(max_tries):
            try:
                first_line = self.write_verse(mode='forward')
                rhyme = self.get_rhyming_word(first_line.get_last_n_words(1)[0])
                break
            except RhymeNotFound:
                pass

        if not rhyme:
            raise RhymeNotFound

        lines = [first_line, ]

        for i in range(num_lines):
            next_verse = self.write_verse(mode='backward', first_word=rhyme)
            try:
                rhyme = self.get_rhyming_word(next_verse.get_last_n_words(1)[0])
            except RhymeNotFound:
                rhyme = None
            lines.append(next_verse)

        return lines

    def get_message_response(self, mess):
        print(f"Message: {mess}")
        mess = prep_text(mess)
        last_word = mess.split()[-1]
        print(f"last: {last_word}")
        try:
            rhyme = self.get_rhyming_word(last_word)
            print(rhyme)
        except RhymeNotFound:
            print("error")
            return "Meh"

        resp = self.write_verse(mode='backward', first_word=rhyme)

        return resp

    def sing_a_song(self, num_verse=3, num_chorus_lines=6):
        chorus = self.generate_rhyming_lines(num_chorus_lines)
        chorus = [str(sen) for sen in chorus]
        chorus = {"title": "Chorus", "text": chorus}
        song = []

        for i in range(num_verse):
            verse = self.generate_rhyming_lines(8)
            verse = [str(sen) for sen in verse]
            song.append({"title": f"Verse {i+1}", "text": verse})
            song.append(chorus)

        for segment in song:
            for line in segment["text"]:
                print(line)
            print("\n")

        return song

    @classmethod
    def create_bieber_dup(cls, corpus_path, base):
        corpus = open(corpus_path, 'r', encoding='utf-8')
        forward_model = MarkovModel(corpus, base)
        forward_model.fit_model()

        corpus.seek(0)
        rhymes = forward_model.fit_rhymes()

        corpus = open(corpus_path, 'r', encoding='utf-8')
        backward_model = MarkovModel(reverse_lines(corpus), base)
        backward_model.fit_model()

        return cls(base, forward_model, backward_model, rhymes)

    @classmethod
    def load_bieber_dup(cls, path):
        f = open(path, 'rb')
        loaded_model = pickle.load(f)

        forward = MarkovModel([], loaded_model['base'])
        backward = MarkovModel([], loaded_model['base'])

        forward.model = loaded_model['forward']
        backward.model = loaded_model['backward']

        return cls(loaded_model['base'],forward,backward,loaded_model['rhymes'])

    def save_bieber_dup(self, path):
        self.models['forward'].corpus, self.models['backward'].corpus = None, None
        saved_models = {
            'base': self.base,
            'forward': dict(self.models['forward'].model),
            'backward': dict(self.models['backward'].model),
            'rhymes': self.rhymes
        }
        f = open(path, 'wb')
        pickle.dump(saved_models, f)


def rhyme(inp, level):
     entries = nltk.corpus.cmudict.entries()
     syllables = [(word, syl) for word, syl in entries if word == inp]
     rhymes = []
     for (word, syllable) in syllables:
             rhymes += [word for word, pron in entries if pron[-level:] == syllable[-level:]]
     return set(rhymes)


if __name__ == '__main__':
    # init_cmu()
    # little_biebs = SongWriter.create_bieber_dup("corpus.txt", 4)
    # little_biebs.save_bieber_dup(path="./bieber4.pkl")
    model_n2 = SongWriter.load_bieber_dup('bieber4.pkl')
    song = model_n2.sing_a_song()
    print(song)

