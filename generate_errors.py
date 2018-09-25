import copy
import random
from tqdm import tqdm
from mecab import Mecab


GEN_SIZE = 5000000
src_file = 'resource/bccwj.txt'
ans_save_file = 'error_corpus/bccwj.5M.ans'
err_save_file = 'error_corpus/bccwj.5M.err'

mecab_dic = '/tools/env/lib/mecab/dic/unidic'
mecab = Mecab(mecab_dic)
TARGETS = ['が', 'を', 'に', 'で']
TARGET_PART = '助詞-格助詞'


def get_case_positions(words, pos_tags):
    """格助詞の位置リストを返す"""
    case_idx =  [i for i, (w, p) in enumerate(zip(words, pos_tags))
                 if p == TARGET_PART and w in TARGETS]
    return case_idx, len(case_idx)


def get_n_case(text):
    """文中の格助詞の数を返す"""
    words, pos_tags = mecab.tagger(text)
    n_case = sum([1 for w, p in zip(words, pos_tags) 
                  if p == TARGET_PART and w in TARGETS])
    return n_case


def generate_patterns(confusion_set):
    """
    置換候補の全組み合わせを生成する
    :param confusion_set: [['が', 'に', 'を', 'で'], ['が', 'に', 'を', 'で']]
    :return patterns: [['が', 'が'], ['が', 'に'], ['が', 'を'], ..., ['で', 'で']]
    """
    ap = 1  # ap:全候補文の数
    base = []
    for i in range(len(confusion_set)):
        base.append(len(confusion_set[i]))
        ap *= len(confusion_set[i])
    # 組み合わせを作成
    elements = []
    for i in range(len(confusion_set)):
        if i == 0:
            step = int(ap / base[i])
        else:
            step = int(step / base[i])
        repeat = int(ap / base[i] / step)
        element = []
        for _ in range(repeat):
            for particle in confusion_set[i]:
                for _ in range(step):
                    element.append(particle)
        elements.append(element)
    # 配列を縦方向に結合
    patterns = []
    for i in range(ap):
        patterns.append([e[i] for e in elements])
    return patterns


if __name__ == '__main__':
    with open(src_file, 'r') as f:
        src_lines = f.readlines()

    count = 0
    for line in tqdm(src_lines):
        if count > GEN_SIZE: break
        src_text = line.replace('\n', '')
        candidates = []
        words, parts = mecab.tagger(src_text)
        case_idx, n_case = get_case_positions(words, parts)
        if not case_idx or n_case > 5: continue
        if n_case == 1:
            for t in TARGETS + ['']:
                error = ''.join(words[:case_idx[0]] + [t] + words[case_idx[0]+1:])
                delete = 1 if not t else 0
                if n_case == get_n_case(error) + delete:
                    candidates.append(error)
        else:
            confusion_set = [TARGETS] * n_case
            patterns = generate_patterns(confusion_set)
            for pattern in patterns:
                error_words = copy.deepcopy(words)
                for i in range(n_case):
                    error_words = error_words[:case_idx[i]] + [pattern[i]] + error_words[case_idx[i]+1:]
                error = ''.join(error_words)
                delete = pattern.count('')
                if n_case == get_n_case(error) + delete:
                    candidates.append(error)
        if candidates:
            choice = random.choice(candidates)
            count += 1

        with open(ans_save_file, 'a') as f:
            f.write(src_text + '\n')
        with open(err_save_file, 'a') as f:
            f.write(choice + '\n')
