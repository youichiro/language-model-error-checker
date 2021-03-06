import re
from calculator import LM

model_file = '/lab/ogawa/tools/kenlm/data/nikkei/nikkei_all_4.binary'
test_file = '/lab/ogawa/gec-classifier/datasets/naist_gawonide.test.wkt'
TARGET_PARTICLES = ['が', 'を', 'に', 'で']
lm = LM(model_file)


def lm_choice(text, target_idx):
    scores = []
    for p in TARGET_PARTICLES:
        candidate = text[:target_idx] + p + text[target_idx+1:]
        score = lm.probability(candidate.split(' '))
        scores.append([score, p])
    best = max(scores)[1]
    return best


def main():
    with open(test_file) as f:
        testdata = f.readlines()
    count, t = 0, 0
    for test in testdata:
        test = test.replace('\n', '')
        target_idx = test.find('<') + 1
        ans = test[target_idx]
        text = test[:target_idx-1] + 'X' + test[target_idx+2:]
        target_idx -= 1
        predict = lm_choice(text, target_idx)
        count += 1
        t += 1 if predict == ans else 0
        print(text.replace(' ', ''), predict, ans, predict == ans)

    print('Acc. {:.2f}% ({}/{})'.format(t / count * 100, t, count))


if __name__ == '__main__':
    main()
