# -*- coding: utf8 -*-
__author__ = 'nikita'

import subprocess
import re

class Word:
    Word = u''
    Lemma = u''
    Pos = u''
    Animacy = u''
    Gender = u''
    Number = u''
    Case = u''
    AdjDegree = u''
    VerbRepr = u''
    Aspect = u''
    Tense = u''
    VerbFace = u''
    Voice = u''
    Other = u''
    Dom = 0
    Link = u''
    Id = 0

    feats = ["Tense", "Case", "Number", "VerbRepr", "Other",
             "AdjDegree", "VerbFace", "Gender", "Aspect",
             "Animacy"]

    def parse_features(self, features):
        try:
            for i in range(0, len(features)):
                    for translation in Translations.__dict__:
                        if Translations.__dict__.get(translation) is not None:
                            if features[i] in Translations.__dict__.get(translation):
                                self.__dict__[translation] = Translations.__dict__.get(translation)[features[i]]
        except Exception, ex:
            print ex.message
            pass

    def lemmatise(self):
        stemProc = subprocess.Popen(["./mystem"],
                                    stdin=subprocess.PIPE,
                                    stdout=subprocess.PIPE)
        out2, err2 = stemProc.communicate(self.Word.encode('utf8'))
        match = re.search( ur"{[^}]+}", out2 )
        if match is not None:
            print "lemmatised new word"
            lemma = match.group()
            lemma = lemma.replace("{", "")
            lemma = lemma.replace("}", "")
            lemma = lemma.replace("?", "")
            self.Lemma = lemma
        # stemProc.terminate()


class Translations:
    Number = {
        u'ЕД': 'sg',
        u'МН': 'pl',
    }
    Gender = {
        u'ЖЕН': 'f',
        u'МУЖ': 'm',
        u'СРЕД': 'n',
    }
    Case = {
        u'ИМ': 'nom',
        u'РОД': 'gen',
        u'ДАТ': 'dat',
        u'ВИН': 'acc',
        u'ТВОР': 'ins',
        u'ПР': 'prep',
        u'ПАРТ': 'gen2',
        u'МЕСТН': 'loc',
    }
    Animacy = {
        u'ОД': 'anim',
        u'НЕОД': 'inan',
    }
    VerbRepr = {
        u'ИНФ': 'inf',
        u'ПРИЧ': 'adjp',
        u'ДЕЕПР': 'advp',
        u'ИЗЪЯВ': 'real',
        u'ПОВ': 'imp',
    }
    Tense = {
        u'ПРОШ': 'pst',
        u'НЕПРОШ': 'npst',
        u'НАСТ': 'prs',
    }
    VerbFace = {
        u'1-Л': '1p',
        u'2-Л': '2p',
        u'3-Л': '3p',
    }
    Other = {
        u'КР': 'shrt',
        u'СЛ': 'compl',
        u'СМЯГ': 'soft',
    }
    Aspect = {
        u'НЕСОВ': 'imperf',
        u'СОВ': 'perf',
    }
    Voice = {
        u'СТРАД': 'pass',
    }
    AdjDegree = {
        u'СРАВ': 'comp',
        u'ПРЕВ': 'supl',
    }
