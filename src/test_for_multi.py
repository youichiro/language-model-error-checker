import os
import re
import argparse
from calculator import LM
from mecab import Mecab

TARGET_PARTICLES = ['が', 'を', 'に', 'で']
TARGET_POS = ['助詞-格助詞', '助動詞']
mecab_dict_dir = os.environ['MECABDIC']
mecab = Mecab(mecab_dict_dir)


def choice(words, target_idx, lm):
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

    acc = 0
    total_prediction_num = 0
    acc_of_error = 0
    total_error_num = 0
    error = 0
    n = 0

    for err, ans in zip(error_data, answer_data):
        err = err.replace('\n', '')
        ans = ans.replace('\n', '')
        err_words, err_parts = mecab.tagger(err)
        ans_words, ans_parts = mecab.tagger(ans)
        corrected_words =  err_words[::]

        # もし誤り文と正解文で単語分割の数が異なるならエラー
        if [len(t) for t in err_words] != [len(t) for t in ans_words]:
            error += 1
            continue

        # 訂正箇所
        target_idx = [idx for idx in range(len(err_words) - 1)
                      if err_parts[idx] in TARGET_POS
                      and err_words[idx] in TARGET_PARTICLES
                      and idx != 0 and idx != len(err_words) - 1]
        # 誤り箇所
        error_idx = [idx for idx in range(len(err_words) - 1) if err_words[idx] != ans_words[idx]]

        # 文末から訂正
        if reverse: target_idx[::-1]

        for idx in target_idx:
            predict = choice(err_words, idx, lm)
            corrected_words[idx] = predict
            answer = ans_words[idx]
            if predict == answer:
                acc += 1
                if idx in error_idx:
                    acc_of_error += 1
            total_prediction_num += 1

        corrected = ''.join(corrected_words)
        n += 1
        total_error_num += len(error_idx)
        if args.show:
            print(f'{n}')
            print(f'err: {err}')
            print(f'ans: {ans}')
            print(f'out: {corrected}')
            print(f'Result: {corrected == ans}\n')

    print(f"""
    # sentence num: {n}
    # error sentence num: {error}
    # total prediction: {total_prediction_num}
    # correct prediction: {acc}
    # total error num: {total_error_num}
    # correct prediction for error: {acc_of_error}
    Accuracy: {acc / total_prediction_num * 100:.2f}%
    Accuracy of errors: {acc_of_error / total_error_num * 100:.2f}%
    Accuracy of non errors: {(acc - acc_of_error) / (total_prediction_num - total_error_num) * 100:.2f}%
    """)

if __name__ == '__main__':
    main()
