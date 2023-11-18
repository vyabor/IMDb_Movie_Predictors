import pandas as pd
import contractions
import re
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.multiclass import OneVsRestClassifier
from sklearn.linear_model import SGDClassifier
from sklearn.neighbors import KNeighborsClassifier
from gensim.parsing.preprocessing import remove_stopwords
import pickle
import os

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

movie_ratings = pd.read_csv(f'{dname}/movie_plots_merged.csv')

Genres = []
for i in range(len(movie_ratings['genres'])):
    Genres.append(movie_ratings['genres'][i].split(','))

movie_ratings['genres'] = Genres

multilabel_binarizer = MultiLabelBinarizer()
multilabel_binarizer.fit(movie_ratings['genres'])
y_genres = multilabel_binarizer.transform(movie_ratings['genres'])

movie_ratings['plots_clean'] = movie_ratings['movie_plots'].apply(contractions.fix)

def word_cleaner(text):
    text = re.sub('[0-9]nd|[0-9]st|[0-9]rd|[0-9]th+','',text)
    text = text.lower()
    text = text.replace("'", '')
    text = re.sub("[^a-zA-Z]"," ",text)
    text = ' '.join(text.split())
    return(text)

movie_ratings['plots_clean'] = movie_ratings['plots_clean'].apply(word_cleaner)
movie_ratings['plots_clean'] = movie_ratings['plots_clean'].apply(remove_stopwords)

X_plot = movie_ratings['plots_clean']

multilabel_binarizer_similar = MultiLabelBinarizer()
y = [[movie_ratings['ids'][i]] for i in range(len(movie_ratings['ids']))]
y = multilabel_binarizer_similar.fit_transform(y)

vectorizer2 = TfidfVectorizer(ngram_range = (2,3))
X_names = vectorizer2.fit_transform(X_plot)
KNN = KNeighborsClassifier(5, n_jobs = -1, metric = 'cosine')
KNN.fit(X_names, y)

tfidf_vec=TfidfVectorizer(max_df = 0.3, ngram_range = (1,2))
X_vec = tfidf_vec.fit_transform(X_plot)

classifier = OneVsRestClassifier(SGDClassifier(max_iter = 10000, loss = 'log_loss', penalty = 'l2', alpha = 0.0001, class_weight = 'balanced', n_jobs = -1, random_state = 20), n_jobs = -1)
classifier.fit(X_vec, y_genres)

filename = '../../Movie-Predictor/static/tfidf_vec.pickle'
pickle.dump(tfidf_vec, open(filename, 'wb'))

filename = '../../Movie-Predictor/static/multilabel_binarizer.pickle'
pickle.dump(multilabel_binarizer, open(filename, 'wb'))

filename = '../../Movie-Predictor/static/vectorizer2.pickle'
pickle.dump(vectorizer2, open(filename, 'wb'))

filename = '../../Movie-Predictor/static/multilabel_binarizer_similar.pickle'
pickle.dump(multilabel_binarizer_similar, open(filename, 'wb'))

filename = '../../Movie-Predictor/static/movie_ratings.pickle'
pickle.dump(movie_ratings, open(filename, 'wb'))

filename = '../../Movie-Predictor/static/classifier.pickle'
pickle.dump(classifier, open(filename, 'wb'))

filename = '../../Movie-Predictor/static/KNN.pickle'
pickle.dump(KNN, open(filename, 'wb'))