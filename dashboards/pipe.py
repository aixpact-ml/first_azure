
# from flask import session
import os
import re
import string
from collections import Counter
import pandas as pd
import numpy as np
from pathlib import Path

import streamlit as st

import spacy
from spacy.tokens import Doc, Span, Token
from spacy.pipeline import EntityRuler
from spacy.tokenizer import Tokenizer
from spacy.matcher import Matcher
from spacy.attrs import ORTH, NORM, LEMMA, ENT_TYPE, POS
from spacy.lang.char_classes import ALPHA, ALPHA_LOWER, ALPHA_UPPER
from spacy.lang.char_classes import CONCAT_QUOTES, LIST_ELLIPSES, LIST_ICONS
from spacy.util import compile_prefix_regex, compile_infix_regex, compile_suffix_regex
from spacy.lang.de.punctuation import _quotes

from utter_dicts import POS
from custom_ner import EntMatcher, EntityMatcher, SVO, SpellCheck

import doctest

############## setup

PATH = Path('./data')
path = os.path.join('./data', 'utters.csv')
text = ''

############## declare constants

MATCHED_ENTS2 = []

# Words that are not specific or explicit
STOPWORDS = ['an', 'the', 'this', 'that', 'there', 'in', 'it', 'its', 'of', 'or', 'to', 'only', 'how',
             'is', 'was', 'are', 'be', 'been', 'do', 'get', 'got', 'want', 'will', 'had', 'has', 'should',
             'can', "'s", "'ve", "'d", 'make', 'take', 'takes', 'have', 'come', 'could', 'put', 'move', 'would',
             'gon', 'na', 'try', 'tried', 'use', 'using', 'used', 'regarding', 'know', 'follow', 'need',
             'for', 'so', 'as', 'and', 'yet', 'too', 'just', 'with', 'if', 'like', 'then', 'than', 'because',
             'sir', 'madam', 'pls', 'please', 'thanks', 'thank', 'thx', 'kind', 'kindly', 'but', 'say', 'hope',
             'what', 'which', 'when', 'where', 'why', 'already', 'still', 'same', 'else', 'up', 'on',
             'hi', 'hello', 'howdy', 'hi!', 'hey', 'dear', 'goodmorning', 'goodafternoon', 'good', 'however',
             'soon', 'more', 'old', 'new', 'first', 'last', 'anymore', 'much', 'from', 'really', 'back',
             'many', 'out', 'at', 'all', 'some', 'through', 'after', 'other', 'now', 'tell', 'see', 'hope',
             'again', 'here', 'about', 'ask', 'give', 'go', 'another', 'very', 'thru', 'each', 'into', 'since',
             'digit', 'number', 'earlier', 'someone', 'once', 'different', 'exactly', 'till',
             'me', 'my', 'you', 'your', "m'", '..', '...', "'", 'everything', 'fully', 'help']

# Verb - action groups CRUD
VERBS = dict(
    inform=['check', 'help', 'request', 'advice', 'assist', 'advise', 'inform'],
    get=['retrieve', 'recieve', 'receive', 'require', 'follow', 'reflect', 'result'],
    provide=['provide', 'upload', 'present', 'indicate', 'submit', 'resubmit', ],
    process=['process', 'perform', 'bill', 'list'],
    create=['open', 'create', 'submit', 'register', 'enroll', 'start', 'initiate', 'complete', 'apply'],
    confirm=['confirm', 'accept', 'accord', 'approve', 'maintain', 'proceed', 'verify', 'activate'],
    update=['update', 'change', 'move', 'edit', 'replace', 'renew', 'deduct', 'revert', 'resubmit', 'correct', 'compute'],
    fail=['reject', 'fail', 'forget', 'lose', 'hinder'],
    stop=['end', 'disconnect', 'stop', 'cancel', 'terminate'],
    instruct=['how', 'why', 'when', 'where', 'long', 'much', 'many', 'instruct'],
    explain=['understand', 'wonder', 'remember', 'recognize', 'appear', 'explain'],
    )

# OOV Domain terms - annomize?
OOV_TERMS = {"OTHER BANK": ['bpi', 'cimb', 'prc', 'interbank', 'metrobank', 'unionbank'],
              "ING": ['ing'],
              "CASH": ['gcash', 'atm'],
              "MESSAGE": ['sms', 'wechat', 'whatsapp'],
              "CREDS": ['id', 'ids', 'umud', 'sss'],
              "LOGIN": ['pincode', 'pass', 'pin', 'login'],
              "ACCOUNT": ['acct']
              }

