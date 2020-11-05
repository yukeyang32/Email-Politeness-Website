from .model import score_strategies_token_indices
from .features.vectorizer import PolitenessFeatureVectorizer

def get_scores_strategies_token_indices(msg):
  for doc in PolitenessFeatureVectorizer.preprocess([msg]):
    probs, strategies, token_indices = score_strategies_token_indices(doc)
    sent_block = []
    for i in range(len(doc['word_tokens'])):
      sent_block.append(
        {
          "tokens": doc['word_tokens'][i],
          "involved_index": token_indices["involved"][i],
          "impolite_index": token_indices["impolite"][i],
          "polite_index": [],
        }
      )
    return {
      "score_polite"    : probs['polite'],
      "score_impolite"  : probs["impolite"],
      "strategies"      : strategies,
      "sentences": sent_block,
      # "token_indices"   : token_indices,
    }


if __name__ == "__main__":
  from test_documents import TEST_DOCUMENTS, TEST_TEXTS

  for text in TEST_TEXTS:
    print(get_scores_and_strategies(text))