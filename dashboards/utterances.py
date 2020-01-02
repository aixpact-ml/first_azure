
# from flask import session
import os
import re
import string
from collections import Counter, defaultdict
import pandas as pd
import numpy as np
from pathlib import Path
import altair as alt
import streamlit as st
from vega_datasets import data

import spacy
from spacy.tokens import Doc, Span, Token
from spacy import displacy
from spacy.pipeline import EntityRuler

from weasyprint import HTML, CSS
from weasyprint.fonts import FontConfiguration

from utter_utils import pos_matcher, text_entities
from utter_dicts import POS
from custom_ner import EntityMatcher, SVO, SpellCheck

font_config = FontConfiguration()

# from pipe import spell_checker, ent_matcher_verbs
from pipe import nlp, svo, STOPWORDS, VERBS, OOV_TERMS, BANK_TERMS, TAGS, IDX_TAGS

#######################



def annomize(doc, nlp=nlp):
    redacted = []
    for t in doc:
        if t.ent_type_ in ['REDACTED', 'PERSON', 'ORG', 'GPE', 'MONEY', 'QUANTITY', 'CARDINAL']:
            redacted.append(t.ent_type_)
        else:
            redacted.append(t.text)
    return nlp(' '.join(redacted))


############## setup

st.title("Labeling utterances")

PATH = Path('./data')
path = os.path.join('./data', 'utters.csv')
text = ''


############## read data

# Read multiple sheets from the same file
xls_path = os.path.join('./data', 'ph-team-labelling.xlsm')
xls = pd.ExcelFile(xls_path)
df = pd.read_excel(xls, 'data_')
df['utterance'] = df['INITIAL_MESSAGE']
# st.dataframe(df)

############## input

# utter = st.text_input("Utterance...", 'your text here...')
idx = st.number_input('index: ') # st.selectbox('Select utterance:', df.index)
utter = df.loc[int(idx), 'utterance']
# st.write('TOKENS:',[ut.text for ut in nlp(correct_spacing(utter))])

# utter = correct_spacing(utter)
st.write(utter)
doc = nlp(utter)
doc = annomize(doc)
st.write(' '.join([t.text for t in doc]))

################ SET TAGS IS_SOMETHING

def set_tag(LABEL, terms):
    getter = lambda t: t.ent_type_ if t.ent_type_ in terms else ''
    Token.set_extension(f'IS_{LABEL}', getter=getter, force=True)

def get_tags(doc, LABEL):
    # return [(t.text, eval(f't._.IS_{tag}')) for t in doc]
    return ', '.join(set(t.ent_type_.lower() for t in doc if eval(f't._.IS_{LABEL}')))

for LABEL, terms in TAGS.items():
    set_tag(LABEL, terms)


###############

# token.lemma_, 'lemma', 'is_alpha', 'is_stop', token.is_alpha, token.is_stop,
pos_dep = pd.DataFrame([(token.text, token.norm_, token.lemma_, token._.IS_PRODUCT, token._.IS_ACTION, token.pos_, token.tag_, token.dep_, token.ent_type_,
            token.shape_, token.head.text, token.head.head.head.head.head.head.text) for token in doc
            if token.dep_ not in ['det', 'poss', 'case', 'prep', 'punct', 'cc', 'mark'] # , 'intj'
            # if token.dep_ not in ['nsubj', 'nsubjpass']
            if token.tag_ not in ['TO', 'PRP', 'CD', '_SP', 'SP_'] # 'UH',
            # if token.pos_ not in ['AUX']
            if token.head.head.head.head.lemma_.lower() not in ['thank', 'thanks', 'appreciate', 'hope']
            ])

pos_dep.columns = ['token', 'norm', 'lemma', 'PRODUCT', 'ACTION', 'pos', 'tag', 'dep', 'ent', 'shape', 'head', 'root']

# Sanity checks
# st.write(' '.join(t.text for t in doc))
# st.write(pos_dep)
# st.write(pos_dep.groupby(['root', 'ent'])['ent'].describe()['count'].unstack().fillna(0).T[1:])
# st.write(Counter(pos_dep.loc[:, 'ent']))

