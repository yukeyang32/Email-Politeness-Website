import os
import _pickle
import string
import nltk
import spacy
from itertools import chain
from collections import defaultdict
from nltk.stem.wordnet import WordNetLemmatizer
import pprint

#### PACKAGE IMPORTS ###########################################################
# from features.politeness_strategies import get_politeness_strategy_features
from .politeness_strategies import get_politeness_strategy_features

# Get the Local Directory to access support files.
LOCAL_DIR = os.path.split(__file__)[0]

DEBUG = False

def print_debug(*args, **kwargs):
  if DEBUG:
    print(*args, **kwargs)


class VectorizerRuntimeError(RuntimeError):
  def __init__(self, msg):
    super(VectorizerRuntimeError, self).__init__(msg)



def get_unigrams_and_bigrams(document, debug=False):
  """
  Grabs unigrams and bigrams from document sentences. NLTK does the work.
  """
  unigram_lists = list(map(lambda x: nltk.word_tokenize(x), document["sentences"]))
  #print_debug("list: ", list(unigram_lists))
  bigrams = list(chain(*list(map(lambda x: nltk.bigrams(x), unigram_lists))))
  unigrams = list(chain(*list(unigram_lists)))

  return unigrams, bigrams

def get_word_tokens_unigrams_bigrams(document, debug=False):
  """
  Grabs unigrams and bigrams from document sentences. NLTK does the work.
  """
  word_tokens = [nltk.word_tokenize(sentence) for sentence in document["sentences"]]
  #unigram_lists = list(map(lambda x: nltk.word_tokenize(x), document["sentences"]))
  #print_debug("list: ", list(unigram_lists))
  bigrams = list(chain(*list(map(lambda x: nltk.bigrams(x), word_tokens))))
  unigrams = list(chain(*list(word_tokens)))

  return word_tokens, unigrams, bigrams