# OOV Domain terms - annomize?
BANK_TERMS = {"PAYMENT": ['transfer', 'deposit', 'money', 'via', 'gcash', 'bpi', 'fund',
              'credit', 'cash', 'payment', 'check', 'cheque', 'amount', 'time', 'money',
              'metrobank', 'unionbank', 'instapay', 'bdo', 'interbank', 'transaction',
              'withdrawal', 'payee', 'destination', 'transaction', 'withdraw', 'withdrawal'],
              #
              "ACCOUNT": ['account', 'active', 'activation', 'application',
              'open', 'submission', 'document', 'proof', 'profile'],
              #
              "CREDS": ['id', 'ids', 'umud', 'sss', 'address', 'phone', 'driver', 'license', 'passport',
              'identification', 'signature', 'maiden', 'married'],
              #
              "CASH": ['gcash', 'atm'],
              #
              "LOGIN": ['pincode', 'password', 'pin', 'code', 'login'],
              "WELCOME": ['hi', 'hey', 'hello', 'dear', 'goodafternoon', 'goodmorning'],
              "STATE": ['unavailable', 'fail', 'unable', 'not', 'yet', 'reject',
                        'earlier', 'late', 'recent', 'old', 'new', 'wrong'],
              "EXPLAIN": ['when', 'why', 'how', 'long', 'much'],
              "UNRESOLVED": ['still', 'again', 'already', 'why', 'where', 'times', 'twice',
                             'last', 'anymore', 'different'],
              "TBA": ['verification']
              }

ANNOMIZE = {"REDACTED": ['bank'],
            "PERSON": ['bank'],
            "ORG": []
            }

HOW = {"HOW": ['how', 'long', 'much', 'many'],
       }

TAGS = {"PRODUCT": ['PAYMENT', 'ACCOUNT'],
        "P_DET": ['CASH', 'OTHER BANK'],
        "P_ATTR": ['CREDS', 'LOGIN', 'PROCESS', 'FAIL', 'STATE', 'UNRESOLVED', 'UPDATE',
                   'ORDINAL', 'DATE'],
        # "CHANNEL": ['CASH', '', ''],
        "ACTION": ['INFORM', 'INSTRUCT', 'EXPLAIN', 'HOW'],
        "A_ATTR": ['MESSAGE', 'GET', 'PROVIDE', 'CREATE', 'CONFIRM', 'STOP', 'DURATION', 'TIME'],
        "WELCOME": ['WELCOME'],
        "OTHER": ['REDACTED', 'TBA']
        }

IDX_TAGS = {v: k for k, values in TAGS.items() for v in values}

############## load vocab

@st.cache(allow_output_mutation=True, persist=True)  # REACTIVATE after DEBUG
def load_vocab():
    """Load vocab."""
    return spacy.load("en_core_web_md")  # sm or lg

nlp = load_vocab()


################ SET TAGS IS_SOMETHING

def set_tags(dictionary):
    """
    Set custom tags.

    >>> set_tags({'PERSON': 'Frank', 'VERB': 'is', 'PLACE': 'here'})
    None
    """
    for LABEL, terms in dictionary.items():
        getter = lambda t: t.pos_ in terms
        Token.set_extension(f'IS_{LABEL}', getter=getter, force=True)
    return None

def get_tag(doc, tag):
    """
    Get custom tags.

    >>> get_tag(nlp('Frank is here'), 'PERSON')
    'Frank'

    """
    # return [(t.text, eval(f't._.IS_{tag}')) for t in doc]
    return ', '.join([t.text for t in doc if eval(f't._.IS_{tag}')])

def some_test(doc):
    """
    Just some test function.

    >>> some_test(nlp('Frank is here'))
    'Frank'
    """
    return doc[0]


########### Infixes - how to split tokens

def custom_tokenizer(nlp):
    # https://spacy.io/usage/linguistic-features#tokenization
    special_cases = {"ing": [{"ORTH": "ING"}]}  #
    prefix_re = re.compile(r'''^[[("']''')
    suffix_re = re.compile(r'''[])"']$''')
    infix_re = re.compile(r'''[!\.,\?:;()|]''')  # split on symbol inside string
    simple_url_re = re.compile(r'''^https?://''')
    return Tokenizer(nlp.vocab, rules=special_cases,
                                prefix_search=prefix_re.search,
                                suffix_search=suffix_re.search,
                                infix_finditer=infix_re.finditer,
                                token_match=simple_url_re.match)

