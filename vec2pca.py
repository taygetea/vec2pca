from bs4 import BeautifulSoup
from gensim.models import Word2Vec
import logging
from nltk.corpus import stopwords
import nltk.data
import pandas as pd
import plac
import re
from sklearn.decomposition import PCA
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)


try:
    tokenizer = nltk.data.load("tokenizers/punkt/english.pickle")
except:
    import nltk.downloader
    downloader.download("punkt"
    tokenizer = nltk.data.load("tokenizers/punkt/english.pickle")



# convert a string of text to a list of words
def separate_words(sentence, remove_urls=True, remove_stopwords=False):

    if remove_urls:
        sentence = BeautifulSoup(sentence).get_text()

    wordlist = re.sub("[^a-zA-Z]", " ", sentence).lower().split()

    if remove_stopwords:
        stops = set(stopwords.words("english"))
        wordlist = [w for w in wordlist if w not in stops]

    return wordlist


# parse a document to sentences
def to_sentences(document, tokenizer, remove_stopwords=False, remove_urls=False):

    sentences = tokenizer.tokenize(document.strip())
    sentences = [separate_words(sentence, remove_stopwords, remove_urls)
                 for sentence in sentences if len(sentence) > 0]

    return sentences


# train a model
def train(sentences, features=100, mincount=100, workers=12, context=10,
        sample=1e-3, save=False, precomp=True):
    model = Word2Vec(sentences,
                     sg=1,
                     workers=workers,
                     size=features,
                     min_count=mincount,
                     window=context,
                     sample=sample)
    if precomp:
        model.init_sims(replace=True)
    if save:
        print(save)
        model.save("%s_%dfeatures_%dmin_words_%dcontext" % (save, features, mincount, context))
    print("Training complete. Output contains %d words with %d features" % (model.syn0.size, model.syn0[0].size))
    return model


def run_pca(df, outfile="components.csv", n_components=8):
    pca = PCA(n_components)
    pc = pca.fit_transform(df)
    component_names = ["PC"+str(x) for x in range(1,len(pc[0])+1)]
    df2 = pd.DataFrame(pc, index=df.index, columns=component_names)
    wordcomponents = pd.DataFrame([df2.sort_values(by=x).index for x in component_names]).transpose()
    concatted = pd.concat([wordcomponents.iloc[0:20,0:4],
                           pd.DataFrame(wordcomponents.columns[0:4]).transpose(),
                           wordcomponents.iloc[-20:,0:4]])
    print(concatted.to_string(index=False))

    if outfile:
        wordcomponents.to_csv(outfile)
    else:
        return wordcomponents

def main(fname, output):
    sentences = []
    inputdata = pd.Series(open(fname).readlines()).dropna()
    for document in inputdata:
        sentences += to_sentences(document, tokenizer)
    model = train(sentences, save=fname)
    keys = list(model.vocab.keys())
    df = pd.DataFrame(model[keys], index=keys)
    run_pca(df, outfile=output)


if __name__ == "__main__":
    # outputfile = "/home/olivia/datascience/jsmill_components.csv"
    # filename = "/home/olivia/datascience/d"
    # main(filename, outputfile)
    plac.call(main)
















