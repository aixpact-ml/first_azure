import streamlit as st
from streamlit import config
import spacy
from spacy import displacy
import os
from pathlib import Path
from weasyprint import HTML, CSS
from weasyprint.fonts import FontConfiguration

from ner_utils import pos_matcher
from ner_constants import POS

font_config = FontConfiguration()

PATH = "/_first_azure/data"
text = ''


@st.cache(allow_output_mutation=True, persist=True)
def load_vocab():
    """Load vocab."""
    return spacy.load("en_core_web_sm")

nlp = load_vocab()

# Add title on the page
st.title("Resume Analyzer")


def read_file(file, path=PATH):
    """Select from allowed files"""
    # st.markdown(file)
    with open(f'{path}/{file}', 'rb') as f:
        text = f.read().decode('utf-8')
    tagged_text = pos_matcher(text, nlp)

    pos_txt = spacy.displacy.render(tagged_text,
                                    style='ent',
                                    page=True,
                                    manual=True,
                                    options={'colors': POS})

    # fix breaktag: </b> to <b>
    pos_txt = pos_txt.replace('</b>', '<b>')

    # Set CSS for weasyprint
    css = [CSS(string='@page {size: A3; margin: 1cm; font-family: Titillium Web !important;}',
               font_config=font_config)]

    # Save as pdf
    output_path = Path(f'{PATH}/{file.split(".")[0]}_pos_cv.pdf')
    html = HTML(string=f'{pos_txt}')
    html.write_pdf(output_path, stylesheets=css)

    # Save as png
    output_path = Path(f'{PATH}/{file.split(".")[0]}_pos_cv.png')
    html = HTML(string=f'{pos_txt}')
    st.image(html.write_png(stylesheets=css),
                                caption='AIxPact Resumé Analyzer',
                                use_column_width=True)

    # Save as svg
    output_path = Path(f'{PATH}/{file.split(".")[0]}_pos_cv.svg')
    output_path.open("w", encoding="utf-8").write(pos_txt)

    return text


files = [f for f in os.listdir(PATH) if f.endswith(('txt', 'doc', 'docx'))]
read_file(st.selectbox("select file: ", files))

