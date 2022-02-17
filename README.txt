This is a tool I have built for running a python webapp locally on a PC. This webapp predicts genres and similar movies based on a given movie plot summary input

1.) Open a command prompt window and run the following: python -m pip install -r 'requirements.txt'
2.) Download data.tsv and ratings.tsv from https://drive.google.com/file/d/15UxgHZCIDtpcspk7Ka34_ZacfBpYunG1/view?usp=sharing and put both in the IMDb_Movie_Predictors folder
3.) Choose the folder of whichever decade you want, and then navigate to IMDb-Scraper/bot and open a command prompt window here
4a.) Run the following command: scrapy crawl quotes -o movie_plots.csv
NOTE: the scrapy bot will take awhile to run. Going faster than its current settings risks a temporary IP ban from IMDb
4b.) If you do not want to run the scrapy bot, then download the movie_plots.csv file from PLACEHOLDER and place it in IMDb-Scraper/bot directory for your chosen decade
5.) Navigate to the Movie-Pickler/src folder of the same decade you chose and run main.py
6.) Navigate to the Movie-Predictor/src folder for your decade and run main.py
7.) Congrats! You're running a movie predictor webapp locally!