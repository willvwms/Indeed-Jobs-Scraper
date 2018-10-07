# --------------------------------------------------------------------------------
# DEPENDENCIES, GLOBAL VARIABLES
# --------------------------------------------------------------------------------
import sys
import os
import requests
from datetime import datetime
from bs4 import BeautifulSoup
import csv
from datetime import datetime
import operator

# Change directory and prepare file name for output
os.chdir('./')
x = datetime.now()
date = x.strftime("%m-%d-%y") # 03/13/28
time = x.strftime("%I-%M-%p") # 10:10 AM
timestamp = '{}__{}'.format(date,time)
jobs = list()

# --------------------------------------------------------------------------------
# QUERY STRING
# --------------------------------------------------------------------------------
	# https://www.newmediacampaigns.com/blog/building-an-indeed-job-search-page-on-your-site
	# publisher - The Publisher ID assigned during registration.
	# v - Version. Which version of the API you wish to use. All publishers should be using version 2. Currently available versions are 1 and 2. This parameter is required.
	# formatFormat. - Which output format of the API you wish to use. The options are "xml" and "json." If omitted or invalid, the XML format is used.
	# callback - Callback. The name of a javascript function to use as a callback to which the results of the search are passed. This only applies when format=json. For security reasons, the callback name is restricted letters, numbers, and the underscore character.
	# q - Query. By default terms are ANDed. To see what is possible, use our advanced search page to perform a search and then check the url for the q value.
	# l - Location. Use a postal code or a "city, state/province/region" combination.
	# sort - Sort by relevance or date. Default is relevance.radiusDistance from search location ("as the crow flies"). Default is 25.
	# st - Site type. To show only jobs from job boards use 'jobsite'. For jobs from direct employer websites use 'employer'.
	# jt - Job type. Allowed values: "fulltime", "parttime", "contract", "internship", "temporary".
	# start - Start results at this result number, beginning with 0. Default is 0.
	# limit - Maximum number of results returned per query. Default is 10
	# fromage - Number of days back to search.
	# highlight - Setting this value to 1 will bold terms in the snippet that are also present in q. Default is 0.
	# filter - Filter duplicate results. 0 turns off duplicate job filtering. Default is 1.
	# latlong - If latlong=1, returns latitude and longitude information for each job result. Default is 0.
	# co - Search within country specified. Default is us. See below for a complete list of supported countries.
	# chnl - Channel Name: Group API requests to a specific channel
	# userip - The IP number of the end-user to whom the job results will be displayed. This field is required.
	# useragent - The User-Agent (browser) of the end-user to whom the job results will be displayed. This can be obtained from the "User-Agent" HTTP request header from the end-user. This field is required.

template = 'https://www.indeed.com/jobs?q={}+-experienced,+-senior&l=San+Francisco&radius={}&explvl=entry_level&limit={}&fromage={}&start=1'
fromage = '1'
radius = '20'
query_terms = 'software+engineer+(associate+or+junior+or+apprentice+or+entry+or+entry-level)'
limit = '50'
# from_number = ['1', '51', '101', '151', '201', '251', '301']
query = template.format( query_terms, radius, limit, fromage )

# --------------------------------------------------------------------------------
# MAIN PROCESS
# --------------------------------------------------------------------------------

html = requests.get(query).text
soup = BeautifulSoup(html, "html5lib")
postings = soup.find_all(class_="result")

print('Postings collection length: '+ str(len(postings)))

counter = 1

for item in postings:

	try:
		print('trying posting {}'.format(str(counter)))
		job = dict()

		age	= item.find("span", {"class":"date"}).get_text(strip=True).replace(" days ago", "").replace(" day ago", "")
		title = item.find("a", {"data-tn-element":"jobTitle"}).get_text(strip=True)
		company = item.find("span", {"class":"company"}).find("a",recursive=False).get_text(strip=True)
		city = item.find("span", {"class":"location"}).get_text(strip=True)
		summary = item.find("span", {"class":"summary"}).get_text(strip=True)
		jobkey = item.attrs['data-jk']
		link = "https://www.indeed.com/viewjob?jk={}".format(jobkey)

		job = {
			"Age": age,
			"Title": title,
			"Company": company,
			"City": city,
			"Summary" : summary,
			"Job Key (ID)" : jobkey,
			"Link" : link,
		}

		jobs.append(job)

		print('reached end of block for posting {}'.format(str(counter)))

		counter += 1

	except:
		print("Failed to scrape posting {} of {}".format(counter, str(len(postings))))
		counter += 1

print('Jobs list length: '+ str(len(jobs)))

jobs.sort(key=operator.itemgetter('Age'))

with open('posts__{}.xlsx'.format(timestamp), 'w', newline='\n', encoding='utf-8') as csvfile:
	fieldnames = jobs[0].keys()
	# fieldnames = list(item.keys())
	writer = csv.DictWriter(csvfile, delimiter="	", fieldnames=fieldnames)
	writer.writeheader()
	writer.writerows(jobs)
