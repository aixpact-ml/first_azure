import string
import re
import pandas as pd
import numpy as np
from collections import defaultdict, Counter

import spacy
from spacy import displacy
from spacy.matcher import Matcher
from spacy.lemmatizer import Lemmatizer
from spacy.lookups import Lookups

from ner_constants import ENNEAGRAM, HEADERS, MEASURABLE_RESULTS, OCEANS, POS, SKILLS, TECH_STACK, colors
# from config.settings import config

import streamlit as st

# MATCHED_ENTS = []


def lemmatize():
    """"""
    lookups = Lookups()
    lookups.add_table("lemma_rules", {"noun": [["s", ""]]})
    lemmatizer = Lemmatizer(lookups)
    return lemmatizer


def text_entities(text, nlp):
    """Extract entities: Person, Org, Product, Gpe"""

    symbol_reg = r'[|,\/,(,),/\n,/:]'
    text = re.sub(symbol_reg, ' ', text)

    doc = nlp(text) # .lower()
    entities = []
    for ent in doc.ents:
        if ent.label_ not in ['DATE', 'PERCENT', 'CARDINAL']:
            entities.append(str(ent).lower())
    return entities, Counter(entities).most_common()


def clean_ne(text, nlp):
    """Extract set of clean named entities and Counter from document."""

    from collections import defaultdict, Counter
    symbol_reg = r'[|,\/,(,),/\n,/:]'
    entities = defaultdict()
    doc = nlp(text)

    for ent in doc.ents:
        if ent.label_ not in ['DATE', 'PERCENT', 'CARDINAL']:
            ne = str(ent)
            ne_list = (ne.replace('\n', ',')
                         .replace('/', ',')
                         .replace(':', ',')
                         .replace('(', ',')
                         .replace(')', '')
                         .split(','))
            for ent in ne_list:
                entity = re.sub(symbol_reg, ' ', ent)
                strip = str(entity.lower().strip())
                if len(strip) > 1:
                    entities[strip] = entities.get(strip, 0) + 1
    return entities, Counter(entities).most_common()


def extract_regex(text, regex):
    """Extract set of URL's from document"""
    try:
        matches = re.finditer(regex, text, re.MULTILINE)
        matches = set([match.group() for match in matches])
    except AttributeError:
        matches = []
    return matches


def extract_headers(doc):
    """Extract headers from CV."""
    headers = pd.DataFrame(columns=['chunk', 'root', 'dependency', 'line', 'start', 'stop'])
    for line, sentence in enumerate(doc.sents):
        for i, chunk in enumerate(sentence.noun_chunks):
            if len(chunk) > 0:
                if set(chunk.lemma_.lower().split()) & set(HEADERS):
                    chunk_ = ' '.join(str(chunk).split())
                    if chunk.root.dep_ not in ['pobj', 'nsubj', 'dobj']:
                        headers.loc[f'{line}'] = (chunk_, chunk.root.head.text, chunk.root.dep_,
                                                  line, chunk.start, chunk.end)
    return headers


def extract_personalia(doc, nlp, named_entities):
    """Extract contact details.

    Levenshtein edit distance"""
    from nltk.metrics.distance import edit_distance
    EMAIL_REGEX = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}"
    PHONE_REGEX = r"\(?([/+,0]*)?(\d{2})?\)?[\s\.-]{0,2}?(\d{2,3})[\s\.-]{0,2}(\d{6,8})"
    LINKEDIN_REGEX = r"((?:http|https):\/\/)?(\w{2,3})?(linkedin\.com/)+(\w{2,3})(\/)+(\S)+"
    URL_REGEX = r"((?:http|https):\/\/)?((?:[\w-]+)(?:\.[\w-]+)+)(?:[\w.,@?^=%&amp;:\/~+#-]*[\w@?^=%&amp;\/~+#-])?"

    # TODO
    HEADERS_REGEX = r"\n+([a-zA-Z-]{5,25})+([\s\w-]{1,35})?([a-zA-Z0-9-\(\)]{4,25})?\n+"

    email = extract_regex(doc, EMAIL_REGEX)
    url = extract_regex(doc, URL_REGEX)
    phone = extract_regex(doc, PHONE_REGEX)
    linkedin = extract_regex(doc, LINKEDIN_REGEX)
    headers = extract_headers(nlp(doc)).chunk.unique().tolist()  # extract_regex(doc, HEADERS_REGEX)

    # Get named entity most similar to first email name
    if len(email) > 0:
        first_email = list(email)[0].split('@')[0]
    else:
        first_email = 'unknown@email.address'
    scores = []
    for ne in named_entities[:10]:
        scores.append(edit_distance(first_email, ne ,substitution_cost=1, transpositions=False))
    try:
        idx = np.argmax(scores)
        name = named_entities[idx]
    except:
        name = '<UNK> name not found'

    personalia = {'name': name,
                  'email': list(email), #[0],
                  'phone': list(phone),
                  'linkedIn': list(linkedin), #[0],
                  'web': list(url),
                  'headers': list(headers)
                 }
    df = pd.DataFrame(list(personalia.items()))
    df.columns = ['Personalia', 'Details']

    return df.set_index('Personalia')


