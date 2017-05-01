## Instagram
## Purpose: Search instagram for tags, collect all the media IDs

# Load Libraries
import scrapy
import time
from selenium import webdriver
import os
import csv
import pickle

# Set up the environment
chromedriver = "/Applications/chromedriver"
os.environ["webdriver.chrome.driver"] = chromedriver

# CSV file that the media IDs will write to
media_file = open('media_file', 'wb')
media_writer = csv.writer(media_file)

# List of tags to search
with open('instagram_shoes.pkl', 'rb') as picklefile:
	shoes_list = pickle.load(picklefile)

# print shoes_list

# # Test that scrolling is working properly on a short list
# shoes_list = ['yeezyblachblahblahdhs','yeezyboostpirateblack']

# New scrapy spider instance
class instagram(scrapy.Spider):
	name = "instagram"

	# Required so that requests are nicely spaced out
	custom_settings = {
		"DOWNLOAD_DELAY" : 2,
		"CONCURRENT_REQUESTS_PER_DOMAIN" : 1,
	}

	# Initialize the spider
	def __init__(self):
		self.driver = webdriver.Chrome(chromedriver)
		scrapy.Spider.__init__(self)

	# Close after last reference to spider
	def __del__(self):
		scrapy.Spider.__del__(self)

	# Starting point url for spider. 
	def start_requests(self):
		base_url = 'https://www.instagram.com/explore/tags/{}/'
		urls = [base_url.format(shoe) for shoe in shoes_list]
		
		for i in range(0, len(urls)):
			yield scrapy.Request(url = urls[i], callback = self.picture_links, meta = {'shoe_tag':shoes_list[i]})

	# The overall browsing page for all photos for each tag
	def picture_links(self, response):
		shoe_tag = response.request.meta['shoe_tag']
		self.driver.get(response.url)
		self.driver.maximize_window()
		time.sleep(3)

		# Scroll once to get to the load more button
		self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

		# Check if there is a load more button and then click on it
		for i in self.driver.find_elements_by_xpath('//*[@id="react-root"]/section/main/article/div/a'):
			if i:
				i.click()
				# Scroll to allow page load
				for i in range(0,19999):
					self.driver.execute_script("window.scrollBy(0, 5);")

		time.sleep(3)

		# Collect all of the links
		url_list = []
		
		for i in self.driver.find_elements_by_xpath('//article[@class="_3n7ri"]//a'):
			url = i.get_attribute('href')
			url_list.append(url)

		print url_list

		for i in range(0, len(url_list)):
			yield scrapy.Request(url = url_list[i], callback = self.media_IDs,
				meta = {'shoe_tag':shoe_tag})

	# Individual post page to collect media IDs
	def media_IDs(self, response):
		shoe_tag = response.request.meta['shoe_tag']
		self.driver.get(response.url)
		self.driver.maximize_window()
		time.sleep(3)

		media_id_list = []
		
		for i in self.driver.find_elements_by_xpath('//meta[@property="al:ios:url"]'):
			media_id = i.get_attribute('content')
			print media_id
			
			media_data = (shoe_tag, media_id)
			media_id_list.append(media_data)

		print media_id_list
		# Write results to files
		media_writer.writerows(media_id_list)



		







			





