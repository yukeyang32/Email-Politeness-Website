import csv
import json

from .features.vectorizer import PolitenessFeatureVectorizer

if __name__ == "__main__":
    """ csv file format
        Community, Id, Request, Score1, Score2, Score3, Score4, Score5, TurkId1, TurkId2, TurkId3, TurkId4, TurkId5, Normalized Score

        necessary info: Request-2, Normalized Score-13
    """

    with open("corpora/wikipedia.annotated.csv", "r") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        scores = []
        texts = []
        title = True
        for row in csv_reader:
            if title:
                title = False
                continue
            texts.append(row[2])
            scores.append(float(row[13]))

        vectorizer = PolitenessFeatureVectorizer()
        documents = vectorizer.preprocess(texts)
        for i,_ in enumerate(documents):
            documents[i]["score"] = scores[i]

    with open("corpora/wikipedia.parsed.json", "w") as out_file:
        json.dump(documents, out_file)
