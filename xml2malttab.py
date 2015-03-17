# -*- coding: utf8 -*-
__author__ = 'imozerov'

import xml.parsers.expat
import glob
import argparse
from rus_dicts import *
from word import Word


def parse_command_line_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('path')
    parser.add_argument('output')
    return parser.parse_args()


class Reader(object):
    def __init__(self):
        self._parser = xml.parsers.expat.ParserCreate()
        self._parser.StartElementHandler = self.start_element
        self._parser.EndElementHandler = self.end_element
        self._parser.CharacterDataHandler = self.char_data

    def start_element(self, name, attr):
        if name == 'W':
            features = attr['FEAT'].split(' ') if 'FEAT' in attr else ['UNK']
            self.word = Word()
            self.word.parse_features(features)
            for i in range(0, len(features)):
                if features[i] in feat_ru_en:
                    features[i] = feat_ru_en[features[i]]

            lemma = lemma = attr['LEMMA'].lower() if 'LEMMA' in attr else ''
            link = attr['LINK'] if 'LINK' in attr else None

            dom = int(attr['DOM']) if attr['DOM'] != '_root' else 0
            pos = features[0]
            feat = set(features[1:])

            if 'adjp' in feat:
                pos = 'VADJ'
                feat -= {'adjp'}

            if 'advp' in feat:
                pos = 'VADV'
                feat -= {'advp'}

            if 'inf' in feat:
                pos = 'VINF'
                feat -= {'inf'}

            self.word.Pos = pos
            self.word.Dom = dom
            self.word.Link = link_ru_en[link] if link in link_ru_en else 'ROOT'
            self.word.Lemma = lemma
            self.word.Id = int(attr['ID'])

            self._info = word_t(lemma=lemma, pos=pos, feat=feat, id=int(attr['ID']), dom=dom, link=link)
            self._cdata = ''

    def end_element(self, name):
        if name == 'S':
            self._sentences.append(self._sentence)
            self._sentence = []
            self.word_sent.append(self.words)
            self.words = []
        elif name == 'W':
            self._sentence.append((self._cdata, self._info))
            #Бывают fantom-слова в корпусе.
            if self.word.Word.strip() == "":
                self.word.Word = self.word.Lemma
            self.words.append(self.word)
            self._cdata = ''

    def char_data(self, content):
        self._cdata += content
        if "word" in self.__dict__.keys() and content != '\n':
            self.word.Word += content.replace(".", "").replace(",", "").replace('"', "")\
                .replace('(', "").replace(')', "").strip()

    def read(self, filename):
        f = self.open_file(filename)
        self.filename = filename
        content = f.read()
        f.close()
        content = content.replace('encoding="windows-1251"', 'encoding="utf-8"')

        self._sentences = []
        self._sentence = []
        self._cdata = ''
        self._info = ''
        self.word_sent = []
        self.words = []

        self._parser.Parse(content)

        return self._sentences, self.word_sent

    def open_file(self, filename):
        return open(filename)


class Translator(object):
    extention = ".tab"
    extention_conll = ".conll"
    train_set_postfix = "_train"
    test_set_postfix = "_test"

    def __init__(self, output="corpus"):
        self._output = output
        self._files_limit = 100
        self._test_set = None
        self._train_set = None
        self._test_set_words = None
        self._train_set_words = None

    def translate(self, files):
        corpus = []
        corpus_sents = []
        for file in files[0:self._files_limit]:
            R = Reader()
            sentences, word_sentences = R.read(file)
            corpus.extend(sentences)
            corpus_sents.extend(word_sentences)
            del (R)

        fold_size = int(round(len(corpus) / 10))
        fold_size_words = int(round(len(corpus_sents) / 10))

        self._train_set = corpus[0:-fold_size]
        self._test_set = corpus[-fold_size:]

        self._train_set_words = corpus_sents[0:-fold_size_words]
        self._test_set_words = corpus_sents[-fold_size_words:]

    def print_train_set(self):
        return self._print_to_file(self._train_set, self.train_set_postfix)

    def print_test_set(self):
        return self._print_to_file(self._test_set, self.test_set_postfix)

    def print_train_set_conll(self):
        return self._print_to_conll_file(self._train_set_words, self.train_set_postfix)

    def print_test_set_conll(self):
        return self._print_to_conll_file(self._test_set_words, self.test_set_postfix)

    def in_english(self, feat_set):
        en_feat_list = []
        for feat in feat_set:
            if unicode(feat) in feat_ru_en.keys():
                en_feat_list.append(feat_ru_en[feat])
        return set(en_feat_list)

    def _print_to_file(self, list_to_print, out_postfix):
        filename = self._output + out_postfix + self.extention
        with open(filename, "w+") as f:
            for sentence in list_to_print:
                for word in sentence:
                    w = word[0] or 'FANTOM'
                    p = '.'.join([word[1].pos] + sorted(word[1].feat & selected_feat))
                    l = word[1].link if word[1].dom else 'ROOT'
                    d = str(word[1].dom)
                    f.write('\t'.join([w, p, d, l]).encode("utf-8"))
                    f.write('\n')
                f.write('\n')
        return filename

    def _print_to_conll_file(self, list_to_print, out_postfix):
        from pprint import pprint
        filename = self._output + out_postfix + self.extention_conll
        with open(filename, "w+") as f:
            for sentence in list_to_print:
                for word in sentence:
                    # print word
                    # feats = "|".join([word.Tense, word.Case, word.Number, word.VerbRepr, word.Other,
                    #                   word.AdjDegree, word.VerbFace, word.Gender, word.Aspect,
                    #                   word.Animacy])
                    feats = []
                    for feat_name in word.feats:
                        if feat_name in word.__dict__.keys() and word.__dict__[feat_name] != u'':
                            feats.append(str.upper(word.__dict__[feat_name]))
                    feat = "|".join(feats)
                    if feat == '':
                        feat = '_'
                    conllstr = ('\t'.join([str(word.Id), word.Word, word.Lemma, word.Pos, word.Pos, feat,
                                     str(word.Dom), str.upper(word.Link)])+"\n").encode("utf-8")
                    f.write(conllstr)
                    print conllstr
                f.write('\n')
                print '\n'
        return filename


if __name__ == '__main__':
    args = parse_command_line_arguments()
    files = glob.glob(args.path + 'SynTagRus2014/*/*.tgt')
    translator = Translator(args.output)
    translator.translate(files)
    translator.print_train_set_conll()
    translator.print_test_set_conll()





