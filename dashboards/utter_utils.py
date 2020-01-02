import string
import re
import pandas as pd
import numpy as np
from collections import defaultdict, Counter

import spacy
from spacy import displacy
from spacy.matcher import Matcher, PhraseMatcher
from spacy.lemmatizer import Lemmatizer
from spacy.lookups import Lookups

from utter_dicts import FAMILY, PRODUCT_ATTR, CHANNEL, ACTION, ACTION_ATTR, POS, COLORS
# from config.settings import config

import streamlit as st

STOPWORDS = ['sir', 'pls', 'please', 'thanks', 'thank', 'hi', 'hello', 'howdy', 'hi!']


def lemmatize():
    """"""
    lookups = Lookups()
    lookups.add_table("lemma_rules", {"noun": [["s", ""]]})
    lemmatizer = Lemmatizer(lookups)
    return lemmatizer


def text_entities(text, nlp):
    """Extract entities: Person, Org, Product, Gpe"""
    try:
        symbol_reg = r'[|,\/,(,),/\n,/:]'
        text = re.sub(symbol_reg, ' ', text)

        doc = nlp(text)
        entities = []
        for ent in doc.ents:
            entities.append(str(ent).lower())
        return entities, Counter(entities).most_common()
    except:
        return [], Counter()


def extract_regex(text, regex):
    """Extract set of URL's from document"""
    try:
        matches = re.finditer(regex, text, re.MULTILINE)
        matches = set([match.group() for match in matches])
    except AttributeError:
        matches = []
    return matches


def root_action(utterance, nlp):
    """"""
    NEGATIONS = ['no', 'not', "n't", 'without', 'fail', 'don', "don't"]

    # nlp_utts = nlp(utterances.lower())
    nlp_utts = nlp(utterance.lower())

    # Roots per sentence without stop words like Hi!
    roots = [token.lemma_ for token in nlp_utts if token.dep_ == 'ROOT'
                                         if token.lemma_.lower() not in STOPWORDS]

    # Action verbs
    verbs = [token.lemma_ for token in nlp_utts if token.pos_ == 'VERB'
                                         if token.dep_ != 'aux'
                                         if token.lemma_.lower() not in STOPWORDS]

    # Action verbs
    negs = [token.lemma_ for token in nlp_utts
                                         if token.lemma_.lower() in NEGATIONS]
    # st.write('negs', negs)
    # Merge Roots and action verbs
    action = set(roots + verbs + negs)
    st.write(len(roots), roots)
    st.write(len(verbs), verbs)
    st.write(len(action), action)

    return action


def pos_matcher(text, nlp):
    """"""
    doc = nlp(text.lower())
    # Closure - Initiate matcher object and list of entities
    matcher = Matcher(nlp.vocab)

    MATCHED_ENTS = []

    def on_match(matcher, doc, i, matches, label='MATCH'):
        """Callback to built list of entity dictionaries in doc.

        Fails silently on: ... driver's ...???"""
        try:
            match_id, start, end = matches[i]
            span = doc[start:end]
            match_ents = [{'start': span.start_char,
                           'end': span.end_char,
                           'label': doc.vocab.strings[match_id]}]
            MATCHED_ENTS.extend(match_ents)
        except Exception as err:
            pass
        return None

    def annotate_pos(DICT, **kwargs):
        """Annotate skills & emotions"""
        lemmatizer = lemmatize()
        for key in DICT.keys():
            for word in DICT[key]:
                try:
                    if kwargs.get('lemmatize', True):
                        lemma = lemmatizer(word, u"VERB")[0]  # VERB only?
                    else:
                        lemma = word
                    pattern = kwargs.get('pattern', lambda w: [{'LEMMA': w.lower()}])
                    matcher.add(key, on_match, pattern(lemma))
                except:
                    pass
        return None

    # Build annotators

    # Noun chunks > 2 (not: I, me, etc.)
    # TODO "driver's license" not annotated....
    noun_chunks = [nc for nc in doc.noun_chunks if len(nc.text) > 2]

    for e, nc in enumerate(noun_chunks):
        nc_fn, nc_root_fn, nc_head_fn, nc_words = [], [], [], []

        # Composite patterns for noun chunks
        words = nc.text.split(' ')
        for i, w in enumerate(words):
            w = w.lower()
            nc_words.append(w)
            nc_fn.append({'LOWER': w})

        for i, w in enumerate(nc.root.text):
            nc_root_fn.append({'LOWER': w.lower()})
        nc_head_fn.append({'LOWER': nc.root.head.text.lower()})

        # st.write(f'ENTITY', ' '.join(nc_words), words, nc_fn)
        matcher.add(f'ENTITY', on_match, nc_fn)
        matcher.add(f'ENTITY_ROOT', on_match, nc_root_fn)
        matcher.add(f'ENTITY_HEAD', on_match, nc_head_fn)


    # root_verbs = root_action(text, nlp)
    # DICT = {'ROOT': root_verbs}
    # annotate_pos(DICT)


    # self_fn = lambda w: [{'LEMMA': w.lower()}]
    # for k, v in FAMILY.items():
    #     DICT = {k.upper(): v}
    #     annotate_pos(DICT, pattern=self_fn)

    # self_fn = lambda w: [{'LEMMA': w.lower()}]
    # for k, v in PRODUCT_ATTR.items():
    #     DICT = {k.upper(): v}
    #     annotate_pos(DICT, pattern=self_fn)

    # self_fn = lambda w: [{'LEMMA': w.lower()}]
    # for k, v in CHANNEL.items():
    #     DICT = {k.upper(): v}
    #     annotate_pos(DICT, pattern=self_fn)

    # self_fn = lambda w: [{'LEMMA': w.lower()}]
    # for k, v in ACTION.items():
    #     DICT = {k.upper(): v}
    #     annotate_pos(DICT, pattern=self_fn)

    # self_fn = lambda w: [{'LEMMA': w.lower()}]
    # for k, v in ACTION_ATTR.items():
    #     DICT = {k.upper(): v}
    #     annotate_pos(DICT, pattern=self_fn)

    # # TODO Get root / verbs / nouns
    # patt_fn = lambda w: [{'LEMMA': w.lower()}, {'POS': 'ADV', 'OP': '*'}, {'POS': 'ADJ'}]
    # DICT = {'STOP': STOPWORDS}
    # annotate_pos(DICT, pattern=patt_fn)

    # self_fn = lambda w: [{'LEMMA': w.lower()}]
    # DICT = {'SELF': ['i', 'me', 'my', 'mine']}
    # annotate_pos(DICT, pattern=self_fn)

    # DICT = {'NEGATIVE': ['late', 'little', 'fail', 'small', 'doubt', 'sorry', ]}
    # annotate_pos(DICT)

    # DICT = {'TECH_STACK': TECH_STACK}
    # annotate_pos(DICT)

    # named_entities, ne_counter = text_entities(text, nlp)
    # personalia = extract_personalia(text, nlp, named_entities)
    # assert personalia is not None, f'personalia error: {personalia}'
    # st.dataframe(personalia)
    # headers_fn = lambda w: [{'LEMMA': w.lower()},  {'POS': 'CCONJ', 'OP': '*'}, {'POS': 'VERB', 'OP': '*'}, {'POS': 'NOUN', 'OP': '*'}]
    # DICT = {'HEADERS': personalia.loc['headers', 'Details']}
    # annotate_pos(DICT, pattern=headers_fn)


    _ = matcher(doc)  # use matcher on doc
    tagged_text = {'text': text, 'ents': MATCHED_ENTS, 'title': 'Utterance Labeler'}

    return tagged_text
