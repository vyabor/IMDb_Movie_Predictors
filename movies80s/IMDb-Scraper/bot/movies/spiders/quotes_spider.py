import scrapy
from ..items import movie_plotsItem
import pandas as pd

class QuotesSpider(scrapy.Spider):
    name = "quotes"
    movie_ids = pd.read_csv('movie_ids_80s.csv')
    movie_ids = list(movie_ids['ids'])
    url = []
    for i in movie_ids:
        site = f'https://www.imdb.com/title/{i}/plotsummary'
        url.append(site)
    
    def start_requests(self):
        urls = QuotesSpider.url
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        movie_plots = movie_plotsItem()
        movie_plots['movie_plots'] = []
        tmp = list(movie_plots['movie_plots'])
        
        html = [' '.join(line.strip() for line in p.xpath(".//text()").extract() if line.strip()) for p in response.xpath("//p")]
        no_plot = 'It looks like we don\'t have any Plot Summaries for this title yet. Be the first to contribute! Just click the "Edit page" button at the bottom of the page or learn more in the Plot Summary submission guide .'
        no_syn = 'It looks like we don\'t have a Synopsis for this title yet. Be the first to contribute! Just click the "Edit page" button at the bottom of the page or learn more in the Synopsis submission guide .'
        related = 'Related lists from IMDb users'
        copy = '© 1990- 2022 by IMDb.com, Inc.'
        tags = 'Taglines | Synopsis | Plot Keywords | Parents Guide'
        
        if((no_plot not in html) and (no_syn not in html) and (related in html) and (copy in html) and (tags in html)):
            tmp.append(max(html[:len(html) - 3], key = len))
        elif((no_plot not in html) and (no_syn not in html) and (related not in html) and (copy not in html) and (tags not in html)):
            tmp.append(max(html[:len(html)], key = len))
        elif((no_plot not in html) and (no_syn not in html) and (related not in html) and (copy not in html) and (tags in html)):
            tmp.append(max(html[:len(html)-2], key = len))
        elif((no_plot not in html) and (no_syn not in html) and (related not in html) and (copy in html) and (tags not in html)):
            tmp.append(max(html[:len(html)-2], key = len))
        elif((no_plot not in html) and (no_syn not in html) and (related in html) and (copy not in html) and (tags not in html)):
            tmp.append(max(html[:len(html)-2], key = len))
        elif((no_plot not in html) and (no_syn not in html) and (related in html) and (copy in html) and (tags not in html)):
            tmp.append(max(html[:len(html) - 1], key = len))
        elif((no_plot not in html) and (no_syn not in html) and (related in html) and (copy not in html) and (tags in html)):
            tmp.append(max(html[:len(html) - 1], key = len))
        elif((no_plot not in html) and (no_syn not in html) and (related not in html) and (copy in html) and (tags in html)):
            tmp.append(max(html[:len(html) - 1], key = len))
        elif((no_plot not in html) and (no_syn in html) and (related in html) and (copy in html) and (tags in html)):
            tmp.append(max(html[:len(html) - 4], key = len))
        elif((no_plot not in html) and (no_syn in html) and (related not in html) and (copy not in html) and (tags not in html)):
            tmp.append(max(html[:len(html) - 1], key = len))
        elif((no_plot not in html) and (no_syn in html) and (related not in html) and (copy not in html) and (tags in html)):
            tmp.append(max(html[:len(html) - 3], key = len))
        elif((no_plot not in html) and (no_syn in html) and (related in html) and (copy not in html) and (tags not in html)):
            tmp.append(max(html[:len(html) - 3], key = len))
        elif((no_plot not in html) and (no_syn in html) and (related not in html) and (copy in html) and (tags not in html)):
            tmp.append(max(html[:len(html) - 3], key = len))
        elif((no_plot not in html) and (no_syn in html) and (related in html) and (copy in html) and (tags not in html)):
            tmp.append(max(html[:len(html)-2], key = len))
        elif((no_plot not in html) and (no_syn in html) and (related in html) and (copy not in html) and (tags in html)):
            tmp.append(max(html[:len(html)-2], key = len))
        elif((no_plot not in html) and (no_syn in html) and (related not in html) and (copy in html) and (tags in html)):
            tmp.append(max(html[:len(html)-2], key = len))
        elif((no_plot in html) and (no_syn in html)):
            tmp.append(no_plot)
        elif((no_plot in html) and (no_syn not in html)):
            tmp.append(no_plot)
        else:
            tmp.append(max(html[:len(html) - 4], key = len))

        movie_plots['movie_plots'] = tmp

        yield movie_plots