class PolitenessFeatureVectorizer:
  """
  Return document features based on 1) unigrams, 2) bigrams, and 3) politeness
  strategies. Politeness strategies are inspired by the following papers and
  are modeled using dependency-parses.

    Penelope Brown and Stephen C. Levinson. 1978. Universals in language
      use: Politeness phenomena. In Esther N. Goody, editor, Questions and
      Politeness: Strategies in Social Interaction, pages 56–311,
      Cambridge. Cambridge University Press.

    Penelope Brown and Stephen C. Levinson. 1987. Politeness: some
        universals in language usage. Cambridge University Press.
  """
  UNIGRAMS_FILENAME = os.path.join(LOCAL_DIR, "featunigrams.p")
  BIGRAMS_FILENAME = os.path.join(LOCAL_DIR, "featbigrams.p")

  def __init__(self, debug=False):
    """
    Load pickled lists of unigram and bigram features. These lists can be
    generated using the training set and
    PolitenessFeatureVectorizer.generate_bow_features
    """
    global DEBUG
    DEBUG = debug
    self.unigrams = _pickle.load(open(self.UNIGRAMS_FILENAME, 'rb'),
                                 encoding='latin1', fix_imports=True)
    self.bigrams = _pickle.load(open(self.BIGRAMS_FILENAME, 'rb'),
                                encoding='latin1', fix_imports=True)

  def features_strategies_token_indices(self, document):
    return self.__features(document)

  def features_and_strategies(self, document):
    features, strategies, _ = self.__features(document)
    return features, strategies

  def features(self, document):
    ret, _, _ = self.__features(document)
    return ret

  def __features(self, document):
    """
    Given a document dictionary of the following form, return a dictionary
    of features.
      {
        "sentences": ["sent1 text", "sent2 text", ...],
        "parses": [
                    [sent1 dependency-parse list],
                    [sent2 dependency-parse list],
                    ...
                  ]
      }
    """
    feature_dict = {}
    # Add unigram, bigram features:
    feature_dict.update(self._get_term_features(document))
    # Add politeness strategy features:
    polite_features, polite_strategies, token_indices = get_politeness_strategy_features(document, debug=DEBUG)
    feature_dict.update(polite_features)
    return feature_dict, polite_strategies, token_indices

  def _get_term_features(self, document):
    # One binary feature per ngram in self.unigrams and self.bigrams
    #unigrams, bigrams = get_unigrams_and_bigrams(document)
    word_tokens, unigrams, bigrams = get_word_tokens_unigrams_bigrams(document)
    # Add unigrams to document for later use
    print_debug("!!!!!!", unigrams)
    document['word_tokens'] = word_tokens
    document['unigrams'] = unigrams
    unigrams, bigrams = set(unigrams), set(bigrams)
    f = {}
    f.update(dict(map(lambda x: ("UNIGRAM_" + str(x), 1 if x in unigrams else 0), self.unigrams)))
    f.update(dict(map(lambda x: ("BIGRAM_" + str(x), 1 if x in bigrams else 0), self.bigrams)))
    return f

  @staticmethod
  def preprocess(documents):
    nlp = spacy.load('en')

    if isinstance(documents, list):
      documents = [{"text" : text} for text in documents]

    for document in documents:
      document['sentences'] = nltk.sent_tokenize(document['text'])
      document['parses'] = []
      for s in document['sentences']:

        # Spacy inclues punctuation in dependency parsing, which would lead to errors in feature extraction
        bak = s
        s = ""
        for x in bak:
          if x in string.punctuation:
             s += " "
          else:
             s += x
        s = ' '.join(s.split())
        doc = nlp(s)#unicode(s, "utf-8"))
        cur = []
        #for sent in doc.sents:
        for sent in doc.sents:
          pos = sent.start
          for tok in sent:
            ele = "%s(%s-%d, %s-%d)"%(tok.dep_.lower(), tok.head.text, tok.head.i + 1 - pos, tok.text, tok.i + 1 - pos)
            cur.append(ele)
        document['parses'].append(cur)

      # document["word_tokens"], document['unigrams'], document['bigrams'] = get_word_tokens_unigrams_bigrams(document)
    return documents

  @staticmethod
  def generate_bow_features(documents, min_unigram_count=20, min_bigram_count=20):
      """
      Given a list of documents, compute and store a list of unigrams and
      bigrams with a frequency > min_unigram_count and > min_bigram_count,
      respectively. This method must be called prior to the first vectorizer
      instantiation. Documents must be of the form:
          {
              "sentences": [ "sent1 text", "sent2 text", ... ],
              "parses": [ ["dep(a, b)"], ["dep(c, d)"], ... ]
          }
      """
      punctuation = string.punctuation
      punctuation = punctuation.replace("?","").replace("!","")
      unigram_counts, bigram_counts = defaultdict(int), defaultdict(int)
      # Count unigrams and bigrams:
      for d in documents:
          unigrams, bigrams = get_unigrams_and_bigrams(d)
          # Count
          for w in unigrams:
              unigram_counts[w] += 1
          for w in bigrams:
              bigram_counts[w] += 1
      # Keep only ngrams that pass frequency threshold:
      unigram_features = []
      for key in unigram_counts.keys():
          if unigram_counts[key] > min_unigram_count:
              unigram_features.append(key)
      bigram_features = []
      for key in bigram_counts.keys():
          if bigram_counts[key] > min_bigram_count:
              bigram_features.append(key)
      # Save results:
      _pickle.dump(unigram_features, open(PolitenessFeatureVectorizer.UNIGRAMS_FILENAME, 'wb'))
      _pickle.dump(bigram_features, open(PolitenessFeatureVectorizer.BIGRAMS_FILENAME, 'wb'))

if __name__ == "__main__":
  # Extract features from test documents
  # from test_documents import TEST_DOCUMENTS

  vectorizer = PolitenessFeatureVectorizer()
  documents = ["Have you found the answer for your question? If yes would you please share it?", "Sorry :) I dont want to hack the system!! :) is there another way?", "What are you trying to do?  Why can\'t you just store the \"Range\"?", "This was supposed to have been moved to &lt;url&gt; per the cfd. why wasn\'t it moved?"]
  print(isinstance(documents, list))
  pprint.pprint(PolitenessFeatureVectorizer.preprocess(documents))

  # for doc in TEST_DOCUMENTS:
  #     f = vectorizer.features(doc)

  #     # print_debug summary of features that are present
  #     print_debug("\n====================")
  #     print_debug("Text: ", doc['text'])
  #     print_debug("\tUnigrams, Bigrams: %d" % len(filter(lambda x: f[x] > 0 and ("UNIGRAM_" in x or "BIGRAM_" in x), f.keys())))
  #     print_debug("\tPoliteness Strategies: \n\t\t%s" % "\n\t\t".join(filter(lambda x: f[x] > 0 and "feature_politeness_" in x, f.keys())))
  #     print_debug("\n")
