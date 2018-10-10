from tqdm import tqdm
from correction import Checker
from bleu import compute_bleu

model_file = '/lab/ogawa/tools/kenlm/data/nikkei/nikkei_all_4.binary'
mecab_dict_file = '/tools/env/lib/mecab/dic/unidic'
reverse = True
testdata_ans_file = 'testdata/naist_gawonide.ans'
testdata_err_file = 'testdata/naist_gawonide.err'
checker = Checker(model_file, mecab_dict_file, reverse=reverse)

testdata_ans = open(testdata_ans_file).readlines()
testdata_err = open(testdata_err_file).readlines()
assert len(testdata_ans) == len(testdata_err)

ans_data = []
res_data = []
for i in range(len(testdata_ans)):
    text_id = i + 1
    ans = testdata_ans[i].replace('\n', '')
    err = testdata_err[i].replace('\n', '')
    if err == ans:
        print("err and ans are the same. text_id: {}".format(text_id))
        continue
    res, evl = checker.correction(err, ans)
    if not res:
        print("IndexError. text_id: {}".format(text_id))
        continue
    result = True if res == ans else False
    print("{}\t入力文\t{}\t{}".format(text_id, err, result))
    print("{}\t訂正文\t{}\t{}".format(text_id, res, result))
    print("{}\t正解文\t{}\t{}".format(text_id, ans, result))
    print("\t\ttp: {}, tn: {}, fp: {}, fn: {}".format(evl[0], evl[1], evl[2], evl[3]))

    ans_data.append([ans])
    res_data.append(res)

checker.show_final_eval()
checker.show_substitution_eval()
checker.show_completion_eval()

bleu_score = compute_bleu(ans_data, res_data, smooth=True)[0]
print('BLEU: {:.4f}'.format(bleu_score))
