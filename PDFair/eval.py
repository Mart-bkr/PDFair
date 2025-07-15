"""
eval.py

Extension module for evaluating the quality of Markdown output generated from WOO PDFs.
Compares the DeepDoctection-based Markdown conversion against pdf2text output using n-gram similarity.

Author: Martijn Bastiaan Bakker
Date: 15-07-2025
"""

from subprocess import run
import spacy
import re
import os

nlp = spacy.load("nl_core_news_sm")
banned_tokens = {"©", "\uf0b7", '•', '\u2022'}


class PttToken:
    def __init__(self, text, line, index):
        self.text = text

        self.line = line
        self.index = index

        self.border = 0
        self.missing = 0

    def __repr__(self):
        return f"{self.text} (l{self.line}:i{self.index}) - missing {self.missing} times."


class Ngrams:
    def __init__(self, tokens, ngrams):
        self.tokens = tokens
        self.ngrams = ngrams

    def ptttoken_border(self, n=4):
        for i in range(len(self.tokens)):
            if i != len(self.tokens) - 1 and (self.tokens[i + 1].line - self.tokens[i].line) > 1:
                self.tokens[i].border = 1
            if i != 0 and (self.tokens[i].line - self.tokens[i - 1].line) > 1:
                self.tokens[i].border = 1

        for i in range(len(self.tokens)):
            if self.tokens[i].border: 
                continue
            if any(True if t.border == 1 else False for t in self.tokens[i:i + n - 1]):
                self.tokens[i].border = 2
            if any(True if t.border == 1 else False for t in self.tokens[max(0, i - n + 2):i]):
                self.tokens[i].border = 2


# Convert a page class for evaluation
class PageEval:
    def __init__(self, page):
        self.page = page  # The original page
        self.txt = None  # Pdf2text output
        self.ptt = None  # pdf2text ngrams
        self.ddt = None  # deepdoctection ngrams

    # Get pdf2text output (WSL)
    def pdf2txt(self):
        command = ['pdftotext', self.page.doc.location, 'out.txt',  '-nopgbrk', '-f', f'{self.page.p}', '-l', f'{self.page.p}']

        result = -1

        for i in range(10):
            if result == 0: break
            try:
                result = run(command)
            except:
                print(f'{command} failed')

        with open('out.txt', 'r') as file:
            self.txt = file.read()

        os.remove('out.txt')

    # Tokenize text, with or without positional information
    @staticmethod
    def tokenize(text, position):
        if position: 
            return [PttToken(t.lower(), l, i) for l, s in enumerate(re.split('\n', text)) for i, t in enumerate(re.findall('(\w+)', s))]
        return [PttToken(t.lower(), -1, -1) for t in re.findall('(\w+)', text)]

    # Compute deepdoctection ngrams
    def ddt_ngrams(self, n=4):
        tokens = self.tokenize(self.page.header + self.page.md, False)

        self.ddt = Ngrams(tokens,
                        {" ".join(t.text for t in tokens[i:i+n]) for i in range(len(tokens) - n + 1)})

    # Compute pdf2text ngrams (run pdf2text() first)
    def ptt_ngrams(self, n=4, ignore_exception=False):
        if not self.txt and not ignore_exception: raise Exception("Page has no generated text attribute. Use self.pdf2text() first.")

        tokens = self.tokenize(self.txt, True)

        self.ptt = Ngrams(tokens,
                          {" ".join(t.text for t in tokens[i:i+n]) : tokens[i:i+n] for i in range(len(tokens) - n + 1)})

    # Compare n-grams between pdf2text and DeepDoctection output.
    def compare_ngrams(self):
        missing = [ngram for ngram in list(self.ptt.ngrams.keys()) if not ngram in self.ddt.ngrams]

        for ngram in missing:
            for token in self.ptt.ngrams[ngram]:
                token.missing += 1  # The 'missing' value indicates the amount of times a token was not present in a ngram.

    # Replace visualize later with your own function
    def visualize(self):
        raise NotImplementedError(f"{self.__class__.__name__} must implement `visualize()`")
