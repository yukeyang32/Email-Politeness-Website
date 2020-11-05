import codecs
import os
import re
import spacy
from itertools import chain

local_dir = os.path.split(__file__)[0]

# Load feedback analysis rules
neq_filename = os.path.join(local_dir, "inequality-basic.txt")
neq_words = set(map(lambda x: x.strip(), codecs.open(neq_filename, encoding='utf-8').read().splitlines()))

prof_filename = os.path.join(local_dir, "profanity-words.txt")
prof_words = set(map(lambda x: x.strip(), codecs.open(prof_filename, encoding='utf-8').read().splitlines()))

neg_filename = os.path.join(local_dir, "negative-words.txt")
neg_words = set(map(lambda x: x.strip(), codecs.open(neg_filename, encoding='utf-8').read().splitlines()))


parse_element_split_re = re.compile(r"([-\w!?]+)-(\d+)")
getleft = lambda p: parse_element_split_re.findall(p)[0][0].lower()
getleftpos = lambda p: int(parse_element_split_re.findall(p)[0][1])
getright = lambda p: parse_element_split_re.findall(p)[1][0].lower()
getrightpos = lambda p: int(parse_element_split_re.findall(p)[1][1])
remove_numbers = lambda p: re.sub(r"\-(\d+)" , "", p)
getdeptag = lambda p: p.split("(")[0]


def rules_check(rule_list, s):
    """
    Given a rule and a sentence, find all the matched indices.
    Return a list of tuples, with each tuple containing the start
      and end character index in the sentence.
    """
    matched_indices = list()
    for w in rule_list:
        w = w.replace('*', '\*')   ## avoid regex special characters
        for it in re.finditer(r'\b({})\b'.format(w), s):
            matched_indices.append((it.start(), it.end()))
    return matched_indices



###### STRATEGIES BASED ON PARSES ######
pleasestart_helper = lambda p: (getleftpos(p) == 1 and getleft(p) == "please") or (getrightpos(p) == 1 and getright(p) == "please")

def pleasestart(p, s=None, type="helper"):
    if type == "helper":
        return pleasestart_helper(p)
    loc = re.search(r'\b({})\b'.format("please"), s)
    return [(loc.start(), loc.end())]
pleasestart.__name__ = "Please start"


why_rule = ["what","why","who","how"]
why_helper = lambda p: (getleftpos(p) in (1,2) and getleft(p) in why_rule) or (getrightpos(p) in (1,2) and getright(p) in why_rule)

def why(p, s=None, type="helper"):
    if type == "helper":
        return why_helper(p)
    res = list()
    for w in why_rule:
        loc = re.search(r'\b({})\b'.format(w), s)
        if loc is not None:
            res.append( (loc.start(), loc.end()) )
    return res
why.__name__ = "Direct question"


conj_rule = ["so","then","and","but","or"]
conj_helper = lambda p: (getleftpos(p) == 1 and getleft(p) in conj_rule) or (getrightpos(p) == 1 and getright(p) in conj_rule)

def conj(p, s=None, type="helper"):
    if type == "helper":
        return conj_helper(p)
    res = list()
    for w in conj_rule:
        loc = re.search(r'\b({})\b'.format(w), s)
        if loc is not None:
            res.append( (loc.start(), loc.end()) )
    return res
conj.__name__ = "Direct start"


secondperson_rule = ["you","your","yours","yourself"]
secondperson_start_helper = lambda p: (getleftpos(p) == 1 and getleft(p) in secondperson_rule) or (getrightpos(p) == 1 and getright(p) in secondperson_rule)

def secondperson_start(p, s=None, type="helper"):
    if type == "helper":
        return secondperson_start_helper(p)
    res = list()
    for w in secondperson_rule:
        loc = re.search(r'\b({})\b'.format(w), s)
        if loc is not None:
            res.append( (loc.start(), loc.end()) )
    return res
secondperson_start.__name__ = "2nd person start"