# for LABEL, terms in TAGS.items():
#     st.write(f'{LABEL}: {get_tags(doc, LABEL)}')

st.subheader(f'Label: {df.loc[idx, "topic"]}')

#######################

def softmax(x):
    """Softmax"""
    from scipy.special import softmax
    return softmax(x)



def similarity(token_a, keywords, score='maxi'):
    """Get max/average similarity
    Mean m/b normalised - less words result in higher score"""
    similarities = []
    doc = Doc(nlp.vocab, keywords)
    for token_b in doc:
        try:
            sim = token_a.similarity(token_b)
            similarities.append(sim)
        except:
            continue
    if score == 'norm_mean':
        score = np.mean(similarities + np.log(len(similarities) + 5))
    else:
        score = np.max(similarities)
    return score


def utter_sim(doc, labels, pos='VERB'):
    """Get most similar label"""
    assert type(labels) == type(dict())

    similarities = []
    for token in doc:
        for label, keywords in labels.items():
            try:
                if token.pos_ == pos:
                    sim_score = similarity(token, keywords)
                    similarities.append((label, sim_score))
            except:
                continue
    df = pd.DataFrame(similarities).groupby(0).mean().sort_values(1, ascending=False)
    df[1] = softmax(df.values)
    df.columns = ['softmax']
    return df


# st.write('Most similar verbs:', utter_sim(doc, VERBS, 'VERB'))
# st.write('Most similar ents:', utter_sim(doc, BANK_TERMS, 'NOUN'))
# st.write('Most similar ents:', utter_sim(Doc(nlp.vocab, doc.ents), BANK_TERMS, 'NOUN'))

dikt = defaultdict()
for e in doc.ents:
    if e.lemma_ not in dikt.get(e.label_, []):
        dikt[e.label_] = dikt.get(e.label_, []) + [e.lemma_]
df = pd.DataFrame((k + ' ', v) for k, v in dikt.items())
df.columns = ['LABEL', 'TERMS']
df['PRODUCT'] = [IDX_TAGS.get(l.strip(), 'OTHER') for l in df['LABEL']]
df = df.groupby('PRODUCT').sum()
df['TERMS'] = df['TERMS'].str.join(' ')
df = df.reindex(['WELCOME', 'ACTION', 'A_ATTR', 'PRODUCT', 'P_DET', 'P_ATTR', 'OTHER']).fillna('')
st.write(df)

# st.write('Entities - account/payment:', [f'{e.label_}: {e.text}'for e in doc.ents if e.label_ in ['ACCOUNT', 'PAYMENT']])

############################

def extract_excerpt(doc):
    # try:
    #     utter = re.sub('([.,!?()])', r'\1 ', str(utter))
    #     utter = re.sub('\s{2,}', ' ', utter)
    # except:
    #     utter = str(utter)
    return [" ".join([token.text
                for token in sent
                    if token.dep_[-3:] in ['omp', 'neg', 'aux', 'mod', 'obj',
                                            'ubj', 'OOT', 'und', 'ttr', 'ass', 'vcl']
                    # if token.head.head.head.head.lemma_.lower() not in ['thank', 'thanks', 'appreciate', 'hope']
                    ])
                for sent in doc.sents
                    if len(sent.text.split(' ')) > 2
            ]

def extract_action(doc):
    return [" ".join([f'{token.text}'
                for token in sent
                    if token.dep_[-3:] in ['omp', 'neg', 'aux', 'mod', 'ass']
                    ])
                for sent in doc.sents
                    if len(sent.text.split(' ')) > 2
            ]

def extract_prod(doc):
    return [" ".join([token.text
                for token in sent
                    if token.dep_[-3:] in ['obj', 'ubj', 'OOT', 'und', 'ttr',]])
                for sent in doc.sents
                    if len(sent.text.split(' ')) > 2
            ]

# df = df.fillna('nothing')
# for utter in df.loc[:, 'utterance']:
#     doc = nlp(utter)
#     st.write(utter, extract_excerpt(doc))
#     st.write(', '.join([t.text for t in doc]))
#     # st.write('PRODUCT:', extract_prod(doc))
#     # st.write('ACTION:', extract_action(doc))


