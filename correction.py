import re
from culculator import LM
from mecab import Mecab

TARGET_PARTICLES = ['が', 'を', 'に', 'で']


class Checker:
    def __init__(self, model_file, mecab_dict_file, reverse=True):
        self.lm = LM(model_file)
        self.mecab = Mecab(mecab_dict_file)
        self.reverse = reverse
        self.sent_num = self.correct_num = 0
        self.tp = self.tn = self.fp = self.fn = 0
        self.err, self.res, self.ans = [], [], []

    def is_missing(self, current_pos, next_pos):
        if not self.reverse:
            if re.match(r'^(名詞|代名詞|接尾辞-名詞的).*?$', current_pos) \
            and not re.match(r'^(助詞|助動詞).*?$', next_pos) \
            and not (current_pos == '名詞-数詞' and next_pos == '名詞-数詞'):
                return True
            else:
                return False
        elif self.reverse:
            if not re.match(r'^(助詞|助動詞).*?$', current_pos) \
            and re.match(r'^(名詞|代名詞|接尾辞-名詞的).*?$', next_pos) \
            and not (current_pos == '名詞-数詞' and next_pos == '名詞-数詞'):
                return True
            else:
                return False

    def best_choice(self, words, idx, choices):
        if self.reverse:
            words = words[::-1]
            idx = len(words) - 1 - idx
        scores = []
        for c in choices:
            if c:
                score = self.lm.probability(words[:idx] + [c] + words[idx+1:])
            else:
                score = self.lm.probability(words[:idx] + words[idx+1:])
            scores.append([score, c])
        best_particle = max(scores)[1]
        return best_particle


    def eval_correction(self, idx):
        if self.err[idx] != self.res[idx]:
            if self.res[idx] == self.ans[idx]: self.tp += 1
            elif self.res[idx] != self.ans[idx]: self.fp += 1
        elif self.err[idx] == self.res[idx]:
            if self.res[idx] == self.ans[idx]: self.tn += 1
            elif self.res[idx] != self.ans[idx]: self.fn += 1


    def eval_completion(self, idx):
        if len(self.res) - len(self.err) == 1:
            if self.res[idx] == self.ans[idx]:
                self.tp += 1
            else:
                self.fp += 1
                if self.err[idx] == self.ans[idx]:
                    self.ans = self.ans[:idx] + ['dummy'] + self.ans[idx:]
        elif len(self.res) - len(self.err) == 0:
            if self.res[idx] == self.ans[idx]:
                self.tn += 1
            else:
                self.fn += 1
                self.ans = self.ans[:idx] + self.ans[idx+1:]
        else:
            raise ValueError("eval error (completion).")


    def this_eval(self, prev_tp, prev_tn, prev_fp, prev_fn):
        return [self.tp - prev_tp, self.tn - prev_tn, self.fp - prev_fp, self.fn - prev_fn]


    def show_final_eval(self):
        precision = self.tp / (self.tp + self.fp) * 100
        recall = self.tp / (self.tp + self.fn) * 100
        f_measure = 2 * precision * recall / (precision + recall)
        accuracy = self.correct_num / self.sent_num * 100
        result = """
        ----- Results -----
        sent_num: {sent}
        #TP: {tp}, #TN: {tn}, #FP: {fp}, #FN: {fn}
        F={f:2.2f}%, P={p:2.2f}%, R={r:2.2f}%, Acc={correct}/{sent}={a:2.2f}%
        """.format(sent=self.sent_num, tp=self.tp, tn=self.tn, fp=self.fp, fn=self.fn,
                   f=f_measure, p=precision, r=recall, correct=self.correct_num, a=accuracy)
        print(result)


    def correction(self, err, ans):
        self.sent_num += 1
        tp, tn, fp, fn = self.tp, self.tn, self.fp, self.fn
        words, parts = self.mecab.tagger(err)
        ans_words, _ = self.mecab.tagger(ans)
        if self.reverse:
            words = words[::-1]
            parts = parts[::-1]
            ans_words = ans_words[::-1]
        self.err, self.ans = words[:], ans_words[:]

        idx = 0
        while idx < len(parts) - 1:
            # 訂正
            if parts[idx] == '助詞-格助詞' and words[idx] in TARGET_PARTICLES:
                best_particle = self.best_choice(words, idx, TARGET_PARTICLES)
                words[idx] = best_particle
                self.res = words[:]
                self.eval_correction(idx)
                self.err = words[:]

            # 補完
            if self.is_missing(parts[idx], parts[idx + 1]):
                words.insert(idx+1, 'dummy')
                parts.insert(idx+1, '助詞-格助詞')
            if words[idx] == 'dummy':
                best_particle = self.best_choice(words, idx, TARGET_PARTICLES + [''])
                if best_particle:
                    words = words[:idx] + [best_particle] + words[idx + 1:]
                else:
                    words = words[:idx] + words[idx+1:]
                    parts = parts[:idx] + parts[idx + 1:]
                self.res = words[:]
                self.eval_completion(idx)
                self.err = words[:]

            idx += 1

        if words == ans_words: self.correct_num += 1
        if self.reverse: words = words[::-1]

        return ''.join(words), self.this_eval(tp, tn, fp, fn)


def main():
    model_file = '/lab/ogawa/tools/kenlm/data/nikkei_all.binary'
    mecab_dict_file = '/tools/env/lib/mecab/dic/unidic'
    reverse = True

    checker = Checker(model_file, mecab_dict_file, reverse=reverse)

    err = ''
    while err != 'end':
        err = input('err > ')
        ans = input('ans > ')
        output, evl = checker.correction(err, ans)
        print(output)
        print(evl)


if __name__ == '__main__':
    main()
