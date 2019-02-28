# -*- coding: utf-8 -*-

import re
from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_bootstrap import Bootstrap
from src.mecab import Mecab
from src.correction_for_api import Checker


app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
bootstrap = Bootstrap(app)

# local
# model_file = '/Users/you_pro/workspace/tools/kenlm/data/nikkei_all_4.binary'
# mecab_dict_file = '/usr/local/lib/mecab/dic/unidic'

# nlp
# model_file = '/home/ogawa/tools/kenlm_data/nikkei_all_4.binary'
# mecab_dict_file = '/tools/env/lib/mecab/dic/unidic/'

# docker
model_file = '/home/tools/kenlm/data/nikkei_all_4.binary'
mecab_dict_file = '/usr/lib64/mecab/dic/unidic'

mecab = Mecab(mecab_dict_file)
checker = Checker(model_file, mecab_dict_file)


@app.route('/', methods=['GET', 'POST'])
def top():
    return render_template('checker.html', base_url=base_url)


@app.route('/api/correction', methods=['GET'])
def correction_api():
    text = request.args.get('input_text')
    texts = re.split('[。\n]', text)
    tokens = []
    for text in texts:
        text = text.strip()
        tokens += checker.correction(text)
        tokens += [["", 0]]
    return jsonify(({'tokens': tokens}))


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
    # app.run(host='127.0.0.1', port=8893)
