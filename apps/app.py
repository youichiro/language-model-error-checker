import sys
sys.path.append('..')
from flask import Flask, render_template, request, redirect, url_for, jsonify
from mecab import Mecab
from correction_for_api import Checker

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
model_file = '/home/ogawa/tools/kenlm_data/nikkei_all_4.binary'
mecab_dict_file = '/usr/local/lib/mecab/dic/unidic'
mecab = Mecab(mecab_dict_file)
checker = Checker(model_file, mecab_dict_file)


@app.route('/', methods=['GET', 'POST'])
def top():
    return render_template('checker.html')


@app.route('/api/correction', methods=['GET'])
def correction_api():
    text = request.args.get('input_text')
    tokens = checker.correction(text)
    return jsonify(({'tokens': tokens}))


# @app.route('/api/correction', methods=['GET'])
# def correction_api():
#     text = request.args.get('input_text')
#     words, _ = mecab.tagger(text)
#     tokens = [[word, 0] for word in words]
#     if tokens:
#         tokens[0][1] = 1
#     return jsonify(({'tokens': tokens}))


if __name__ == '__main__':
    app.debug = True
    app.run(host='127.0.0.1')