nlp.tokenizer = custom_tokenizer(nlp)
entity_ruler = EntityRuler(nlp, overwrite_ents=True)

############ modify tokenizer infix patterns - METHOD 2
# keep words-with-dashes_together
# infixes = (LIST_ELLIPSES + LIST_ICONS + [
#         r"(?<=[0-9])[+\-\*^](?=[0-9-])",
        # r"(?<=[{al}{q}])\.(?=[{au}{q}])".format(al=ALPHA_LOWER, au=ALPHA_UPPER, q=CONCAT_QUOTES),
        # r"(?<=[{a}]),(?=[{a}])".format(a=ALPHA),
        # r"(?<=[{a}0-9])[:<>=/](?=[{a}])".format(a=ALPHA)
        # ])
# infix_regex = spacy.util.compile_infix_regex(infixes)
# nlp.tokenizer.infix_finditer = infix_regex.finditer

# Sanity check
# st.write([t.text for t in nlp("Required\languages:java-python/c#,javascript.so-me,here?dot")])
# st.write('https://bank-to-bank')


############## ADD missing/special terms to vocab or use as spell checker of normalize words

def add_special_pattern(text, orth, label):
    """Add special case rule and entity rule to label KB/OOV terms."""
    for cap in [text.lower(), text.upper(), text[0]+text[1:].capitalize(), text.title()]:
        nlp.tokenizer.add_special_case(cap, [{ORTH: orth, NORM: label}])
        for symbol in list('!?,.'):
            nlp.tokenizer.add_special_case(cap+symbol, [{ORTH: orth, NORM: label}])
    entity_ruler.add_patterns([{"label": label, "pattern": text}])
    return None

# placeholder/annomizer - TODO Cap sensitive or not?
for placeholder, keywords in OOV_TERMS.items():
    for t in keywords:
        add_special_pattern(t, placeholder, placeholder)


#
def redact(doc):
    for t in doc:
        if not doc.vocab.strings[t.text]:
            st.write('<OOV>')
            add_special_pattern(t.text, '<OOV>', '<OOV>')
    return doc

# # Sanity check
# text = 'gcash gcash, gcash. gcash! gcash? ' + 'Gcash Gcash, Gcash. Gcash! Gcash? ' + 'gCash gCash, gCash. gCash! gCash?'
# st.write('sanity check all', text)
# st.write('sanity check all', nlp(text))
# st.write('sanity check all', [t.text for t in nlp(text)])

############## Spelling

# @st.cache(allow_output_mutation=True, persist=True)  # REACTIVATE after DEBUG
def load_spellchecker(**kwargs):
    spell_checker = SpellCheck()
    # nlp = kwargs.get('nlp')
    # if True:  # TODO kwargs.get('punct')
    #     DOMAIN_WORDS = ["'m", "'d", "'ve", "'ll'", "'s", 'id', 'hi', 'hey', 'ing', 'bpi',
    #     'gcash', 'cimb', 'prc', 'sms', 'umud', 'sss', 'pincode']
    #     df_custom = pd.DataFrame((t, 99999999999) for t in list(string.punctuation) + DOMAIN_WORDS)
    #     spell_checker.append_dict(df_custom)
    return spell_checker

# spell_checker = load_spellchecker()


############## nlp pipe

def append_pipe(component, nlp=nlp, **kwargs): #name, after, nlp=nlp):
    """"""
    try:
        nlp.add_pipe(component, **kwargs) #name=name, after=after)
    except Exception as err:
        # Already added to pipe / replace
        # st.write(nlp.pipe_names)
        # st.write(err)
        nlp.replace_pipe(kwargs.get('name'), component)


def pipe_spelling(doc, vocab=nlp.vocab):
    """Correct at token level."""
    tokens = []
    for t in doc:
        if t.dep_ == 'compound':
            tokens.append(spell_checker(t.text.lower()))
        else:
            tokens.append(t.text.lower())
    # tokens = [spell_checker(t.text.lower()) for t in doc]
    return Doc(vocab, tokens)


def pipe_lower(doc, vocab=nlp.vocab):
    """"""
    # st.write('before lower', doc)
    tokens = [t.text.lower() for t in doc]
    # st.write('after lower', tokens)
    return Doc(vocab, tokens)


