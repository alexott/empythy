import csv
import os
import sys

from sklearn.base import BaseEstimator, TransformerMixin
#from sklearn.cross_validation import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

import pickle

from empythy import utils

if sys.__stdin__.isatty():
    module_path = os.path.dirname(sys.argv[0])
else:
    module_path = os.path.dirname(__file__)


class EmpathyMachines(object):

    def __init__(self):
        pass


    def train(self, corpus='Twitter', corpus_array=None, print_analytics_results=False, verbose=True, file_name=None):
        corpus_name = corpus.lower()

        if print_analytics_results:
            verbose = True

        if verbose:
            print('Loading the corpus')

        if corpus_name == 'custom':
            raw_data = corpus_array

        elif corpus_name == 'twitter':
            corpus_file_path = os.path.join(module_path, 'corpora', 'aggregatedCorpusCleanedAndFiltered.csv')
            raw_data = utils.load_dataset(corpus_file_path)

        elif corpus_name == 'moviereviews':
            raw_data = utils.load_movie_reviews()

        confidence_threshold = None
        if corpus_name == 'twitter':
            confidence_threshold = 0.3

        # This cannot be baked into our pipeline, because we only apply it to our training data, not our predictions data
        corpus_strings, sentiments = utils.clean_initial_data(raw_data, confidence_threshold=confidence_threshold)

        ppl = Pipeline([
            ('tfidf', TfidfVectorizer()),
            ('clf', LogisticRegression())
        ])

        # set all our parameters at once.
        # the step of the pipeline we are setting parameters for is the name__ part, and the parameter we are setting is what comes after the __
        ppl.set_params(
            # if we fail to parse a given character, just ignore it
            tfidf__decode_error='ignore',
            # strip accents from characters
            tfidf__strip_accents='unicode',
            # break the string apart into words, not characters
            tfidf__analyzer='word',
            # get words in groups that range in length from 1 - 4. So "I love DoorDash" turns into "I", "love", "I love", "I love DoorDash"...
            tfidf__ngram_range=(1,4),
            # instead of using pre-defined stopwords, ignore all words that have an intra-document frequency > 0.7
            # (ignore all words/phrases that appear in more than 70% of our documents)
            tfidf__max_df=0.7,
            # stop_words are commonly used words that don't likely differentiate a message ('of','me','a', etc.)
            tfidf__stop_words='english',
            # convert all characters to lowercase
            tfidf__lowercase=True,
            # keep only this many features (all features if None)
            tfidf__max_features=20000,
            # smooth idf weights to prevent zero divisions
            tfidf__smooth_idf=True
        )

        if verbose:
            print('Running the pipeline...')
            print('This means transforming the data and training the model')

        ppl.fit(corpus_strings, sentiments)

        self.trained_pipeline = ppl

        # if print_analytics_results:
        #     X_train, X_test, y_train, y_test = train_test_split(sparse_transformed_corpus, sentiments, test_size=0.2)
        # else:
        #     X_train = sparse_transformed_corpus
        #     y_train = sentiments

        # if print_analytics_results:
        #     print('Model\'s score on the training data:')
        #     print(self.trained_model.score(X_train, y_train))
        #     print('Model\'s score on the holdout data:')
        #     print(self.trained_model.score(X_test, y_test))

        if verbose:
            print('Finished training!')


    def save(self, filename):
        with open(filename, 'wb') as f:
            pickle.dump(self.trained_pipeline, f)

    @staticmethod
    def load(filename):
        inst = EmpathyMachines()
        with open(filename, 'rb') as f:
            inst.trained_pipeline = pickle.load(f)
        return inst

    def predict(self, text):
        try:
            if isinstance(text, basestring):
                text = [text]
        except:
            if isinstance(text, str):
                text = [text]

        return self.trained_pipeline.predict(text)

        # TODO(PRESTON):
            # consider formatting the output based on the input type
            # so if we get passed in a string, just return a string
            # whereas if we get passed an array, return an array.
