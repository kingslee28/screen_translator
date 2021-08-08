# -*- coding:utf-8 -*-
import re
import textwrap


def wrap_text(text, width, word_split=''):
    wrapped_text = ''
    if word_split == ' ':  # e.g. English words
        for chunk in textwrap.wrap(text, width=width, break_long_words=False):
            wrapped_text += chunk + '\n'
        return wrapped_text
    elif word_split == '':  # e.g. Chinese words
        temp_text = ''
        punctuations = '[,，｡。､、;；!！?？…]'
        matched_punctuations = re.findall(punctuations, text)
        for i, chunk in enumerate(re.split(punctuations, text)):
            temp_text += chunk.strip()
            if i < len(matched_punctuations):
                temp_text += matched_punctuations[i] + ' '
        for chunk in textwrap.wrap(temp_text, width=width, break_long_words=True):
            wrapped_text += chunk + '\n'
        return wrapped_text.replace(' ', '')
