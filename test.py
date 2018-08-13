from tqdm import tqdm
from correction import Checker

model_file = '/lab/ogawa/tools/kenlm/data/nikkei_all.binary'
mecab_dict_file = '/tools/env/lib/mecab/dic/unidic'
reverse = True
testdata_file = ''

checker = Checker(model_file, mecab_dict_file, reverse=reverse)

with open(testdata_file, 'r') as f:
    testdata = f.readlines()

for i, line in enumerate(tqdm(testdata)):
    text_id = i + 1
    ans, err = line.replace('\n', '').split('\t')
    res = checker.correction(err, ans)
    result = True if res == ans else False
    print("{text_id}\t入力文\t{err}\t{result}\n".format(text_id, err, result))
    print("{text_id}\t訂正文\t{res}\t{result}\n".format(text_id, res, result))
    print("{text_id}\t正解文\t{ans}\t{result}\n".format(text_id, ans, result))

checker.show_final_eval()