############## SVO

# # svo = SVO(nlp)
# st.write(doc[:].as_doc().text)
# st.write('SVO: ', svo(utter))

# ##############

# # Get specific verbs
# freq = Counter([ut.lemma_.lower() for ut in doc if ut.pos_ == "VERB"
#                                                if ut.dep_ != "aux"
#                                                if ut.is_alpha
#                                                if ut.text.lower() not in STOPWORDS
#                                                if len(ut.text) > 2])
# # st.write(f'Verb frequency: {", ".join([str(k) + ":" + str(v) for k, v in freq.items()])}')


# # Get specific words
# freq = Counter([ut.lemma_.lower() for ut in doc if ut.lemma_.lower() not in STOPWORDS
#                                                if ut.dep_ != "aux"
#                                                if ut.pos_ != "VERB"
#                                                if ut.is_alpha
#                                                if ut.text.lower() not in STOPWORDS
#                                                if len(ut.text) > 1])
# # st.write(f'Word frequency: {", ".join([str(k) + ":" + str(v) for k, v in freq.items()])}')

# # IOU
# freq_account = Counter([ut.lemma_.lower() for ut in doc if ut.lemma_.lower() in BANK_TERMS['ACCOUNT']])
# freq_account = np.sum([1 for ut in nlp(utter) if ut.lemma_.lower() in BANK_TERMS['ACCOUNT']])
# # st.write('IoU account:', freq_account / len(utter))

# # IOU
# freq_payment = np.sum(Counter([ut.lemma_.lower() for ut in doc if ut.lemma_.lower() in BANK_TERMS['PAYMENT']]).values())
# freq_payment = np.sum([1 for ut in nlp(utter) if ut.lemma_.lower() in BANK_TERMS['PAYMENT']])
# # st.write('IoU payment:', freq_payment / len(utter))

# # Label for product family
# # st.subheader(f'Label: {"account" if ((freq_account + 1e-8) / (freq_payment + 1e-8)) >= 1 else "payment"} Topic: {df.loc[idx, "topic"]}')


# #
# noun_chunks = [nc.root.head.text + " " + nc.text for nc in doc.noun_chunks
#                         if nc.text not in STOPWORDS
#                         if len(nc.text) > 2]
# # st.subheader(f'Label attributes: {", ".join(noun_chunks)}')

# #
# # st.write([f'noun chunk: {nc.text} - head: {nc.root.head.text}' for nc in nlp(utter).noun_chunks])
# # [ancestors], [head], [chunk]
# st.write([f'[{ ", ".join([a.text for a in nc.root.head.ancestors if a.text.lower() not in STOPWORDS] ) }] \
#                                 {nc.root.head.dep_} {nc.root.dep_} \
#                                 [{nc.root.head.text}], [{nc.text}]'
#                                 for nc in doc.noun_chunks
#                                 if nc.text.lower() not in STOPWORDS
#                                 if len(nc.text) > 2
#                                 ])


# # IOU - customer is doing something which is where he needs bank to step in
# iou = []
# for k, v in VERBS.items():
#     freq_ = int(np.sum([1 for ut in doc if ut.lemma_.lower() in v]))
#     if freq_ > 0:
#         iou.append(-freq_)
# # st.subheader(f'Action attributes(sorted): {", ".join([list(VERBS.keys())[k] for k in np.argsort(iou)])}')


###############

# import textacy.ke
# # https://chartbeat-labs.github.io/textacy/getting_started/quickstart.html
# st.write(textacy.ke.textrank(nlp(utter), normalize="lemma", topn=10))

###############

# dep_labels = []
# st.write('some utterance about opening an account that failed')
# for token in nlp('some utterance about opening an account that failed'):
#     while token.head != token:
#         st.write(token.text, token.head.text)
#         dep_labels.append(token.dep_)
#         token = token.head


#################

