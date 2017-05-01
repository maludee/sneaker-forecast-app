## StockX!
## Purpose: Scrape all the data from the site stockx.com

# Load Libraries
import scrapy
import time
from selenium import webdriver
import os
import csv
from collections import defaultdict

# Set up the environment
chromedriver = "/Applications/chromedriver"
os.environ["webdriver.chrome.driver"] = chromedriver

# 3 CSV files to store the data from sales, ask, and bidding history tables
sale_file = open('sale_file.csv', 'wb')
sale_writer = csv.writer(sale_file)


ask_file = open('ask_file.csv', 'wb')
ask_writer = csv.writer(ask_file)


bid_file = open('bid_file.csv', 'wb')
bid_writer = csv.writer(bid_file)


# New scrapy spider instance
class sneaker(scrapy.Spider):
	name = "sneaker"

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
		url = 'https://stockx.com/sneakers'
		yield scrapy.Request(url = url, callback = self.shoe_links)

	# The overall browsing page for all sneakers
	def shoe_links(self, response):
		self.driver.get(response.url)
		self.driver.maximize_window()
		time.sleep(3)

		name_list = []
		num_sales_list = []
		image_url_list = []
		url_list = []
		
		# Scroll to end of page and load all images
		for i in range(0,400):
			self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

		time.sleep(3)

		# Get the overall info from the browse page
		for i in self.driver.find_elements_by_xpath('//a[contains(@class, "tile")]'):
			
			name = i.find_element_by_xpath('.//div[@class="name"]').text
			name_list.append(name)
			num_sales = i.find_element_by_xpath('.//div[@class="change most-active"]').text
			num_sales_list.append(num_sales)
			image_url = i.find_element_by_xpath('.//div[@class="img"]/img').get_attribute('src')
			image_url_list.append(image_url)
			url = i.get_attribute('href')
			url_list.append(url)
			
			print name, num_sales, image_url, url
		
		for i in range(0, len(url_list)-1):
			yield scrapy.Request(url = url_list[i], callback = self.shoe_page, 
				meta = {'name':name_list[i], 'num_sales':num_sales_list[i], 'image_url': image_url_list[i]})
			
	
	# The individual page for each sneaker
	def shoe_page(self, response):
		name = response.request.meta['name']
		num_sales = response.request.meta['num_sales']
		image_url = response.request.meta['image_url']
		shoe_data = defaultdict(str)
		self.driver.get(response.url)
		self.driver.maximize_window()
		time.sleep(3)

		sale_list = []
		ask_list = []
		bid_list = []

		for i in self.driver.find_elements_by_xpath(
			'//div[contains(@class,"product-details")]//div[contains(@class,"detail")]'):
			if i.text.strip() != '':
				item = i.text.split(':')
				key = item[0].lower()
				value = item[1].lower()
				shoe_data[key] = value


		# Get the ask history
		try:
			lowest_ask = self.driver.find_element_by_xpath(
				'//*[@id="market-summary"]/div[3]/div/div[1]/div[2]').text
		except:
			lowest_ask = ''

		# Open the ask table
		for i in self.driver.find_elements_by_xpath(
			'//*[@id="market-summary"]/div[3]/div/div[1]/div[3]/div/a'):
			i.click()
			time.sleep(3)
		try:	
			for i in self.driver.find_elements_by_xpath(
				'//div[@class="allAsks modal-md modal-primary modal-dialog"]//tbody//tr'):
				ask_info = i.text
				ask_data = (name, ask_info)
				ask_list.append(ask_data)

		except:
			num_asks = ''
		print lowest_ask

		# Close the ask data
		for i in self.driver.find_elements_by_xpath(
			'/html/body/div[4]/div/div/div/div[1]/button/span'):
			i.click()
			time.sleep(3)

		# Get rid of the annoying popup thing by scrolling slightly
		for i in range(0,1):
			self.driver.execute_script("window.scrollBy(0, 250);")


		# Get the bidding history
		try:
			highest_bid = self.driver.find_element_by_xpath(
				'//*[@id="market-summary"]/div[4]/div/div[1]/div[2]').text
		except:
			highest_bid = ''

		# Open the bidding table
		for i in self.driver.find_elements_by_xpath(
			'//*[@id="market-summary"]/div[4]/div/div[1]/div[3]/a/span[1]'):
			i.click()
			time.sleep(3)
		
		try:
			for i in self.driver.find_elements_by_xpath(
				'//div[@class="allBids modal-md modal-primary modal-dialog"]//tbody//tr'):
				bid_info = i.text
				bid_data = (name, bid_info)
				bid_list.append(bid_data)
		except:
			num_bids = ''
		print highest_bid
		
		# Close the bidding history table
		for i in self.driver.find_elements_by_xpath(
			'/html/body/div[4]/div/div/div/div[1]/button/span'):
			i.click()
			time.sleep(3)


		# Send the main shoe data to a JSON file
		shoe_data['name'] = name
		shoe_data['num_sales'] = num_sales
		shoe_data['image_url'] = image_url
		shoe_data['highest_bid'] = highest_bid
		shoe_data['lowest_ask'] = lowest_ask
		yield shoe_data

		# Open the sales history table
		for i in self.driver.find_elements_by_xpath(
			'//*[@id="product-page-container"]/div/div[13]/div/div/div/div[2]/div[2]/a'):
			i.click()
			for i in self.driver.find_elements_by_xpath(
				'/html/body/div[4]/div/div/div/div[2]/div/div[1]/div/button'):
				i.click()
				time.sleep(3)
				
		# Get info out of the sales history table
		for item in self.driver.find_elements_by_xpath('//*[@id="480"]/tbody//tr'):
			try:
				sale_info = item.text
				print ' '
				print item.text
				print ' '
				sale_data = (name, sale_info)
				print ' '
				print sale_data
				print ' '
				sale_list.append(sale_data)
				print sale_list
			except:
				continue

		# Write results of tables to files
		sale_writer.writerows(sale_list)
		ask_writer.writerows(ask_list)
		bid_writer.writerows(bid_list)








			





