import os
import re
import argparse
from calculator import LM
from mecab import Mecab

TARGET_PARTICLES = ['が', 'を', 'に', 'で']
TARGET_POS = '助詞-格助詞'
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
    acc_of_one = 0
    n_of_one = 0

    for n, (err, ans) in enumerate(zip(error_data, answer_data)):
        err = err.replace('\n', '')
        ans = ans.replace('\n', '')
        err_words, err_parts = mecab.tagger(err)
        ans_words, ans_parts = mecab.tagger(ans)
        corrected_words =  err_words[::]

        # 訂正箇所
        target_idx = [idx for idx in range(len(err_words) - 1)
                      if err_parts[idx] == TARGET_POS
                      and err_words[idx] in TARGET_PARTICLES]

        # 文末から訂正
        if reverse: target_idx[::-1]

        # 訂正箇所が1箇所か複数か
        is_one_error = True if len(target_idx) == 1 else False
        if is_one_error: n_of_one += 1

        for idx in target_idx:
            predict = choice(err_words, idx, lm)
            corrected_words[idx] = predict
            answer = ans_words[idx]

            if predict == answer:
                acc += 1
                if is_one_error:
                    acc_of_one += 1
            total_prediction_num += 1

        corrected = ''.join(corrected_words)
        if args.show:
            print(f'{n+1}')
            print(f'err: {err}')
            print(f'ans: {ans}')
            print(f'out: {corrected}')
            print(f'Result: {corrected == ans}\n')

    total_acc = acc / total_prediction_num * 100
    one_acc = acc_of_one / n_of_one * 100
    multi_acc = (acc - acc_of_one) / (total_prediction_num - n_of_one) * 100
    print(f"""
    \n[Total]
    Accuracy: {total_acc:.5}%
    # sentence: {n+1}
    # total prediction: {total_prediction_num}
    \n[For one error]
    Accuracy: {one_acc:.5}%
    # sentence: {n_of_one}
    # total prediction: {n_of_one}
    \n[For multiple error]
    Accuracy: {multi_acc:.5}%
    # sentence: {(n+1) - n_of_one}
    # total prediction: {total_prediction_num - n_of_one}
    """)

if __name__ == '__main__':
    main()
