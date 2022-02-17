import pandas as pd
import numpy as np
import json
import contractions
import re
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.multiclass import OneVsRestClassifier
from sklearn.linear_model import SGDClassifier
from sklearn.metrics import f1_score,precision_score,recall_score,accuracy_score,hamming_loss
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.model_selection import GridSearchCV
from sklearn.neighbors import KNeighborsClassifier
import time
from sklearn import utils
from gensim.parsing.preprocessing import remove_stopwords
import pickle

meta = pd.read_csv('../../../data.tsv', sep = '\t')
meta = meta[(meta['titleType'] != 'short') & (meta['titleType'] != 'tvEpisode') & (meta['titleType'] != 'tvShort') & (meta['titleType'] != 'video') & (meta['titleType'] != 'videoGame')]

meta = meta[meta['genres'].notna()]

meta = meta[meta['genres'] != "\\N"]

meta = meta.reset_index()
meta = meta.drop('index', axis = 1)

Genres = []
for i in range(len(meta['genres'])):
    Genres.append(meta['genres'][i].split(','))

meta['genres'] = Genres
meta_movies = meta[meta['titleType'] == 'movie']

meta_movies = meta_movies.reset_index()
meta_movies = meta_movies.drop('index', axis = 1)

meta_movies = meta_movies[meta_movies['startYear'] != "\\N"]
meta_movies = meta_movies.reset_index()
meta_movies = meta_movies.drop('index', axis=1)

meta_movies['startYear'] = [int(meta_movies['startYear'][i]) for i in range(len(meta_movies['startYear']))]

meta_movies = meta_movies[(meta_movies['startYear'] >= 1980) & (meta_movies['startYear'] <= 1989)]
meta_movies = meta_movies.reset_index()
meta_movies = meta_movies.drop('index', axis=1)

movie_ids_90s = meta_movies['tconst']

movie_plts = pd.read_csv('../../IMDb-Scraper/bot/movie_plots.csv')
plots = []
for i in movie_plts['movie_plots']:
    plots.append(str(i))

tmp_movies = meta_movies.head(len(plots))

tmp_movies['plots'] = plots

ratings = pd.read_csv('../../../ratings.tsv', sep = '\t')

movie_ratings = tmp_movies.merge(ratings, on = 'tconst')

bad = []
for i in range(movie_ratings.shape[0]):
    bad.append(re.findall(r"^\bIt looks like we don't have\b.+",movie_ratings['plots'][i]))

plots_new = []
for i in range(movie_ratings.shape[0]):
    plots_new.append(re.findall(r"^(?!\bIt looks like we don't have\b).+",movie_ratings['plots'][i]))

movie_ratings['plots_new'] = plots_new

movie_ratings = movie_ratings[movie_ratings['plots_new'].str.len() > 0]

movie_ratings = movie_ratings.drop('plots_new', axis = 1)

movie_ratings = movie_ratings.reset_index()
movie_ratings = movie_ratings.drop('index', axis = 1)

multilabel_binarizer = MultiLabelBinarizer()
multilabel_binarizer.fit(movie_ratings['genres'])
y = multilabel_binarizer.transform(movie_ratings['genres'])

movie_ratings['plots_clean'] = movie_ratings['plots'].apply(contractions.fix)

def word_cleaner(text):
    text = re.sub('[0-9]nd|[0-9]st|[0-9]rd|[0-9]th+','',text)
    text = text.lower()
    text = text.replace("'", '')
    text = re.sub("[^a-zA-Z]"," ",text)
    text = ' '.join(text.split())
    return(text)

movie_ratings['plots_clean'] = movie_ratings['plots_clean'].apply(word_cleaner)
movie_ratings['plots_clean'] = movie_ratings['plots_clean'].apply(remove_stopwords)

x = movie_ratings['plots_clean']
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size = 0.2, random_state = 20)

tfidf_vec=TfidfVectorizer(max_df = 0.3, ngram_range = (1,2))
x_train_vec = tfidf_vec.fit_transform(x_train)
x_test_vec = tfidf_vec.transform(x_test)

classifier = OneVsRestClassifier(SGDClassifier(max_iter = 10000, loss = 'log', penalty = 'l2', alpha = 0.0001, class_weight = 'balanced', n_jobs = -1, random_state = 20), n_jobs = -1)
classifier.fit(x_train_vec, y_train)

multilabel_binarizer_similar = MultiLabelBinarizer()
Y = [[movie_ratings['tconst'][i]] for i in range(len(movie_ratings['tconst']))]
Y = multilabel_binarizer_similar.fit_transform(Y)
x = movie_ratings['plots_clean']
vectorizer2 = TfidfVectorizer()
x_names = vectorizer2.fit_transform(x)
KNN = KNeighborsClassifier(5, n_jobs = -1, metric = 'cosine')
KNN.fit(x_names, Y)

cos_sim = cosine_similarity(x_names, x_names)
indices = pd.Series(movie_ratings['primaryTitle'])

preds_log = classifier.predict_proba(x_test_vec)
preds_new = (preds_log >= 0.45).astype(int)
tmp = multilabel_binarizer.inverse_transform(preds_new)
y_test_tmp = multilabel_binarizer.inverse_transform(y_test)
print('Accuracy:', accuracy_score(y_test,preds_new))
print('Hamming Loss:', hamming_loss(y_test,preds_new))
print()
print('Micro Precision:', precision_score(y_test, preds_new, average = 'micro'))
print('Micro Recall:', recall_score(y_test, preds_new, average = 'micro'))
print('Micro F1:', f1_score(y_test, preds_new, average = 'micro'))
print()
print('Macro Precision:', precision_score(y_test, preds_new, average = 'macro'))
print('Macro Recall:', recall_score(y_test, preds_new, average = 'macro'))
print('Macro F1:', f1_score(y_test, preds_new, average = 'macro'))

filename = '../../Movie-Predictor/src/static/tfidf_vec.pickle'
pickle.dump(tfidf_vec, open(filename, 'wb'))

filename = '../../Movie-Predictor/src/static/multilabel_binarizer.pickle'
pickle.dump(multilabel_binarizer, open(filename, 'wb'))

filename = '../../Movie-Predictor/src/static/vectorizer2.pickle'
pickle.dump(vectorizer2, open(filename, 'wb'))

filename = '../../Movie-Predictor/src/static/multilabel_binarizer_similar.pickle'
pickle.dump(multilabel_binarizer_similar, open(filename, 'wb'))

filename = '../../Movie-Predictor/src/static/cos_sim.pickle'
pickle.dump(cos_sim, open(filename, 'wb'))

filename = '../../Movie-Predictor/src/static/indices.pickle'
pickle.dump(indices, open(filename, 'wb'))

filename = '../../Movie-Predictor/src/static/movie_ratings.pickle'
pickle.dump(movie_ratings, open(filename, 'wb'))

filename = '../../Movie-Predictor/src/static/classifier.pickle'
pickle.dump(classifier, open(filename, 'wb'))

filename = '../../Movie-Predictor/src/static/KNN.pickle'
pickle.dump(KNN, open(filename, 'wb'))




