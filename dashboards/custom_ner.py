import pandas as pd
import numpy as np
import re
import string

import spacy
from spacy.matcher import Matcher, PhraseMatcher
from spacy.tokens import Span, Doc, Token
from spacy.pipeline import Sentencizer
from textacy.spacier import utils

import pkg_resources
from symspellpy import SymSpell, Verbosity

import streamlit as st


class EntityMatcher(object):
    name = "entity_matcher"

    def __init__(self, nlp, terms, label):
        self.vocab = nlp.vocab
        patterns = [nlp.make_doc(text) for text in terms]
        self.matcher = PhraseMatcher(nlp.vocab, attr='LOWER', validate=False)
        # TODO Assign label by dict lookup
        self.matcher.add(label, None, *patterns)

    def __call__(self, doc):
        """Including check for conflicting ents.

        https://github.com/explosion/spaCy/issues/3608"""
        matches = self.matcher(doc)
        seen_tokens = set()
        new_entities = []
        entities = doc.ents
        for match_id, start, end in matches:
            # check for conflicting ents
            if start not in seen_tokens and end not in seen_tokens:
                new_entities.append(Span(doc, start, end, label=match_id))
                entities = [e for e in entities if not (e.start < end and e.end > start)]
                seen_tokens.update(range(start, end + 1))
        doc.ents = tuple(entities) + tuple(new_entities)
        return doc


###################

# # Create custom entity matcher - METHOD 1
# # Add list of terms NOUNS only??
# for keywords in BANK_TERMS.get("OTHER BANK"):
#     entity_matcher = EntityMatcher(nlp, keywords, "OTHER BANK")

# Create entity rules - METHOD 2
# Add entity patterns from dict

# entity_ruler = EntityRuler(nlp, overwrite_ents=True)
# for k, v in VERBS.items():
#     for pattern in v:
#         d = nlp.pipe(pattern)
#         entity_ruler.add_patterns([{"label": k.upper(), "pattern": next(d)[0].lemma_}])

# for k, v in BANK_TERMS.items():
#     for pattern in v:
#         entity_ruler.add_patterns([{"label": k.upper(), "pattern": pattern}])


# METHOD 3
class EntMatcher(object):

    def __init__(self, dictionary, pattern, nlp):
        self.matcher = Matcher(nlp.vocab, validate=True)
        self.dictionary = dictionary
        if pattern:
            self.pattern = pattern
        else:
            self.pattern = lambda x: [{'LEMMA': {'IN': x}, 'POS': {'IN': ['VERB', 'NOUN', '']}}]
        self._add_match()
        # https://spacy.io/usage/processing-pipelines#custom-components-attributes
        # Token.set_extension("IS_PRODUCT", default='', force=True)
        # Doc.set_extension("HAS_PRODUCT", getter=self.has_product, force=True)
        # Span.set_extension("HAS_PRODUCT", getter=self.has_product, force=True)

    def _add_match(self):
        for LABEL, verbs in self.dictionary.items():
            try:
                self.matcher.add(f'{LABEL.upper()}', None, self.pattern(verbs))
            except Exception as err:
                st.write('matcher error:', err)

    def has_product(self, tokens):
        """Getter for Doc and Span attributes. Returns True if one of the tokens
        is a country. Since the getter is only called when we access the
        attribute, we can refer to the Token's 'is_country' attribute here,
        which is already set in the processing step."""
        return any([t._.get("IS_PRODUCT") for t in tokens])

    def __call__(self, doc):
        """Including check for conflicting ents.

        https://github.com/explosion/spaCy/issues/3608"""
        matches = self.matcher(doc)
        seen_tokens = set()
        entities, new_entities = doc.ents, []
        for match_id, start, end in matches:
            # check for/overwrite conflicting ents
            if start not in seen_tokens and end -1 not in seen_tokens:
                new_entities.append(Span(doc, start, end, label=match_id))
                # entities = [e for e in entities if not (e.start < end and start < e.end)]  ### TODO
                entities = [e for e in entities if not (e.start < end and start < e.end)]
                # [e._.set('IS_PRODUCT', 'TBA') for e in new_entities]
                # [e._.set('IS_PRODUCT', '') for e in entities]
                seen_tokens.update(range(start, end))
        doc.ents = tuple(entities) + tuple(new_entities)
        return doc

# nlp = spacy.load("en_core_web_sm")
# terms = ("cat", "dog", "tree kangaroo", "giant sea spider")
# entity_matcher = EntityMatcher(nlp, terms, "ANIMAL")

# nlp.add_pipe(entity_matcher, after="ner")

# print(nlp.pipe_names)  # The components in the pipeline

# doc = nlp("This is a text about Barack Obama and a tree kangaroo")
# print([(ent.text, ent.label_) for ent in doc.ents])