def marker(text, chunk, label="LABEL", ut_start=0):
    """Dict for annotating text with colored tags.
    Match chunks and adjust for symbol tokens"""
    needle = chunk.text.lower()
    p = re.compile(f"{needle}.")
    m = p.search(text.lower() + ' ')
    match_ents = [{'start': m.start() + ut_start,
                   'end': m.end() + ut_start,
                   'label': label.upper()  # chunk.text.lower()
                   }]
    return match_ents

#############

# # Read utterances
# df = pd.read_csv(path, sep=';', header=None, error_bad_lines=False, warn_bad_lines=False)
# df.columns = ['utterance', 'entities']
# df.utterance.fillna('', inplace=True)
# all_text = '\t\n'.join(df.utterance.dropna().values).lower()

# # Entities
# df['entities'] = [text_entities(ut, nlp)[0] for ut in df.utterance]

# # Base for further analysis of POS, DEP, ...
# df['nlp'] = [nlp(ut) for ut in df.utterance.dropna().values]

# char_pointer = 0
# chunks, roots, heads, verbs, tests = [], [], [], [], []

# for i, ut in enumerate(df.nlp):
#     chunks_, roots_, heads_, verbs_, tests_ = [], [], [], [], []

#     # for ent in ut.ents:
#     #     st.write(ent.text, ent.start_char, ent.end_char, ent.label_)

#     for token in ut:
#         if token.pos_ == "VERB" and token.dep_ != "aux":
#             verbs_.append(token.text)
#             verb_chunk_tags = marker(ut.text, token, "ACTION", char_pointer)
#             MATCHED_ENTS2.extend(verb_chunk_tags)

#     for chunk in ut.noun_chunks:
#         if len(chunk) > 2:

#             chunks_.append(chunk.text.lower())
#             noun_chunk_tags = [{'start': chunk.start_char + char_pointer,
#                'end': chunk.end_char + char_pointer,
#                'label': "ENTITY"  #chunk.text.lower()  #label.upper()
#                }]
#             MATCHED_ENTS2.extend(noun_chunk_tags)

#             roots_.append(chunk.root.text.lower())
#             root_chunk_tags = marker(ut.text, chunk.root, "ROOT", char_pointer)
#             MATCHED_ENTS2.extend(root_chunk_tags)

#             heads_.append(chunk.root.head.text.lower())
#             head_chunk_tags = marker(ut.text, chunk.root.head, "HEAD", char_pointer)
#             MATCHED_ENTS2.extend(head_chunk_tags)

#             # tests_.append(f'{chunk.root.head.text.lower()}: {chunk.text.lower()}')

#     char_pointer += len(ut.text) + 2
#     chunks.append(chunks_)
#     roots.append(roots_)
#     heads.append(heads_)
#     verbs.append(verbs_)
#     tests.append(tests_)

# # Sort tags by start
# df_matches = pd.DataFrame(MATCHED_ENTS2).sort_values('start')
# M_E = []
# for i in df_matches.index:
#     M_E.append({
#                 'start': int(df_matches.loc[i, 'start']),
#                 'end': int(df_matches.loc[i, 'end']),
#                 'label': df_matches.loc[i, 'label']
#                 })
# st.write(M_E)
# # st.write('DEBUG', df_matches, df_matches.to_dict())

# df['chunks'] = chunks
# df['roots'] = roots
# df['heads'] = heads
# df['verbs'] = verbs
# df['tests'] = tests

# st.dataframe(df, width=800)


#################

# # Roots per sentence without stop words like Hi!
# df['roots'] = [[token.text for token in ut if token.dep_ == 'ROOT'
#                                            if token.text.lower() not in STOPWORDS]
#                 for ut in df.nlp]

# # Action verbs
# df['verbs'] = [[token.text for token in ut if token.pos_ == 'VERB'
#                                            if token.dep_ != 'aux'
#                                            if token.text.lower() not in STOPWORDS]
#                 for ut in df.nlp]

# # Merge Roots and action verbs
# df['action'] = [list(set(r) | set(v)) for r, v in zip(df['roots'], df['verbs'])]

# # Children of root
# df['children'] = [[[c for c in token.children if len(c) > 1]
#                     for token in ut if token.dep_ == 'ROOT'
#                                     if token.text.lower() not in STOPWORDS]
#                     for ut in df.nlp if ut != '']

