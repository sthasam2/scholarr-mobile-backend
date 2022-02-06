import os
import time

from joblib import load
import pandas as pd
from textblob import TextBlob

# Load trained models from dumps
module_dir = os.path.dirname(__file__)  # get current directory


logreg = load(
    os.path.join(module_dir, "notebook/trained_models/LogRegForSentimentAnalysis.sav")
)
bayes = load(
    os.path.join(module_dir, "notebook/trained_models/NaiBayesForSentimentAnalysis.sav")
)
vectorizer = load(
    os.path.join(module_dir, "notebook/trained_models/DfFittedVectorizer.sav")
)


def vectorize_unknown(content_to_analyze):
    """ """
    try:
        start = time.time()
        print("Tfidf Vectorizing data to be analyzed...")

        unknown = pd.DataFrame({"content": [content_to_analyze]})
        unknown_vectors = vectorizer.transform(unknown.content)
        unknown_words_df = pd.DataFrame(
            unknown_vectors.toarray(), columns=vectorizer.get_feature_names()
        )

        end = time.time()
        print(f"Completed Vectorizing data.\nElasped Time: {end - start}")

        return dict(unknown=unknown, unknown_words_df=unknown_words_df)

    except Exception as error:
        raise error


def calculate_sentiment_index(content_to_analyze):
    """ """
    try:
        #  Vectorize diven data
        vectorized_unknown = vectorize_unknown(content_to_analyze)

        unknown = vectorized_unknown["unknown"]
        unknown_words_df = vectorized_unknown["unknown_words_df"]

        # Logistic Regression predictions + probabilities
        unknown["pred_logreg"] = logreg.predict(unknown_words_df)
        unknown["pred_logreg_proba"] = logreg.predict_proba(unknown_words_df)[:, 1]

        # Bayes predictions + probabilities
        unknown["pred_bayes"] = bayes.predict(unknown_words_df)
        unknown["pred_bayes_proba"] = bayes.predict_proba(unknown_words_df)[:, 1]

        return (unknown["pred_bayes_proba"] + unknown["pred_logreg_proba"]) / 2

    except Exception as error:
        raise error


def calculate_textblob_value(content_to_analyze):
    """ """

    return TextBlob(content_to_analyze).sentiment.polarity