class SVO(object):
    def __init__(self, nlp):
        """"""
        self.nlp = nlp
        self.sentencizer = Sentencizer()
        # https://github.com/explosion/spaCy/issues/3569
        try:
            self.nlp.add_pipe(self.sentencizer, first=True)
        except:
            # already added
            pass

    def __call__(self, text):
        """"""
        doc = self.nlp(text)
        svo = []

        for sent in doc.sents:
            chunks = ''

            # Return the main (non-auxiliary) verbs in a sentence.
            verbs = utils.get_main_verbs_of_sent(sent)

            for verb in verbs:
                # Filter negations
                negation = "".join([t.text for t in sent
                                           if t.dep_ == 'neg'
                                           if t.head == verb])
                # Return all subjects of a verb according to the dependency parse.
                subj = utils.get_subjects_of_verb(verb)

                # Return all objects of a verb according to the dependency parse,
                # including open clausal
                # Get noun chunks of verb
                obj = utils.get_objects_of_verb(verb)

                # Return document indexes spanning all (adjacent) tokens around a verb
                # that are auxiliary verbs or negations.
                start, end = utils.get_span_for_verb_auxiliaries(verb)
                aux = doc[start:end+1].as_doc().text
                for o in obj:
                    for nc in sent.noun_chunks:
                        # st.write('VERB', verb.text,
                        #     'OBJ HEAD:', o.head.text, 'OBJ:', o.text,
                        #     'NC HEAD:', nc.root.head.text, 'NC:', nc.text,
                        #     'NC ANC:', [a.text for a in nc.root.head.ancestors] )
                        if o.text in nc.text.split():
                            chunks += f' {nc.text}'
                            # st.write('CHUNK:', nc.text)
                # obj = " ".join([f"{nc.text}" for nc in sent.noun_chunks if obj.text in nc.text])
                snippet = f'{" ".join([s.text for s in subj])} {negation} {aux} {chunks}'
                svo.append(snippet)
        return '. '.join(svo)


class SpellCheck():

    def __init__(self, init_path=None):
        """Spelling checker: symspellpy==6.5.2.

        https://symspellpy.readthedocs.io/en/latest/examples/lookup.html#basic-usage.
        https://towardsdatascience.com/essential-text-correction-process-for-nlp-tasks-f731a025fcc3."""
        self.sym_spell = SymSpell(max_dictionary_edit_distance=2, prefix_length=7)
        self.set_dictionary_path(init_path)
        self.set_dictionary()
        # self.sym_spell.load_dictionary(self.path, term_index=0, count_index=1)


    def set_dictionary_path(self, path):
        if path:
            self.path = path
        else:
            self.path = pkg_resources.resource_filename("symspellpy",
                                                        "frequency_dictionary_en_82_765.txt")
        return self.path


    def set_df(self):
        self.df = pd.read_csv(self.path, sep=' ', header=None, dtype={0: str, 1: np.int})
        return self.df


    def set_dict(self):
        self.set_df()
        self.dictionary = {self.df.loc[i, 0]: self.df.loc[i, 1] for i in self.df.index}
        return self.dictionary


    def set_dictionary(self):
        self.sym_spell.load_dictionary(self.path, term_index=0, count_index=1)
        self.set_dict()
        return None


    def find(self, term):
        return self.dictionary.get(term, 'nothing found')


    def append_dict(self, df_custom, cust_path='./data/cust_freq_dict_en.txt'):
        """Add custom dictionary.

        df: [term, freq]"""
        df_init = self.set_df()
        try:
            df_custom = df_custom.replace([np.inf, -np.inf, np.nan], 99)
            df_custom[1] = df_custom[1].astype(int)
            df = pd.concat([df_init, df_custom], ignore_index=True)
        except Exception as err:
            st.write('something went wrong', err)
            return -1

        # Remove duplicate terms and sort on frequency
        df.drop_duplicates(subset=[0], keep='first', inplace=True)
        df.sort_values(by=[1], ascending=False, inplace=True)

        # Save & Load after adding custom dictionary
        self.set_dictionary_path(cust_path)
        df.to_csv(self.path, sep=' ', index=None, header=None)
        # self.sym_spell.load_dictionary(self.path, term_index=0, count_index=1)
        self.set_dictionary()
        return None


    def __call__(self, input_term, N=8):
        """lookup suggestions for single- and multi-word input strings"""
        # Check loner words (N chars) on possible concatenation
        # https://symspellpy.readthedocs.io/en/latest/api/symspellpy.html#symspellpy.symspellpy.Verbosity
        if (len(input_term.split(' '))) == 1 or (len(input_term) < N):
            suggestions = self.sym_spell.lookup(input_term,
                                                Verbosity.TOP,
                                                max_edit_distance=2,
                                                transfer_casing=True,
                                                include_unknown=True)
        else:
            # Punctuation get's lost!
            suggestions = self.sym_spell.lookup_compound(input_term,
                                                         max_edit_distance=2,
                                                         transfer_casing=True)
        # Suggestion term, term frequency, and edit distance
        # return [(sug.term, sug.count, sug.distance) for sug in suggestions]
        return [sug.term for sug in suggestions][0]
