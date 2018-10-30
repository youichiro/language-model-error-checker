import sys
sys.path.append('..')
from flask import Flask, render_template, request, redirect, url_for, jsonify
from mecab import Mecab

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
mecab_dict_file = '/usr/local/lib/mecab/dic/unidic'
mecab = Mecab(mecab_dict_file)


@app.route('/', methods=['GET', 'POST'])
def checker():
    return render_template('checker.html')


@app.route('/api/correction', methods=['GET'])
def test():
    text = request.args.get('input_text')
    words, _ = mecab.tagger(text)
    tokens = [[word, 0] for word in words]
    if tokens:
        tokens[0][1] = 1
    return jsonify(({'tokens': tokens}))

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0')
