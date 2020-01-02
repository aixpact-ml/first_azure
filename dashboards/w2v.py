from gensim.models import Word2Vec
from gensim.models import KeyedVectors


with open("./data/utters.csv", 'r') as f:
    sentences = f.read()

model = Word2Vec(sentences=sentences,
                 size=100,
                 window=5,
                 min_count=1,
                 workers=-1,
                 sg=1)

model.save("w2c.vec")

# https://stackoverflow.com/questions/27659985/error-utf8-codec-cant-decode-byte-0x80-in-position-0-invalid-start-byte
utter_dict = Word2Vec.load('w2c.vec')
# utter_dict = KeyedVectors.load_word2vec_format('w2c.vec', binary=True, unicode_errors='ignore')
# utter_dict = KeyedVectors.load_word2vec_format('w2c.vec')
