BEGIN = '__BEGIN__'
END = '__END__'

class Verse:
    def __init__(self):
        self.words = []

    def append(self,word) -> None:
        self.words.append(word)

    def get_last_n_words(self, n) -> tuple:
        return tuple(self.words[-n::])

    def revert(self):
        self.words.reverse()
        return self

    def clear(self):
        self.words = [word for word in self.words if word != BEGIN and word != END]
        return self

    def __str__(self) -> str:
        return " ".join(self.words)

    def __len__(self) -> int:
        return len(self.words)

    def __repr__(self) -> str:
        return repr(self.words)