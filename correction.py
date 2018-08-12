import re
from culculator import LM
from mecab import Mecab

TARGET_PARTICLES = ['が', 'を', 'に', 'で']


def is_missing(current_pos, next_pos, reverse=True):
    if not reverse:
        if re.match(r'^(名詞|代名詞|接尾辞-名詞的).*?$', current_pos) \
           and not re.match(r'^(助詞|助動詞).*?$', next_pos) \
           and not (current_pos == '名詞-数詞' and next_pos == '名詞-数詞'):
            return True
        else:
            return False
    elif reverse:
        if not re.match(r'^(助詞|助動詞).*?$', current_pos) \
           and re.match(r'^(名詞|代名詞|接尾辞-名詞的).*?$', next_pos) \
           and not (current_pos == '名詞-数詞' and next_pos == '名詞-数詞'):
            return True
        else:
            return False

class Checker:
    def __init__(self, model_file, mecab_dict_file, reverse=True):
        self.lm = LM(model_file)
        self.mecab = Mecab(mecab_dict_file)
        self.reverse = reverse


    def best_choice(self, words, idx, choices):
        if self.reverse:
            words = words[::-1]
            idx = len(words) - 1 - idx
        scores = []
        for c in choices:
            words[idx] = c
            score = self.lm.probability(words)
            scores.append([score, c])
        best_particle = max(scores)[1]
        return best_particle


    def correction(self, text):
        words, parts = self.mecab.tagger(text)
        if self.reverse:
            words.reverse()
            parts.reverse()

        idx = 0
        while idx < len(parts) - 1:
            # 訂正
            if parts[idx] == '助詞-格助詞' and words[idx] in TARGET_PARTICLES:
                best_particle = self.best_choice(words, idx, TARGET_PARTICLES)
                words[idx] = best_particle

            # 補完
            if is_missing(parts[idx], parts[idx + 1], reverse=self.reverse):
                words.insert(idx+1, 'dummy')
                parts.insert(idx+1, '助詞-格助詞')
            if words[idx] == 'dummy':
                best_particle = self.best_choice(words, idx, TARGET_PARTICLES)
                words[idx] = best_particle

            idx += 1

        if self.reverse:
            words.reverse()
        return ''.join(words)


def main():
    model_file = '/lab/ogawa/tools/kenlm/data/nikkei_all.binary'
    mecab_dict_file = '/tools/env/lib/mecab/dic/unidic'
    reverse = True

    checker = Checker(model_file, mecab_dict_file, reverse=reverse)

    text = ''
    while text != 'end':
        text = input('>> ')
        output = checker.correction(text)
        print(output)

    # text = '彼が車買う'
    # correct_sent = checker.correction(text)
    # print(correct_sent)


if __name__ == '__main__':
    main()
