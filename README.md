## This is a tool I have built for running a python webapp locally on a PC. This webapp predicts genres and similar movies based on a given movie plot summary input

1. Open a command prompt window and run the following: python -m pip install -r 'requirements.txt'
2. Download data.tsv and ratings.tsv from https://drive.google.com/drive/folders/1jUrP8IFY0EKDNt7jXioHsVihG3hn83wt?usp=sharing and put both in the IMDb_Movie_Predictors folder
3. Choose the folder of whichever decade you want, and then navigate to IMDb-Scraper/bot and open a command prompt window here
4. Run the following command: scrapy crawl quotes -o movie_plots.csv

NOTE: the scrapy bot will take awhile to run. Going faster than its current settings risks a temporary IP ban from IMDb

5. If you do not want to run the scrapy bot, the movie_plots.csv files are already included in the repo
6. Navigate to the Movie-Pickler/src folder of the same decade you chose and run main.py
7. Navigate to the Movie-Predictor folder for your decade and run main.py
8. Congrats! You're running a movie predictor webapp locally!

I had previously uploaded the websites to Google Cloud Platform, but it became too expensive to maintain.