# # Merge Action with children = nested list
# # df['action'] = [list(set(r) | set(v)) for r, v in zip(df['action'], df['children'])]

# # Noun chunks
# df['noun_chunks'] = [list(ut.noun_chunks) for ut in df.nlp]


####################

# roots = []
# for ut in df.utterance:
#     try:
#         for token in nlp(ut):
#             if token.dep_ == 'ROOT':
#                 roots.append(token.text)
#     except:
#         roots.append('')

# df['roots'] = roots
    # print(token.text, token.dep_, token.head.text, token.head.pos_,
    #         [child for child in token.children])


##################


# st.markdown(os.listdir("/_first_azure/"))
# file = f'{path}/{st.selectbox("select file: ", os.listdir(path))}'
# st.markdown(file)

# with open(file, 'r') as f:
#     text = f.read()[:500] + '....'

#     st.write(text)

# @st.cache(allow_output_mutation=True, persist=True)
# def load_vocab():
#     """Load vocab."""
#     return spacy.load("en_core_web_sm")


# nlp = load_vocab()


def tag_utter(utterances, path=PATH):
    """Select from allowed files"""

    # text = '\n\n'.join(utterances)
    # tagged_text = pos_matcher(utterances, nlp)
    # st.write(tagged_text)

    tagged_text = {'text': utterances + ' \n\n', 'ents': M_E, 'title': 'Utterance Labeler'}

    pos_txt = spacy.displacy.render(tagged_text,
                                    style='ent',
                                    page=True,
                                    manual=True,  ### use dict
                                    options={'colors': POS}
                                    )

    # fix breaktag: </b> to <b>
    pos_txt = pos_txt.replace('</b>', '<b>')

    # Set CSS for weasyprint
    css = [CSS(string='@page {size: A3; margin: 1cm; font-family: Titillium Web !important;}',
               font_config=font_config)]

    # Save as pdf
    output_path = Path(f'{PATH}/tagged_utter.pdf')
    html = HTML(string=f'{pos_txt}')
    html.write_pdf(output_path, stylesheets=css)

    # Save/show as png - NOTE CAIRO ERROR: length of doc is limited!
    # add <p style="page-break-before: always" ></p>
    output_path = Path(f'{PATH}/tagged_utter.png')
    html = HTML(string=f'{pos_txt}')
    st.image(html.write_png(stylesheets=css),
                                caption='Labeling utterances',
                                use_column_width=True)

    # Save as svg
    output_path = Path(f'{PATH}/tagged_utter.svg')
    output_path.open("w", encoding="utf-8").write(pos_txt)

    return text


# tag_utter(all_text)



###########################


# from _first_azure.config.settings import config

# from webapp.app import session

# def msg(msg):
#     from flask import current_app
#     from webapp.app import session
#     # print(session)
#     with current_app.app_context():
#         pass

# msg('test')

# st.title("AIxPact Dashboard Main")
# st.markdown(session.get("info", 'no session info'))

# name = st.text_input("What's your name?", '')
# st.write(name)

# st.write(os.getcwd())
# path = Path('./data')
# st.write(path)

# path = os.path.join('./data', file_temp)  # "/_first_azure/data"

# st.markdown(os.listdir("/_first_azure/"))
# file = f'{path}/{st.selectbox("select file: ", os.listdir(path))}'
# st.markdown(file)

# with open(file, 'r') as f:
#     text = f.read()[:500] + '....'

#     st.write(text)


# # Adds a checkbox to the sidebar
# add_selectbox = st.sidebar.checkbox(
#     'How would you like to be contacted?',
#     ('Email', 'Home phone', 'Mobile phone'))

# # Adds a slider to the sidebar
# add_slider = st.sidebar.slider(
#     'Select a range of values',
#     1.0, 100.0, (1.0, 50.0))

# # Amsterdam 52.379189, 4.899431 - km to latlon [71, 111]
# map_data = pd.DataFrame(
#     np.random.randn(5000, 2) * [add_slider[0]/71, add_slider[1]/71] + [52.379189, 4.899431],
#     columns=['lat', 'lon'])

# st.map(map_data)

