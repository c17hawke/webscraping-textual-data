'''
# Author: Sunny Bhaveen Chandra
# Contact: sunny.c17hawke@gmail.com
# dated: March, 04, 2020
'''

from bs4 import BeautifulSoup as soup
import urllib
import requests
import pandas as pd
import time
import os

# dictionary to gather data
data = {"Product": list(), 
      "Name": list(), 
      "Rating": list(), 
      "CommentHead": list(), 
      "Comment": list()}

def get_main_HTML(base_URL=None, search_string=None):
	'''
	return main html page based on search string
	'''
	# construct the search url with base URL and search string
	search_url = f"{base_URL}/search?q={search_string}"
	# usung urllib read the page
	with urllib.request.urlopen(search_url) as url:
	    page = url.read()
	# return the html page after parsing with bs4
	return soup(page, "html.parser")

def get_product_name_links(flipkart_base=None, bigBoxes=None):
	'''
	returns list of (product name, product link)
	'''
	# temporary list to return the results
	temp = []
	# iterate over list of bigBoxes
	for box in bigBoxes:
	    try:
	    	# if prod name and list present then append them in temp
	        temp.append((box.div.div.div.a.img['alt'],
	        	flipkart_base + box.div.div.div.a["href"]))
	    except:
	        pass
	    
	return temp

def get_prod_HTML(productLink=None):
	'''
	returns each product HTML page after parsing it with soup
	'''
	prod_page = requests.get(productLink)
	return soup(prod_page.text, "html.parser")

def get_final_data(commentbox=None, prodName=None):
	'''
	this will append data gathered from comment box into data dictionary
	'''
	# append product name
	data["Product"].append(prodName)
	try:
		# append Name of customer if exists else append default
	    data["Name"].append(commentbox.div.div.\
	          find_all('p', {'class': '_3LYOAd _3sxSiS'})[0].text)
	except:
	    data["Name"].append('No Name')

	try:
		# append Rating by customer if exists else append default
	    data["Rating"].append(commentbox.div.div.div.div.text)
	except:
	    data["Rating"].append('No Rating')

	try:
		# append Heading of comment by customer if exists else append default
	    data["CommentHead"].append(commentbox.div.div.div.p.text)
	except:
	    data["CommentHead"].append('No Comment Heading')

	try:
		# append comments of customer if exists else append default
	    comtag = commentbox.div.div.find_all('div', {'class': ''})
	    data["Comment"].append(comtag[0].div.text)
	except:
	    data["Comment"].append('No Customer Comment')

def save_as_dataframe(data, fileName=None):
	'''
	it saves the dictionary dataframe as csv by given filename inside
	the results folder
	'''
	df = pd.DataFrame(data)
	print(f"shape of df: {df.shape}")
	# create a results folder if not exists
	path_to_store = 'results'
	os.makedirs(path_to_store, exist_ok=True)
	# save the CSV file to results folder
	df.to_csv(f"{path_to_store}/{fileName}.csv", index=None)
	print("File saved successfully!!")


def main():
	# get base URL and a search string to query the website
	base_URL = 'https://www.flipkart.com' # 'https://www.' + input("enter base URL: ")
	
	# enter a product name eg "xiaomi"
	search_string = input("enter a brandname or a product name: ")
	
	# fill the spaces between search strings with +
	search_string = "+".join(search_string.split())
	print('processing...')

	# start counter to count time in seconds
	start = time.perf_counter()

	# store main HTML page for given search query
	flipkart_HTML = get_main_HTML(base_URL, search_string)

	# store all the boxes containing products
	bigBoxes = flipkart_HTML.find_all("div", {"class":"bhgxx2 col-12-12"})

	# store extracted product name links
	product_name_Links = get_product_name_links(base_URL, bigBoxes)

	# iterate over product name and links list
	for prodName, productLink in product_name_Links:
		# iterate over product HTML
	    for prod_HTML in get_prod_HTML(productLink):
	        try:
	        	# extract comment boxes from product HTML
	            comment_boxes = prod_HTML.find_all('div', {'class': '_3nrCtb'})
	            # iterate over comment boxes to extract required data
	            for commentbox in comment_boxes:
	            	# prpare final data
	                get_final_data(commentbox, prodName)
	                
	        except:
	            pass

	# save the data as gathered in dataframe
	save_as_dataframe(data, search_string)

	# finish time counter and calclulate time taked to complet ethis programe
	finish = time.perf_counter()
	print(f"program finished with and timelapsed: {finish - start} second(s)")


if __name__ == '__main__':
	try:
		main()
	except Exception as e:
		print(f"error detected: {e}")
