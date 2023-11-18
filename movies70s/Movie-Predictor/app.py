import pandas as pd
import numpy as np
import contractions
import re
from gensim.parsing.preprocessing import remove_stopwords
import pickle
from pywebio.input import *
from pywebio.output import *
from pywebio.exceptions import *
import pywebio
import argparse
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
with open(os.path.join(APP_STATIC, 'vectorizer2.pickle'), 'rb') as file6:
    vectorizer2 = pickle.load(file6)
with open(os.path.join(APP_STATIC, 'movie_ratings.pickle'), 'rb') as file7:
    movie_ratings = pickle.load(file7)
    
def word_cleaner(text):
    text = re.sub('[0-9]nd|[0-9]st|[0-9]rd|[0-9]th+','',text)
    text = text.lower()
    text = text.replace("'", '')
    text = re.sub("[^a-zA-Z]"," ",text)
    text = ' '.join(text.split())
    return(text)

pywebio.config(theme = 'dark')
def movie_predictor():
    
    put_text("This is a free and fun tool made with Python where people can make up a movie plot and find similar movies from 1970 to today.")
    put_text("Or if you want, you can type in a movie title and see what other movies in the database are similar based on its plot.")
    put_text("Thanks for checking the site out!")
    put_text("Some links in case you wanna run the app by certain decades:")
    put_link("70s", "https://movie-predictor-70s-5xlhowa54q-ue.a.run.app", new_window = True)
    put_text("")
    put_link("80s", "https://movie-predictor-80s-owjw33wcwq-ue.a.run.app", new_window = True)
    put_text("")
    put_link("90s", "https://movie-predictor-90s-xxqp3o6xna-ue.a.run.app", new_window = True)
    put_text("")
    put_link("2000's", "https://movie-predictor-00s-yxpwksz6pa-ue.a.run.app", new_window = True)
    put_text("")
    put_link("2010's", "https://movie-predictor-10s-7sycrvxa2a-ue.a.run.app", new_window = True)
    put_text("")
    put_link("All Decades", "https://movie-predictor-bdym5mncmq-ue.a.run.app", new_window = True)
    put_text("")
    put_text("2023 Vincent Yabor")
    
    data = input_group("You can either input your own plot or the title of a 70's movie", [textarea("Movie plot summary goes here! (25 character minimum)", required = False, name = "Plot"), input("Or type in a 70's movie title! (Case sensitive - must match IMDb title)", name = "Title", required = False)])

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
            similar_movies = ""
            put_text("Not enough words in your plot. Try again!")
            actions(buttons=["Refresh the page"])
            pywebio.session.run_js('window.location.reload()')
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
            for q in range(len(movie_ratings['ids'])):
                if p == movie_ratings['ids'][q]:
                    names.append(movie_ratings['primaryTitle'][q])
                    genre.append(movie_ratings['genres'][q])
                    year.append(movie_ratings['startYear'][q])
                    rating.append(movie_ratings['averageRating'][q])
                
        if names == []:
            popup("Predictions", [put_text("Genres that fit your plot."), put_text("There are no movies that fit your plot. Try again!")], closable = True)
            actions(buttons=["Refresh the page"])
            pywebio.session.run_js('window.location.reload()')
            return(result, similar_movies)
        else:
            similar_movies = pd.DataFrame({'Similar Movies':names, 'Genres':genre, 'Year':year, 'Rating':rating})
            print(similar_movies)
            popup("Predictions", [put_text("Genres that fit your plot:"), put_table(tdata = result.values.tolist(),header = ['Predicted Genre', 'Predicted Genre Score (Out of 1)']), put_text("Here are some 70's movies that fit your plot:"), put_table(tdata = similar_movies.values.tolist(), header = ['Similar Movies', 'Genres', 'Year', 'Rating'])], closable = True)
            actions(buttons=["Refresh the page"])
            pywebio.session.run_js('window.location.reload()')
            return(result, similar_movies)
    
    elif((data["Plot"] == "") and (data["Title"] != "")):
        title=data['Title']
        if(movie_ratings[movie_ratings['primaryTitle'] == title].shape[0] > 1):
            popup(f"There is more than one movie with the title {title}. Please specify the year!")
            startYear = select(options = movie_ratings[movie_ratings['primaryTitle'] == title]['startYear'])
            plot_vec = vectorizer2.transform(movie_ratings[(movie_ratings['primaryTitle'] == title) & (movie_ratings['startYear'] == startYear)]['plots_clean'])
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
                for q in range(len(movie_ratings['ids'])):
                    if p == movie_ratings['ids'][q]:
                        names.append(movie_ratings['primaryTitle'][q])
                        genre.append(movie_ratings['genres'][q])
                        year.append(movie_ratings['startYear'][q])
                        rating.append(movie_ratings['averageRating'][q])
            similar_movies = pd.DataFrame({'Similar Movies':names, 'Genres':genre, 'Year':year, 'Rating':rating})
            similar_movies = similar_movies[similar_movies['Similar Movies'] != title]
            popup(f"Similar 70's Movies to {data['Title']}:", put_table(tdata = similar_movies.values.tolist(), header = ['Similar Movies', 'Genres', 'Year', 'Rating']), closable = True)
            actions(buttons=["Refresh the page"])
            pywebio.session.run_js('window.location.reload()')
            return(similar_movies)
        else:
            plot_vec = vectorizer2.transform(movie_ratings[movie_ratings['primaryTitle'] == title]['plots_clean'])
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
                for q in range(len(movie_ratings['ids'])):
                    if p == movie_ratings['ids'][q]:
                        names.append(movie_ratings['primaryTitle'][q])
                        genre.append(movie_ratings['genres'][q])
                        year.append(movie_ratings['startYear'][q])
                        rating.append(movie_ratings['averageRating'][q])
            similar_movies = pd.DataFrame({'Similar Movies':names, 'Genres':genre, 'Year':year, 'Rating':rating})
            similar_movies = similar_movies[similar_movies['Similar Movies'] != title]            
            popup(f"Similar 70's Movies to {data['Title']}:", put_table(tdata = similar_movies.values.tolist(), header = ['Similar Movies', 'Genres', 'Year', 'Rating']), closable = True)
            actions(buttons=["Refresh the page"])
            pywebio.session.run_js('window.location.reload()')
            return(similar_movies)
                        
    elif((data["Plot"] != "") and (data["Title"] != "")):
        put_text("You have to choose either a plot or title input. Not both!")
        actions(buttons=["Refresh the page"])
        pywebio.session.run_js('window.location.reload()')
    else:
        put_text("No input found. Try again!")
        actions(buttons=["Refresh the page"])
        pywebio.session.run_js('window.location.reload()')
            
if(__name__ == '__main__'):
    import argparse
    from pywebio.platform.tornado_http import start_server as start_http_server
    from pywebio import start_server as start_ws_server
    
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--port", type=int, default=8080)
    parser.add_argument("--http", action="store_true", default=False, help='Whether to enable http protocol for communicates')
    args = parser.parse_args()
    
    if args.http:
        start_http_server(movie_predictor, port=args.port)
    else:
        start_ws_server(movie_predictor, port=args.port, websocket_ping_interval=30)