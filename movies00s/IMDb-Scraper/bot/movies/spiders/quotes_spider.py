import scrapy
from ..items import movie_plotsItem
import pandas as pd
import os

current_dir = os.path.dirname(__file__)
movies_path = os.path.join(current_dir, 'movie_ids_00s.csv')

class QuotesSpider(scrapy.Spider):
    name = "quotes"
    movie_ids = pd.read_csv(movies_path)
    movie_ids = list(movie_ids['ids'])
    url = []
    for i in movie_ids:
        site = f'https://www.imdb.com/title/{i}/plotsummary'
        url.append(site)
    
    def start_requests(self):
        urls = QuotesSpider.url
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.55 Safari/537.36'
        }
        for url in urls:
            yield scrapy.Request(url=url, headers=headers, callback=self.parse)

    def parse(self, response):
        movie_plots = movie_plotsItem()

        # Define XPath expressions for synopsis and plot summary
        synopsis_xpath = "/html/body/div[2]/main/div/section/div/section/div/div[1]/section[2]/div[2]/ul/li/div/div/div/text()"
        plot_summary_xpath = "/html/body/div[2]/main/div/section/div/section/div/div[1]/section[1]/div[2]/ul/li/div/div/div/text()"

        # Extract synopsis and plot summary
        synopsis = response.xpath(synopsis_xpath).extract()
        plot_summary = response.xpath(plot_summary_xpath).extract()

        # Check if synopsis and plot summary exist
        if synopsis:
            # Filter out empty strings and check if synopsis is not empty
            synopsis = [s.strip() for s in synopsis if s.strip()]
            if synopsis:
                longest_synopsis = max(synopsis, key=len)
            else:
                longest_synopsis = None
        else:
            longest_synopsis = None

        if plot_summary:
            # Filter out empty strings and check if plot summary is not empty
            plot_summary = [p.strip() for p in plot_summary if p.strip()]
            if plot_summary:
                longest_plot_summary = max(plot_summary, key=len)
            else:
                longest_plot_summary = None
        else:
            longest_plot_summary = None

        # Determine the longest text
        if longest_synopsis and longest_plot_summary:
            longest_text = max(longest_synopsis, longest_plot_summary, key=len)
        elif longest_synopsis:
            longest_text = longest_synopsis
        elif longest_plot_summary:
            longest_text = longest_plot_summary
        else:
            longest_text = "No plot or synopsis available."

        movie_plots['movie_plots'] = longest_text

        yield movie_plots