import kenlm

class LM:
    def __init__(self, model_file, reverse=True):
        print('Loading KenLM model:', model_file)
        self.lm = kenlm.Model(model_file)
        self.reverse = reverse

    def probability(self, words):
        words = [word for word in words if word]
        if self.reverse:
            words = words[::-1]
        return self.lm.score(' '.join(words), bos=True, eos=True)
