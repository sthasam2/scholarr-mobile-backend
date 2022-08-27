import re
from random import choice
from string import ascii_lowercase

import joblib
import numpy as np
import plotly.graph_objects as go
import pypandoc
from nltk.lm import WittenBellInterpolated
from nltk.tokenize import word_tokenize
from nltk.util import everygrams, pad_sequence
from pdfminer.high_level import extract_text

from apps.classroom_contents.models import (
    ClassworkHasSubmission,
    Submission,
    SubmissionHasAttachment,
)
from apps.plagiarism_detector.models import PlagiarismInfo
from configs.definitions import BASE_DIR, MEDIA_URL

Ngram_N = 10


def open_file(attachment_path, content_type):
    """ """

    extension = attachment_path.split(".")[1]
    if content_type == "application/pdf" or extension == "pdf":
        with open(attachment_path, "rb") as f:
            train_text = extract_text(f)
        f.close()
    else:
        train_text = pypandoc.convert_file(attachment_path, "plain")
    return train_text


def clean_text(raw_text):
    """ """

    cleaned_text = re.sub(r"\[.*\]|\{.*\}", "", raw_text)
    cleaned_text = re.sub(r"[^\w\s]", "", cleaned_text)
    return cleaned_text


def clean_html(raw_html):
    cleanr = re.compile(
        "<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});|(?:\n|\t|\r|\xa0|\x0c)"
    )
    cleantext = re.sub(cleanr, "", raw_html)
    return cleantext


def create_model(raw_text):
    train_text = clean_text(raw_text)
    train_text = clean_html(train_text)
    n = Ngram_N

    training_data = list(
        pad_sequence(word_tokenize(train_text), n, pad_left=True, left_pad_symbol="<s>")
    )
    ngrams = list(everygrams(training_data, max_len=n))
    model = WittenBellInterpolated(n)
    model.fit([ngrams], vocabulary_text=training_data)
    return training_data, model


def calculate_scores(testing_tokenized_data, model):
    n = Ngram_N
    scores = []
    for i, item in enumerate(testing_tokenized_data[n - 1 :]):
        s = model.score(item, testing_tokenized_data[i : i + n - 1])
        scores.append(s)
    scores_np = np.array(scores)
    arr_sum = np.sum(scores_np)
    return (arr_sum / len(scores_np)) * 100


def random_string() -> str:
    """
    generates random string
    """
    return "".join(choice(ascii_lowercase) for i in range(15))


def joblib_dump(model):
    path = str(BASE_DIR) + "/media/trained_models/" + random_string() + ".sav"
    joblib.dump(model, path)
    return path


def joblib_load(item_location):
    return joblib.load(item_location)


def check_plagiarism(attachment_instance, submission):
    """"""
    # hello =

    classwork = submission.submission_classwork.get().classwork

    other_submissions_list = ClassworkHasSubmission.objects.filter(classwork=classwork)[
        :5
    ]
    target_submissions = [item.submission for item in other_submissions_list]

    training_model = joblib_load(attachment_instance.model_dump)

    for target_submission in target_submissions:
        if not target_submission.attachments:
            break

        attachment = target_submission.submission_attachment.get().attachment
        tokenized_data = joblib_load(attachment.tokenized_dump)

        plagiarism_score = calculate_scores(tokenized_data, training_model)

        PlagiarismInfo.objects.create(
            submission_agent=submission,
            submission_target=target_submission,
            percentage_plagiarized=plagiarism_score,
        )

    return
