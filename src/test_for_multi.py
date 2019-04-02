import os
import re
import argparse
from calculator import LM
from mecab import Mecab

TARGET_PARTICLES = ['が', 'を', 'に', 'で']
TARGET_POS = '助詞-格助詞'
mecab_dict_dir = os.environ['MECABDIC']
mecab = Mecab(mecab_dict_dir)


def choice(words, target_idx):
    scores = []
    for p in TARGET_PARTICLES:
        candidate = words[:target_idx] + [p] + words[target_idx+1:]
        score = lm.probability(candidate)
        scores.append([score, p])
    best = max(scores)[1]
    return best


def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--model', required=True, help='LM model file (.binary)')
    parser.add_argument('--err', required=True, help='Error sentence file')
    parser.add_argument('--ans', required=True, help='Answer sentence file')
    parser.add_argument('--forward', default=False, action='store_true')
    parser.add_argument('--show', default=False, action='store_true')
    args = parser.parse_args()

    lm = LM(args.model)
    error_data = open(args.err, 'r').readlines()
    answer_data = open(args.ans, 'r').readlines()
    reverse = not args.forward

    for i, (err, ans) in enumerate(zip(error_data, answer_data)):
        err = err.replace('\n', '')
        ans = ans.replace('\n', '')
        err_words, err_parts = mecab.tagger(err)
        ans_words, ans_parts = mecab.tagger(ans)
        corrected_words =  err_words[::]

        for idx in range(len(err_words) - 1):
            if err_parts[idx] == TARGET_POS and err_words[idx] in TARGET_PARTICLES:
                predict = choice(err_words, idx)
                corrected_words[idx] = predict

        corrected = ''.join(corrected_words)
        if args.show:
            print(f'{i+1}')
            print(f'err: {err}')
            print(f'ans: {ans}')
            print(f'out: {corrected}')
            print(f'Result: {corrected == ans}')

if __name__ == '__main__':
    main()
