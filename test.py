from tqdm import tqdm
from correction import Checker

model_file = '/lab/ogawa/tools/kenlm/data/nikkei_all.binary'
mecab_dict_file = '/tools/env/lib/mecab/dic/unidic'
reverse = True
testdata_file = 'testdata/naist_gawonide.err'

checker = Checker(model_file, mecab_dict_file, reverse=reverse)

with open(testdata_file, 'r') as f:
    testdata = f.readlines()

for i, line in enumerate(tqdm(testdata)):
    text_id = i + 1
    ans, err = line.replace('\n', '').split('\t')
    res, evl = checker.correction(err, ans)
    result = True if res == ans else False
    print("{}\t入力文\t{}\t{}".format(text_id, err, result))
    print("{}\t訂正文\t{}\t{}".format(text_id, res, result))
    print("{}\t正解文\t{}\t{}".format(text_id, ans, result))
    print("\t\ttp: {}, tn: {}, fp: {}, fn: {}".format(evl[0], evl[1], evl[2], evl[3]))

checker.show_final_eval()
checker.show_substitution_eval()
checker.show_completion_eval()