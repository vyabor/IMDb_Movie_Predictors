import pandas as pd
import numpy as np
import contractions
import re
from gensim.parsing.preprocessing import remove_stopwords
import pickle

from flask import Flask
from pywebio.input import *
from pywebio.output import *
from pywebio.exceptions import *
import pywebio

import os
from settings import APP_STATIC

with open(os.path.join(APP_STATIC, 'classifier.pickle'), 'rb') as file1:
    classifier = pickle.load(file1)
with open(os.path.join(APP_STATIC, 'KNN.pickle'), 'rb') as file2:
    KNN = pickle.load(file2)
with open(os.path.join(APP_STATIC, 'multilabel_binarizer.pickle'), 'rb') as file3:
    multilabel_binarizer = pickle.load(file3)
with open(os.path.join(APP_STATIC, 'multilabel_binarizer_similar.pickle'), 'rb') as file4:
    multilabel_binarizer_similar = pickle.load(file4)
with open(os.path.join(APP_STATIC, 'tfidf_vec.pickle'), 'rb') as file5:
    tfidf_vec = pickle.load(file5)
with open(os.path.join(APP_STATIC, 'cos_sim.pickle'), 'rb') as file6:
    cos_sim = pickle.load(file6)
with open(os.path.join(APP_STATIC, 'vectorizer2.pickle'), 'rb') as file7:
    vectorizer2 = pickle.load(file7)
with open(os.path.join(APP_STATIC, 'indices.pickle'), 'rb') as file8:
    indices = pickle.load(file8)
with open(os.path.join(APP_STATIC, 'movie_ratings.pickle'), 'rb') as file9:
    movie_ratings = pickle.load(file9)
    
def word_cleaner(text):
    text = re.sub('[0-9]nd|[0-9]st|[0-9]rd|[0-9]th+','',text)
    text = text.lower()
    text = text.replace("'", '')
    text = re.sub("[^a-zA-Z]"," ",text)
    text = ' '.join(text.split())
    return(text)

class fragile(object):
    class Break(Exception):
      """Break out of the with statement"""

    def __init__(self, value):
        self.value = value

    def __enter__(self):
        return self.value.__enter__()

    def __exit__(self, etype, value, traceback):
        error = self.value.__exit__(etype, value, traceback)
        if etype == self.Break:
            return True
        return error

