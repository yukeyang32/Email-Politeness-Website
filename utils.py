"""
Usage: utils.py

Contains utility helper functions for app.py
"""

import datetime
from politeness.api_util import get_scores_strategies_token_indices
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import re

analyzer = SentimentIntensityAnalyzer()

def score_text(text):
    """
    Score politeness of text.

    Parameters:
      text (string): a text message

    Returns:
      score (string, float, float): politeness information
    """
    ret = get_scores_strategies_token_indices(text)
    impolite_score = ret['score_impolite']
    polite_score = ret['score_polite']

    if impolite_score > 0.5:
      return ("impolite", impolite_score, polite_score)
    elif impolite_score < polite_score:
      return ("polite", impolite_score, polite_score)
    else:
      return ("neutral", impolite_score, polite_score)


def get_time():
    """
    Get current time of system.

    Returns:
      time (string): time in format of Y-m-d
    """
    gettime = str(datetime.datetime.now())[0:18]
    # time = datetime.datetime.strptime(get_time, '%Y-%m-%d %I:%M %p')
    time = datetime.datetime.strptime(gettime, '%Y-%m-%d %H:%M:%S').strftime('%I:%M %p')
    if time[0] == "0":
        time = time[1:]
    return time
    # %Y-%m-%d for Year month date

def find_sentiment(compound_score):
    """
    Function to classify sentiment score into a sentiment.
    The compound score is computed by summing the valence scores of each word in the lexicon,
    adjusted according to the rules, and then normalized to be between -1 and +1

    Parameters:
      score (float): sentiment score

    Returns:
      sentiment (string): either postiive, neutral, or negative
    """
    if compound_score >= 0.05:
      return "positive"
    elif compound_score > -0.05:
      return "neutral"
    else:
      return "negative"

def new_counts(message, old_total_words, old_total_messages):
    """
    Helper Function to update word count and message count

    Parameters:
      message (string): outgoing messagee
      old_total_words (int): old total number of words by user
      old_total_messages (int): old total messages by user

    Returns:
      ( new_total_words(int),
        new_total_messages (int) )
    """
    word_count = len(re.findall(r'\S+', message))
    new_total_words = old_total_words + word_count
    new_total_messages = old_total_messages + 1
    return (new_total_words, new_total_messages)

def new_politeness_sentiment_score(old_politeness, old_sentiment, total_messages, new_total_messages, new_politeness_score, new_sentiment_score, decimal):
    """
    Helper Function to update politeness and sentiment averages

    Parameters:
      old_politeness (float): old average politeness
      old_sentiment (float): old average sentiment
      total_messages (int): total of messages
      new_total_messages (int): total of messages including new message
      new_politeness (float): a new politeness score
      new_sentiment (float): a new sentiment score
      decimal (int): number of decimal points to display

    Returns:
      ( new_politeness(float),
        new_sentiment (float) )
    """
    # if old_politeness == -100. and old_sentiment == -100.:
    new_politeness = ((old_politeness * total_messages) + new_politeness_score)/new_total_messages
    new_sentiment = ((old_sentiment * total_messages) + new_sentiment_score)/new_total_messages
    print({'old_politeness':old_politeness, 'old_sentiment':old_sentiment, 'new_politeness':new_politeness, 'new_sentiment':new_sentiment, 'total_messages':total_messages, 'new_total_messages': new_total_messages, 'new_politeness_score': new_politeness_score, 'new_sentiment_score':new_sentiment_score})
    return (round(new_politeness, decimal), round(new_sentiment, decimal))

def get_scores(message, num_decimals):
  """
  Gets the politeness scores and statistics and rounds them to the num_decimals.
  """
  ret = score_text(message)
  senti = analyzer.polarity_scores(message) #sentiment
  pos, neu, neg, comp = senti['pos'], senti['neu'], senti['neg'], senti['compound']
  is_polite = ret[0]
  if is_polite != "impolite":
    impolite_index = []
    tokens = []
  else:
    impolite_index = ret[3]
    tokens = ret[4]
  impolite_score = round(ret[1], num_decimals)
  polite_score = round(ret[2], num_decimals)


  return is_polite, polite_score, impolite_score, impolite_index, tokens, pos, neu, neg, comp