def pos_matcher(text, nlp):
    """"""
    doc = nlp(text.lower())

    # Closure - Initiate matcher object and list of entities
    matcher = Matcher(nlp.vocab)
    MATCHED_ENTS = []

    def on_match(matcher, doc, i, matches, label='MATCH'):
        """Callback to built list of entity dictionaries in doc."""
        try:
            match_id, start, end = matches[i]
            span = doc[start:end]
            match_ents = [{'start': span.start_char,
                           'end': span.end_char,
                           'label': doc.vocab.strings[match_id]}]
            MATCHED_ENTS.extend(match_ents)
        except:
            pass
        return None


    def annotate_pos(DICT, **kwargs):
        """Annotate skills & emotions"""
        lemmatizer = lemmatize()
        for key in DICT.keys():
            for word in DICT[key]:
                try:
                    if kwargs.get('lemmatize', True):
                        lemma = lemmatizer(word, u"VERB")[0]
                    else:
                        lemma = word
                    pattern = kwargs.get('pattern', lambda w: [{'LEMMA': w.lower()}])
                    if kwargs.get('emotions', False):
                        matcher.add(key + str(emotion_dict.get(lemma, '')), on_match, pattern(lemma))
                    else:
                        matcher.add(key, on_match, pattern(lemma))
                except:
                    pass
        return None

    # Build annotator
    ner, ner_counter = clean_ne(text, nlp)
    DICT = {'NER': ner.keys()}
    annotate_pos(DICT)

    self_fn = lambda w: [{'LEMMA': w.lower()}]
    for k, v in SKILLS.items():
        DICT = {k.upper(): v}
        annotate_pos(DICT, pattern=self_fn)

    patt_fn = lambda w: [{'LEMMA': w}, {'POS': 'ADV', 'OP': '*'}, {'POS': 'ADJ'}]
    annotate_pos(MEASURABLE_RESULTS, pattern=patt_fn)

    self_fn = lambda w: [{'LEMMA': w.lower()}]
    DICT = {'SELF': ['i', 'me', 'my', 'mine']}
    annotate_pos(DICT, pattern=self_fn)

    DICT = {'NEGATIVE': ['late', 'little', 'fail', 'small', 'doubt', 'sorry', ]}
    annotate_pos(DICT)

    DICT = {'TECH_STACK': TECH_STACK}
    annotate_pos(DICT)

    named_entities, ne_counter = text_entities(text, nlp)
    personalia = extract_personalia(text, nlp, named_entities)
    assert personalia is not None, f'personalia error: {personalia}'
    st.dataframe(personalia)
    headers_fn = lambda w: [{'LEMMA': w.lower()},  {'POS': 'CCONJ', 'OP': '*'}, {'POS': 'VERB', 'OP': '*'}, {'POS': 'NOUN', 'OP': '*'}]
    DICT = {'HEADERS': personalia.loc['headers', 'Details']}
    annotate_pos(DICT, pattern=headers_fn)


    _ = matcher(doc)  # use matcher on doc
    tagged_text = {'text': text, 'ents': MATCHED_ENTS, 'title': 'AIxPact Resume Analyzer'}

    return tagged_text