really_rule = ["really", "actually", "honestly", "surely"]
really_helper = lambda p: (getright(p) == "fact" and getdeptag(p) == "prep_in") or remove_numbers(p) in ("det(point, the)","det(reality, the)","det(truth, the)") or len(set([getleft(p), getright(p)]).intersection(really_rule)) > 0

def really(p, s=None, type="helper"):
    if type == "helper":
        return really_helper(p)
    res = list()
    nlp = spacy.load('en')
    doc = nlp(s)
    sent = next(doc.sents)
    char_indices = list()
    idx = 0
    for token in sent:
        char_indices.append(idx)
        idx += len(token)
        if token.whitespace_:
            idx += 1
    if getright(p) == "fact" and getdeptag(p) == "prep_in":
        loc = char_indices[getrightpos(p)-1]
        res.append( (loc, loc+5) )
    if remove_numbers(p) in ("det(point, the)","det(reality, the)","det(truth, the)"):
        loc1 = char_indices[getrightpos(p)-1]
        loc2 = char_indices[getleftpos(p)-1]
        res.append( (loc1, loc1+len(getright(p))+1) )
        res.append( (loc2, loc2+len(getleft(p))+1) )
        # res.append( (loc1, loc2+len(getleft(p))+1) )
    if len(set([getleft(p), getright(p)]).intersection(really_rule)) > 0:
        for w in really_rule:
            loc = re.search(r'\b({})\b'.format(w), s)
            if loc is not None:
                res.append( (loc.start(), loc.end()) )
    return res
really.__name__ = "Factuality"


###### STRATEGIES BASED ON TOKENS ######
inequality = lambda s: rules_check(neq_words, s)
inequality.__name__ = "HASINEQUALITY"

profanity = lambda s: rules_check(prof_words, s)
profanity.__name__ = "HASPROFANITY"

has_negative = lambda s: rules_check(neg_words, s)
has_negative.__name__ = "HASNEGATIVE"


###### CONSTRUCT STRATEGIES ######
DEPENDENCY_STRATEGIES = [pleasestart, why, conj, secondperson_start, really]
TEXT_STRATEGIES = [inequality, profanity, has_negative]


# Convert function name to feature name
fnc2feature_name = lambda f: "feedback_feature_==%s==" % f.__name__.replace(" ","_")
FEEDBACK_FEATURES = map(fnc2feature_name, chain(DEPENDENCY_STRATEGIES, TEXT_STRATEGIES))


def check_strategy(elem, strategy_func, type="TEXT"):
    flag = False
    matchings = list()
    ret = strategy_func(elem)
    if ret and type=="TEXT":
        matchings.extend(ret)
        flag = True
    elif ret and type=="DEPENDENCY":
        matchings.append(elem)
        flag = True
    return matchings if flag else None

def get_feedback(doc):
    """
    Strategies feedback of text.

    Parameters:
        given document with single sentence in form:
            {
                "sentences": ["sentence"],
                "parses": [
                            ["nsubj(dont-5, I-4)", ...]
                          ],
                "unigrams": ["a", "b", "c", ...]
            }

    Returns:
        strategies [("str1", [(index1), (index2), ...]), ("str1", [(index1), (index2), ...]), ...]
        # each index is a tuple of the start and end character index
    """
    if "sentences" not in doc or "parses" not in doc:
        return {f: 0 for f in FEEDBACK_FEATURES}

    strategies = list()

    sentence = doc["sentences"][0].lower()
    parses = doc['parses'][0]
    for fnc in DEPENDENCY_STRATEGIES:
        flag = False
        for p in parses:
            if check_strategy(p, fnc, "DEPENDENCY") is not None:
                flag = True
                break
        if flag:
            ret = fnc(p, sentence, "index")
            strategies.append( (fnc.__name__, ret) )

    for fnc in TEXT_STRATEGIES:
        ret = check_strategy(sentence, fnc, "TEXT")
        if ret is not None:
            strategies.append( (fnc.__name__, ret) )
    return strategies
