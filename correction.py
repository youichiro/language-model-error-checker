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
    def __init__(self, model_file, mecab_dict_file):
        self.lm = LM(model_file)
        self.mecab = Mecab(mecab_dict_file)

    def correction(self, text, reverse=True):
        words, parts = self.mecab.tagger(text)
        if reverse:
            words.reverse()
            parts.reverse()

        idx = 0
        while idx < len(parts) - 1:
            # 補完
            if is_missing(parts[idx], parts[idx + 1], reverse=reverse):
                best_particle = 'hoge'
                words.insert(idx+1, best_particle)
                parts.insert(idx+1, '助詞-格助詞')
            # 訂正
            if parts[idx] == '助詞-格助詞' and words[idx] in TARGET_PARTICLES:
                best_particle = 'huga'
                words[idx] = best_particle
            idx += 1

        return ''.join(words)

def main():
    model_file = '/lab/ogawa/tools/kenlm/data/nikkei_all.binary'
    mecab_dict_file = '/tools/env/lib/mecab/dic/unidic'
    reverse = False

    checker = Checker(model_file, mecab_dict_file)
    text = '彼が車買う'
    correct_sent = checker.correction(text, reverse=reverse)
    print(correct_sent)


if __name__ == '__main__':
    words = ['彼', 'が', '車', '買う', '親', '売る']
    parts = ['名詞', '助詞-格助詞', '名詞', '動詞', '名詞', '動詞']

    main()
