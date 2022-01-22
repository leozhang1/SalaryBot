# Salary.com Data Scraper
# extract salary information for specific job titles in the 317 largest us cities

import csv
from time import sleep
import json
import requests
from bs4 import BeautifulSoup
import re
# Identify scraping methodology
# Navigate to https://www.salary.com/
# Click on the "For You" option, then enter a position into the search box
# In the list of result descriptions, scroll down and click on the title and description that best matches what you're looking for
# URL Pattern
# What you should see now is a curve representing the distribution of salaries, with markers at the quintiles.

# Click the "view as table" link to see the data in table form.. this is the data that we want to scrape
# Take a look at the url to see how it's structured. This is the pattern that we want to imitate with our request
# The job title is at the end of the url with the word salary appended to the end

# Now, go to the top and click "Change City" and then either type in your city, choose one of the suggested cities. You can see how the city name is then appended to the end, and the format which it needs to be in. Let's use this information to create a template in our code. We'll use curly braces instead of the search criteria so that we can change up the url as needed to modify the search.

template = 'https://www.salary.com/research/salary/benchmark/{}-salary/{}'
# Now, use the template you just created to create a url. Then send a get request to extract the raw html from the website.

# build the url based on search criteria
position = 'devops-engineer-i'
# data-scientist-i
city = 'orlando-fl'
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36", 'Accept-Language': 'en-US, en;q=0.5'}
url = template.format(position, city)

# request the raw html
response = requests.get(url, headers=HEADERS)
# Inspect the data extraction options
# Now that we have the raw html, let's take a look at it to see how we might be able to extract the data. The first thing I always look at when I'm trying to scrape data is, can I access it directly through some backend api that returns data in json format? The way I look for this is by looking through the network activity. Typically, this will show up if you filter to XHR. And if you look at the response, you will see clearly formatted json data. Unfortuanately, that is not the case with this project, but you can see something like this in the Yahoo! Finance project where I extract historical stock data using a hidden api.

# json formatted data
# The good news, is that we have something almost as good. The next thing I usually look for is json formatted data that is embedded in the html data. So, right-click on the web-page and then click "view page source". Then, if you scroll down about mid-way, you'll notice some clearly formatted json data, that we can extract from the page, formatted as a python dictionary. This is fantastic, because it make the work SO MUCH EASIER! Not only do we have all of the quintiles broken out, but we also have the locality data and a nice description of the job title.

# Extracting the script
# You can see that the data is embedded in a script tag. However, there are multiple scripts here. The one that we want has a specific type "application/ld+json". That will narrow it a bit, but it won't be specific enough. If you look at these two scripts, you'll notice that they have an "@Type" key. One is called occupation, and the other is called "Organization". This corresponds to the comments above as well. What we can do to specific this exact script is to add a simple regular expression pattern that looks for the word "Organization".

soup = BeautifulSoup(response.text, 'html.parser')
pattern = re.compile(r'Occupation')
script = soup.find('script', {'type': 'application/ld+json'}, text=pattern)

# Identify the relevant data
# If you look closely, you'll notice that there are two sets of compensation statistics, one is the base salary, and the other is total compensation. The total compensation will include bonuses and other benefits. For this example, I'm just going to grab the base salary.

# Extract the json data
# One would think that you could use the text attribute to get the text inside this script tag, however... this isn't actually text. So, what you'll need to use instead is the contents attribute. This will return a list of the contents. There will only be one item in the list, so you'll need to index to the first item.

json_raw = script.contents[0]
# Convert the json data
# Now that we have a raw json string, we need to convert it to a python dictionary. We'll do this by using the loads function in the json library.

json_data = json.loads(json_raw)

# Extracting the data
# Now that you've got a python dictionary, you can index as you would a normal dictionary. So, let's grab the job title, the description, location, and the base compensation statistics.

job_title = json_data['name']
location = json_data['occupationLocation'][0]['name']
description = json_data['description']

