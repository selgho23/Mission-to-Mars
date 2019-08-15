# Dependencies
from bs4 import BeautifulSoup as bs
import requests
import pandas as pd
import pymongo
from splinter import Browser

####################
### WEB SCRAPING ###
####################

def init_browser():
    executable_path = {"executable_path": "chromedriver"}
    return Browser("chrome", **executable_path, headless=False)

def scrape():

    browser = init_browser()

    ### Nasa Mars news
    news_url = "https://mars.nasa.gov/news/"
    browser.visit(news_url)

    html = browser.html
    soup = bs(html, 'html.parser')

    news_title = soup.find('div', class_='content_title').a.text
    news_p = soup.find('div', class_='article_teaser_body').text

    ### JPL Mars Space Images
    img_url = "https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars"
    browser.visit(img_url)

    html = browser.html
    soup = bs(html, 'html.parser')

    base_img_url = "https://www.jpl.nasa.gov"
    img_url_snippet = soup.find('a', class_="button fancybox")['data-fancybox-href']
    featured_img_url = base_img_url + img_url_snippet

    ### Mars Weather
    weather_url = "https://twitter.com/marswxreport?lang=en"
    browser.visit(weather_url)

    html = browser.html
    soup = bs(html, 'html.parser')

    results = soup.find_all("div", class_="js-tweet-text-container")

    ##### Make sure tweet is actually about weather
    for result in results:
        tweet = result.p.text
        tweet_split = tweet.split(" ")
        ##### 'hPa' or 'temps' are commonly found in weather updates
        if ('hPa' in tweet_split) or ('temps' in tweet_split):
            break
            
    mars_weather = tweet
    
    ### Mars Fact
    facts_url = "https://space-facts.com/mars/"

    tables = pd.read_html(facts_url)
    mars_facts = tables[1]
    mars_facts.columns = ["description", "value"]
    mars_facts = mars_facts.set_index('description')

    ### Mars Hemispheres
    hemis_url = "https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars"
    browser.visit(hemis_url)

    html = browser.html
    soup = bs(html, 'html.parser')

    base_url = "https://astrogeology.usgs.gov"
    hemis_img_urls = []

    results = soup.find_all("div", class_='item')
    for result in results:
        
        title = result.find('h3').text
        img_page_url = base_url + result.find('a')['href']
        
        response = requests.get(img_page_url)
        img_soup = bs(response.text, 'html.parser')
        
        img_url = img_soup.find('ul').li.a['href']
        
        img_dict = {'title': title, 
                    'img_url': img_url}
        
        hemis_img_urls.append(img_dict)

    ### Append all scraped data to a dictionary
    ##### First convert mars_facts into a more usable form
    mars_facts_dict = mars_facts.to_dict('split')

    mars_facts_list = []
    for x in range(len(mars_facts_dict['index'])):
        idx = mars_facts_dict['index'][x]
        value = mars_facts_dict['data'][x][0]
        mars_facts_list.append([idx, value])

    mars_dict = {'news_title': news_title,
                 'news_p': news_p,
                 'featured_image_url': featured_img_url,
                 'current_weather': mars_weather,
                 'mars_facts': mars_facts_list,
                 'hemisphere_image_urls': hemis_img_urls}

    browser.quit()

    return mars_dict