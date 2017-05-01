
# Load libraries
import numpy as np
import pandas as pd
import flask
from datetime import datetime
pd.set_option('display.max_colwidth',1000)
import re

# Read csv of info about shoes
shoe_info = pd.read_csv('shoe_info.csv')
# Read csv of shoe predictions
shoe_forecast = pd.read_csv('shoe_forecast_2.csv')
# Read csv of shoe sales
shoe_sales = pd.read_csv('chart_data.csv')
# Read csv of instagram sentiment analysis results
shoe_sent = pd.read_csv('sentsum_2.csv')

def extract_data(shoe_request, data_request):
	if (data_request in ['predicted', 'trend']):
		some_data = shoe_forecast.loc[shoe_forecast.name == shoe_request, data_request].to_string(index=False)
	elif (data_request in ['release_date', 'image_url', 'transactions_last_month']):
		some_data = shoe_info.loc[shoe_info.name == shoe_request, data_request].to_string(index=False)
	else:
		shoe_request_2 = shoe_request.lower().replace(" ", "")
		shoe_request_2 = re.sub("[^a-zA-Z]+", '', shoe_request_2)
		some_data = shoe_sent.loc[shoe_sent.name == shoe_request_2, data_request].to_string(index=False)
	return some_data

def get_sales(shoe_request, data_request):
	""" Get sale history for requested shoe """
	sale_data = []
	df = shoe_sales[shoe_sales.name == shoe_request]
	if (data_request == 'mean'):
		for i in df.date:
			the_mean = df.loc[df.date == i, 'sale_mean'].to_string().split()[1]
			new_row = [int(datetime.strptime(i, '%Y-%m-%d').strftime('%s')) * 1000, float(the_mean)]
			sale_data.append(new_row)
	else:
		for i in df.date:
			the_max = df.loc[df.date == i, 'sale_max'].to_string().split()[1]
			the_min = df.loc[df.date == i, 'sale_min'].to_string().split()[1]
			new_row = [int(datetime.strptime(i, '%Y-%m-%d').strftime('%s')) * 1000, float(the_min), float(the_max)]
			sale_data.append(new_row)
	return sale_data

# Initialize the app
app = flask.Flask(__name__, static_folder='static', static_url_path='')

@app.route("/")
def viz_page():
    with open("sneakers.html", 'r') as viz_file:
        return viz_file.read()

@app.route("/sneakers", methods=["POST"])
def answer():
	data = flask.request.json
	sneaker_name_list = data["question"]
	sneaker_name = sneaker_name_list[0]
	print sneaker_name

	img_url= extract_data(sneaker_name, 'image_url')
	print img_url
	
	release_date= extract_data(sneaker_name, 'release_date')
	transactions= extract_data(sneaker_name, 'transactions_last_month')
	predicted = extract_data(sneaker_name, 'predicted')
	sentiment = extract_data(sneaker_name, 'sentiment_rank')
	engagement = extract_data(sneaker_name, 'comments_last_month_rank')
	comment_count = extract_data(sneaker_name, 'comments_total')

	if extract_data(sneaker_name, 'trend') == 'up':
		trend = "rise"
	else:
		trend = "fall"


	# Mean and range of sale prices for shoe
	sale_mean = get_sales(sneaker_name, 'mean')
	sale_range = get_sales(sneaker_name, 'range')
	print(sale_mean[0])

	return flask.jsonify({
		'img_url':img_url, 'sneaker_name':sneaker_name, 'release_date':release_date, 
		'transactions':transactions, 'sale_mean':sale_mean, 'sale_range':sale_range,
		'predicted':predicted, 'trend':trend, 'sentiment':sentiment,
		'engagement':engagement, 'comment_count':comment_count})

app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)