ntile_10 = json_data['estimatedSalary'][0]['percentile10']
ntile_25 = json_data['estimatedSalary'][0]['percentile25']
ntile_50 = json_data['estimatedSalary'][0]['median']
ntile_75 = json_data['estimatedSalary'][0]['percentile75']
ntile_90 = json_data['estimatedSalary'][0]['percentile90']

salary_data = (job_title, location, description, ntile_10, ntile_25, ntile_50, ntile_75, ntile_90)


def extract_salary_info(job_title, job_city):
    """Extract and return salary information"""
    template = 'https://www.salary.com/research/salary/benchmark/{}-salary/{}'

    # build the url based on search criteria
    url = template.format(job_title, job_city)

    # request the raw html .. check for valid request
    try:
        response = requests.get(url)
        if response.status_code != 200:
            return None
    except requests.exceptions.ConnectionError:
        return None

    # parse the html and extract json data
    soup = BeautifulSoup(response.text, 'html.parser')
    pattern = re.compile(r'Occupation')
    script = soup.find('script', {'type': 'application/ld+json'}, text=pattern)
    json_raw = script.contents[0]
    json_data = json.loads(json_raw)

    # extract salary data
    job_title = json_data['name']
    location = json_data['occupationLocation'][0]['name']
    description = json_data['description']

    ntile_10 = json_data['estimatedSalary'][0]['percentile10']
    ntile_25 = json_data['estimatedSalary'][0]['percentile25']
    ntile_50 = json_data['estimatedSalary'][0]['median']
    ntile_75 = json_data['estimatedSalary'][0]['percentile75']
    ntile_90 = json_data['estimatedSalary'][0]['percentile90']

    data = (job_title, location, description, ntile_10, ntile_25, ntile_50, ntile_75, ntile_90)
    return data
# Now, let's import a list of cities. I found a list of the top 300+ US cities on Wikipedia, and then I re-formatted the city and state name so that I could easily insert it into this function and url.

with open('largest_cities.csv', newline='') as f:
    reader = csv.reader(f)
    # a reader typically returns each row as a list... so I need to flatten the list to make a single list
    cities = [city for row in reader for city in row]
print(cities[:10])
# ['New-York-NY', 'Los-Angeles-CA', 'Chicago-IL', 'Houston-TX', 'Phoenix-AZ', 'Philadelphia-PA', 'San-Antonio-TX', 'San-Diego-CA', 'Dallas-TX', 'San-Jose-CA']
# Getting all city data
# Now I an iterate over each major city in the US, extract the relevant salary information. I'm going to use the sleep function to create a small delay between each request. It's always a good idea to be a good internet citizen and not bombard a server with requests. Primary out of politeness... but also, being impolite with other peoples data and connections is a good way to get yourself banned from their site.

salary_data = []

for city in cities:
    result = extract_salary_info('devops-engineer-i', city)
    if result:
        salary_data.append(result)
        print(f'processed {city}')
        sleep(0.1)
# Save the data to csv
# Finally, we'll save our data to a csv file.
print('done')
with open('salary-results.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['Title','Location', 'Description', 'nTile10', 'nTile25', 'nTile50', 'nTile75', 'nTile90'])
    writer.writerows(salary_data)
# print the first 5 records
# for row in salary_data[:5]:
#     print(row)

# Consolidate into main function

def main(job_title):
    """Extract salary data from top us cities"""

    # get the list of largest us cities
    with open('largest_cities.csv', newline='') as f:
        reader = csv.reader(f)
        # a reader typically returns each row as a list... so I need to flatten the list to make a single list
        cities = [city for row in reader for city in row]

    # extract salary data for each city
    salary_data = []
    for city in cities:
        result = extract_salary_info(job_title, city)
        if result:
            salary_data.append(result)
            sleep(0.5)

    # save data to csv file
    with open('salary-results.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Title','Location', 'Description', 'nTile10', 'nTile25', 'nTile50', 'nTile75', 'nTile90'])
        writer.writerows(salary_data)

    return salary_data



