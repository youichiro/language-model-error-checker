import re
from calculator import LM
from mecab import Mecab

TARGET_PARTICLES = ['が', 'を', 'に', 'で']
TARGET_POS = '助詞-格助詞'


class Checker:
	def __init__(self, model_file, mecab_dict_file):
		self.lm = LM(model_file)
		self.mecab = Mecab(mecab_dict_file)

	def is_missing(self, current_pos, next_pos):
		if not re.match(r'^(助詞|助動詞).*?$', current_pos) \
		and re.match(r'^(名詞|代名詞|接尾辞-名詞的).*?$', next_pos) \
		and not (current_pos == '名詞-数詞' and next_pos == '名詞-数詞'):
			return True
		else:
			return False

	def best_choice(self, words, idx, choices):
		words = words[::-1]
		idx = len(words) - 1 - idx
		scores = []
		for c in choices:
			if c:
				score = self.lm.probability(words[:idx] + [c] + words[idx+1:])
			else:
				score = self.lm.probability(words[:idx] + words[idx+1:])
			scores.append([score, c])
		best_particle = max(scores)[1]
		return best_particle

	def correction(self, text):
		words, parts = self.mecab.tagger(text)
		words = words[::-1]
		parts = parts[::-1]
		fix_flags = [0] * len(words)

		idx = 0
		while idx < len(parts) - 1:
			# 置換
			if parts[idx] == TARGET_POS and words[idx] in TARGET_PARTICLES:
				best_particle = self.best_choice(words, idx, TARGET_PARTICLES)
				words[idx] = best_particle
				fix_flags[idx] = 1
			# 補完
			if self.is_missing(parts[idx], parts[idx + 1]):
				words.insert(idx+1, 'dummy')
				parts.insert(idx+1, TARGET_POS)
				fix_flags.insert(idx+1, 0)
			if words[idx] == 'dummy':
				best_particle = self.best_choice(words, idx, TARGET_PARTICLES + [''])
				if best_particle:
					words[idx] = best_particle
					fix_flags[idx] = 1
				else:
					words = words[:idx] + words[idx+1:]
					parts = parts[:idx] + parts[idx+1:]
					fix_flags= fix_flags[:idx] + fix_flags[idx+1:]
			idx += 1

		words = words[::-1]
		fix_flags[::-1]
		return [(words, is_fix) for word, is_fix in zip(words, fix_flags)]


def test():
	model_file = '/lab/ogawa/tools/kenlm/data/nikkei_all.binary'
	mecab_dict_file = '/tools/env/lib/mecab/dic/unidic'
	checker = Checker(model_file, mecab_dict_file)
	text = ''
	while text != 'end':
		text = input('text> ')
		out = checker.correction(text)
		print(out)