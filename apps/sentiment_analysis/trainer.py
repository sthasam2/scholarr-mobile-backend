import time
import os
from pathlib import Path

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB


module_dir=os.path.dirname(__file__)  # get current directory


class SentimentAnalysis:

    df = None
    words_df = None
    vectorizer = None
    X = None
    Y = None
    logreg = None
    bayes = None

    def _load_training_data(self):
        """Load Training Data"""
        try:
            if self.df is None:
                start = time.time()
                print("Loading Training data...")

                # print(Path(__file__).__str__())
                # df = pd.read_csv(file_dir + "/data/sentiment140-subset.csv", nrows=30000)
                df = pd.read_csv(
                    os.path.join(module_dir, "notebook/data/sentiment140-subset.csv"),
                    nrows=30000,
                )

                end = time.time()
                print(f"Completed Loading data.\nElasped Time: {end - start}")

            return df
        except Exception as error:
            raise error

    def _tfidf_vectorize_dataframe(self):
        """Vectorize Dataframe"""
        try:
            if self.df is None:
                print("Please load data first")
                raise TypeError("df empty. Please load data first)")

            df = self.df

            start = time.time()
            print("Tfidf Vectorizing Training data...")

            vectorizer = TfidfVectorizer(max_features=1000)
            vectors = vectorizer.fit_transform(df.text)
            words_df = pd.DataFrame(
                vectors.toarray(), columns=vectorizer.get_feature_names()
            )

            end = time.time()
            print(f"Completed Loading data.\nElasped Time: {end - start}")

            self.vectorizer = vectorizer
            self.words_df = words_df

            return dict(words_df=words_df, vectorizer=vectorizer)

        except Exception as error:
            raise error

    def _train_data(self):
        """Train Data"""

        try:
            if self.df is None:
                print("Please load data first")
                raise TypeError("df empty. Please load data first)")
            if self.words_df is None:
                print("Please vectorize data first")
                raise TypeError("words_df empty. Please vectorize loaded data first)")

            X = self.words_df
            Y = self.df.polarity

            start = time.time()
            print("Training Data using 1. logistic regression 2. Naive Bayes")

            print("Starting Logistic Regression...")
            logreg = LogisticRegression(C=1e9, solver="lbfgs", max_iter=1000)
            logreg.fit(X, Y)

            print("Starting Naive Bayes...")
            bayes = MultinomialNB()
            bayes.fit(X, Y)

            end = time.time()
            print(f"Completed Training data.\nElasped Time: {end - start}")

            self.X = X
            self.Y = Y
            self.logreg = logreg
            self.bayes = bayes

            return dict(X=X, Y=Y, logreg=logreg, bayes=bayes)

        except Exception as error:
            raise error

    def _vectorize_unknown(self, content_to_analyze):
        """ """
        try:
            if self.vectorizer is None:
                print("Please vectorize data first")
                raise TypeError("words_df empty. Please vectorize loaded data first)")

            vectorizer = self.vectorizer

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

    def calculate_sentiment(self, content_to_analyze):
        """ """
        try:
            if self.vectorizer is None:
                print("Please vectorize data first")
                raise TypeError("words_df empty. Please vectorize loaded data first)")

            if self.logreg is None or self.bayes is None:
                print("Please train data first")
                raise TypeError("logreg and bayes empty. Please train data first)")

            vectorized_unknown = self._vectorize_unknown(content_to_analyze)
            logreg = self.logreg
            bayes = self.bayes

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

    def __init__(self):
        """ """

        self._load_training_data()
        self._tfidf_vectorize_dataframe()
        self._train_data()


# sensisitivity_analyzer = SentimentAnalysis()


# def calculate_sensitivity_index(content):
#     """ """

#     return sensisitivity_analyzer.calculate_sentiment(content)