def pipe_stopwords(doc, vocab=nlp.vocab):
    """"""
    # st.write("Delete all stopwords in pipeline")
    # st.write('before', doc)
    tokens = [t.text for t in doc
                     if t.text.lower() not in STOPWORDS
                     if t.is_alpha
                     if len(t.text) > 1]
    # st.write('after:', tokens)
    return Doc(vocab, tokens)


def pipe_annomizer(doc, vocab=nlp.vocab):
    text = ' '.join([t.text for t in doc])
    add_special_pattern(text, '[REDACTED]', 'REDACTED')
    # redacted = []
    # for t in doc:
    #     if t.ent_type_ in ['REDACTED', 'PERSON', 'ORG']:
    #         redacted.append(Doc(vocab, t.ent_type_)[0])
    #     else:
    #         redacted.append(t)
    #     doc2 = Doc(vocab, redacted)
    return doc




#
ent_matcher_verbs = EntMatcher(VERBS, lambda x: [{'LEMMA': {'IN': x}, 'POS': {'IN': ['VERB', 'NOUN']}}], nlp)
ent_matcher_nouns = EntMatcher(BANK_TERMS, lambda x: [{'LEMMA': {'IN': x}, 'POS': {'IN': ['NOUN', 'PROPN', 'VERB']}}], nlp)
ent_matcher_welcome = EntMatcher(BANK_TERMS, lambda x: [{'LEMMA': {'IN': x}, 'POS': {'IN': ['INTJ']}}], nlp)
ent_matcher_state = EntMatcher(BANK_TERMS, lambda x: [{'LEMMA': {'IN': x}, 'POS': {'IN': ['ADJ', 'PART']}}], nlp)
ent_matcher_resolve = EntMatcher(BANK_TERMS, lambda x: [{'LEMMA': {'IN': x}, 'POS': {'IN': ['ADV']}}], nlp)


# headers_fn = lambda w: [{'LEMMA': w.lower()},  {'POS': 'CCONJ', 'OP': '*'}, {'POS': 'VERB', 'OP': '*'}, {'POS': 'NOUN', 'OP': '*'}]
ent_matcher_how = EntMatcher(HOW, lambda x: [{'NORM': {'IN': x}, 'POS': {'IN': ['ADV']}}], nlp)

ent_matcher_redacted = EntMatcher(ANNOMIZE, lambda x: [{'LEMMA': {'NOT_IN': x},
                                                        'TAG': {'IN': ['NNP']},
                                                        'DEP': {'IN': ['compound', 'dobj', 'pobj', 'nsubj', 'ROOT']}}], nlp=nlp)
# doc = ent_matcher_verbs(nlp('Hi, I forgot my login password! What should I do?'))
# st.write([(t.text, t.lemma_, t.pos_, t.ent_type_) for t in doc])


##################

# Add components to the pipeline
# append_pipe(pipe_spelling, name='spelling', first=True, nlp=nlp)  ### TODO word or sentence level?
# append_pipe(entity_matcher, name='custom_ents', after='ner', nlp=nlp)
append_pipe(entity_ruler, name='pattern_ents', after='ner', nlp=nlp)
append_pipe(ent_matcher_verbs, name='verb_ents', after='ner', nlp=nlp)
append_pipe(ent_matcher_nouns, name='noun_ents', after='ner', nlp=nlp)
append_pipe(ent_matcher_welcome, name='welcome_ents', after='ner', nlp=nlp)
append_pipe(ent_matcher_state, name='state_ents', after='ner', nlp=nlp)
append_pipe(ent_matcher_resolve, name='resolve_ents', after='ner', nlp=nlp)
append_pipe(ent_matcher_redacted, name='redacted_ents', after='ner', nlp=nlp)
append_pipe(ent_matcher_how, name='how_ents', after='ner', nlp=nlp)
# append_pipe(redact, name='oov', after='redacted_ents', nlp=nlp)
# append_pipe(pipe_lower, name='lower', after='ner', nlp=nlp)
# append_pipe(pipe_stopwords, name='stopwords', after='ner', nlp=nlp)

############## SVO

svo = SVO(nlp)

# # Sanity check
# st.write('sanity check all', 'transfer via GCASH gcash? gCash, gcash!, Gcash. gcash-Gcash')
# st.write('sanity check all', nlp('transfer via GCASH gcash? gCash, gcash!, Gcash. gcash-Gcash'))


# TEST SUITE - DOCSTRING
# test_result = doctest.testmod()
# st.write('Suite for all docstring tests:', test_result)