app = Flask(__name__)
@app.route("/")
def movie_predictor():
    
    pywebio.config(theme = 'dark')
    #pywebio.session.run_js('WebIO._state.CurrentSession.on_session_close(()=>{setTimeout(()=>location.reload(), 4000})')
    data = input_group("You can either input your own plot or the title of a movie", [textarea("Movie plot summary goes here! (25 character minimum)", required = False, name = "Plot"), input("Or Movie Title!", name = "Title", required = False)])
    with fragile(put_loading(shape = 'border', color = 'primary')):
        if((data["Plot"] != "") and (data["Title"] == "")):
    
            result = pd.DataFrame({'Predicted Genre':[],'Predicted Genre Score':[]})
            similar_movies = pd.DataFrame({'Similar Movies':[], 'Genres':[], 'Year':[], 'Rating':[]})
            
            plot_input = data['Plot']
            plot_genre = data['Plot']
            plot_genre = contractions.fix(plot_genre)
            plot_genre = word_cleaner(plot_genre)
            plot_genre = remove_stopwords(plot_genre)
            plot_vec_genre_pred = tfidf_vec.transform([plot_genre])    
            plot_predict_genre = classifier.predict_proba(plot_vec_genre_pred)
            plot_predict_genre_new = (plot_predict_genre >= 0.45).astype(int)
            predicted_genres = list(multilabel_binarizer.inverse_transform(plot_predict_genre_new)[0])
            predicted_scores = plot_predict_genre[plot_predict_genre >= 0.45].tolist()
            predicted_scores = [round(i, 3) for i in predicted_scores]
        
            if predicted_genres == []:
                print('No genre predicted.')
                print('Finding similar movies.')
            else:
                result = pd.DataFrame({'Predicted Genre':predicted_genres,'Predicted Genre Score':predicted_scores})
                result = result.sort_values('Predicted Genre Score', ascending = False).reset_index().drop('index', axis = 1)
                print(result)
                print()
                print('Genres predicted. Finding similar movies in database.')
                print()  
                
                plot = contractions.fix(data['Plot'])
                plot = word_cleaner(data['Plot'])
                plot = remove_stopwords(data['Plot']) 
                
            if len(plot_input) < 25:
                result = pd.DataFrame({'a':[1]})
                similar_movies = "Hello There!"
                put_text("Not enough words in your plot. Try again!")
                actions(buttons=["Refresh the page"])
                pywebio.session.run_js('window.location.reload()')
                raise fragile.Break
                return(result, similar_movies)
        
    
            plot_vec = vectorizer2.transform([plot])   

            plot_pred = KNN.predict_proba(plot_vec)   
        
            for i in range(len(plot_pred)):
                if plot_pred[i][0][0] != 1:
                    plot_pred[i][0] = np.array([0,1])
                else:
                    plot_pred[i][0] = np.array([1,0])
        
            tmp = []
            for j in plot_pred:
                if (j == np.array([0,1]))[0][0]:
                    tmp.append(1)
                else:
                    tmp.append(0)
        
            tmp = np.reshape(np.array(tmp), (1, np.array(tmp).shape[0]))
            ids = list(multilabel_binarizer_similar.inverse_transform(np.array(tmp))[0])
            
            names = []
            genre = []
            year = []
            rating = []
            for p in ids:
                for q in range(len(movie_ratings['tconst'])):
                    if p == movie_ratings['tconst'][q]:
                        names.append(movie_ratings['primaryTitle'][q])
                        genre.append(movie_ratings['genres'][q])
                        year.append(movie_ratings['startYear'][q])
                        rating.append(movie_ratings['averageRating'][q])
                    
            if names == []:
                popup("Predictions", [put_text("Genres that fir your plot."), put_text("There are no movies that fit your plot. Try again!")], closable = True)
                actions(buttons=["Refresh the page"])
                pywebio.session.run_js('window.location.reload()')
                raise fragile.Break
                return(result, similar_movies)
            else:
                similar_movies = pd.DataFrame({'Similar Movies':names, 'Genres':genre, 'Year':year, 'Rating':rating})
                print(similar_movies)
                popup("Predictions", [put_text("Genres that fit your plot:"), put_table(tdata = result.values.tolist(),header = ['Predicted Genre', 'Predicted Genre Score (Out of 1)']), put_text("Here are some movies that fit your plot:"), put_table(tdata = similar_movies.values.tolist(), header = ['Similar Movies', 'Genres', 'Year', 'Rating'])], closable = True)
                actions(buttons=["Refresh the page"])
                pywebio.session.run_js('window.location.reload()')
                raise fragile.Break
                return(result, similar_movies)
        
        elif((data["Plot"] == "") and (data["Title"] != "")):
            title=data['Title']
            recommended_movies = []
            if(title in list(indices)):
                idx = indices[indices == title].index[0]
                score_series = pd.Series(cos_sim[idx]).sort_values(ascending = False)
                top_index = list(score_series.iloc[1:6].index)
                for i in top_index:
                    recommended_movies.append(list(movie_ratings['primaryTitle'])[i])
                recommended_movies = pd.DataFrame({"Similar Movies":recommended_movies})
                popup(f"Similar Movies to {data['Title']}:", put_table(tdata = recommended_movies.values.tolist()))
                actions(buttons=["Refresh the page"])
                pywebio.session.run_js('window.location.reload()')
                raise fragile.Break
                return recommended_movies
            else:
                recommended_movies = pd.DataFrame({"Similar Movies":["nothing"]})
                put_text("That title is not in the database. Try again!")
                actions(buttons=["Refresh the page"])
                pywebio.session.run_js('window.location.reload()')
                raise fragile.Break
                return recommended_movies
                    
        elif((data["Plot"] != "") and (data["Title"] != "")):
            put_text("You have to choose either a plot or title input. Not both!")
            actions(buttons=["Refresh the page"])
            pywebio.session.run_js('window.location.reload()')
            raise fragile.Break
        else:
            put_text("No input found. Try again!")
            actions(buttons=["Refresh the page"])
            pywebio.session.run_js('window.location.reload()')
            raise fragile.Break
    

if __name__ == '__main__':
    movie_predictor()
    app.run(host="127.0.0.1", port=8080, debug=False)