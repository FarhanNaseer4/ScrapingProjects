import json
import re
from datetime import datetime

import scrapy


class AtpropertiesSpider(scrapy.Spider):
    name = 'atproperties'
    request_api = 'https://www.atproperties.com/api/v0/agents/search?page=1&order=first'
    custom_settings = {
        'FEED_URI': 'atproperties.csv',
        'FEED_FORMAT': 'csv',
        'FEED_EXPORT_ENCODING': 'utf-8-sig',
        'FEED_EXPORT_FIELDS': ['Business Name', 'Full Name', 'First Name', 'Last Name', 'Street Address',
                               'Valid To', 'State', 'Zip', 'Description', 'Phone Number', 'Phone Number 1', 'Email',
                               'Business_Site', 'Social_Media', 'Record_Type',
                               'Category', 'Rating', 'Reviews', 'Source_URL', 'Detail_Url', 'Services',
                               'Latitude', 'Longitude', 'Occupation',
                               'Business_Type', 'Lead_Source', 'State_Abrv', 'State_TZ', 'State_Type',
                               'SIC_Sectors', 'SIC_Categories',
                               'SIC_Industries', 'NAICS_Code', 'Quick_Occupation', 'Scraped_date', 'Meta_Description']
    }
    headers = {
        'authority': 'www.atproperties.com',
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'cookie': '_gcl_au=1.1.563075873.1669185447; _ga=GA1.2.396943530.1669185447; _gid=GA1.2.1140378597.1669185447; _hjFirstSeen=1; _hjIncludedInSessionSample=0; _hjSession_1791524=eyJpZCI6Ijg1Y2RkODM5LTBiYTItNDhiYS1hMTQ2LWI0ZjU2MTJkNGVjZSIsImNyZWF0ZWQiOjE2NjkxODU0NDg2NjIsImluU2FtcGxlIjpmYWxzZX0=; _hjAbsoluteSessionInProgress=0; _hjSessionUser_1791524=eyJpZCI6IjY4NmZlZGExLTE1NzAtNWUwOC05YjI3LWI3OGNmZjk1MWRmYiIsImNyZWF0ZWQiOjE2NjkxODU0NDcwNzAsImV4aXN0aW5nIjp0cnVlfQ==; cookie-session-agent=eyJpdiI6Imh6NjdhQUdzWVwvOWV3UE9WQ1JMeDlRPT0iLCJ2YWx1ZSI6IitsWitDWVBVZnVtVENlUWd0eWdURnc9PSIsIm1hYyI6IjA1ZGZmZjdiNjAwYmY5MjE0NmMyZTNmYWRmMjU2Zjg5NzkzNzhlODE3NWM5ZDc0ZGI2Mzk0NWVlYjMwN2Q4NGEifQ%3D%3D; XSRF-TOKEN=eyJpdiI6IjlRQVl2eDl4bDFoVTE4UW5VSGJIT1E9PSIsInZhbHVlIjoiS2JoZFJTbExnNlc0NlFyWFFDZlp4Z3ZvbWxHMUxqVm5wN1wvcEUxMmVwZVBZTDVyZTFORWZIRW1MSEtUMktGaU8iLCJtYWMiOiIxZTk4MWFhOTkzYjYxZTcwZDY5YmRjYjJkMTE1ZjhjMDdjZGVmYjhlYjgwYTNlODJiN2VlMTIwNDFmODY2OWVjIn0%3D; laravel_session=eyJpdiI6ImpIWGhFa1ZMTTZPQ0tsa1hVS3lZR0E9PSIsInZhbHVlIjoiT0ZQaDdodXNPMHhkMDFGTENYdTR3OVoyZ2Q4UVBoWDk3NDluZlhKU2hHUHRzWGJYSmpaekFLczQxNTdZWWVIYiIsIm1hYyI6ImY0NDk1YTQ2NTRhNGUyNDdhOTJhZTkyYTQ5MzM3ZjlmMjliN2YxMjc1YTYwYzNlZGMxYWZhOGExYWE2YjIwZTgifQ%3D%3D; _gat_UA-5933381-1=1; XSRF-TOKEN=eyJpdiI6IkR2TjJBQW83ZUdPZkY1aXc4QUhFZFE9PSIsInZhbHVlIjoieDQ0eHFMVEZ5WHlxa3ljbllWUXorWUtMSGNxZzlHRnA2ajhueVFXc2ZvUmV4RWY3MXJhS1ZJXC9SUHZ2ekU1MnEiLCJtYWMiOiJmYWU1ZGY2NmU2N2QwMThlZjkzN2FlYTVhYjhiZjM5Nzg2NDc5OGI2NTlmNTNmOGQ3ZTM0MDhlOTA0NTZiODMwIn0%3D; laravel_session=eyJpdiI6InpNUWsrcXo4ZU1Vd2ZJdGpydmtPYkE9PSIsInZhbHVlIjoiSHRiYnZKSVR0SHpiRmhRY0p0T0dFajVDVUM0RGdaOXdha3N5XC9VaVo1cWtCXC81anFsN3ZPV1RzODkyMUlZZWtBIiwibWFjIjoiZWNkYzk5ZjM5Mjg5NWY0ZTJlMGFjMDcxYzg4YTQwZThlZTFjZDM3ODU3NWViNDE4YzU0ZTE5YzdmNDNmZmNjNiJ9',
        'referer': 'https://www.atproperties.com/chicagoland/agents/search?page=1&q=&order=first',
        'sec-ch-ua': '"Google Chrome";v="107", "Chromium";v="107", "Not=A?Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36',
        'x-client-timezone-offset': '-300',
        'x-csrf-token': 'jbvGjnRDhNlWUyjhGFf2pHuJ1bB2jAXNcUcPBHcg',
        'x-requested-with': 'XMLHttpRequest',
        'x-site-context-id': '9',
        'x-xsrf-token': 'eyJpdiI6IjlRQVl2eDl4bDFoVTE4UW5VSGJIT1E9PSIsInZhbHVlIjoiS2JoZFJTbExnNlc0NlFyWFFDZlp4Z3ZvbWxHMUxqVm5wN1wvcEUxMmVwZVBZTDVyZTFORWZIRW1MSEtUMktGaU8iLCJtYWMiOiIxZTk4MWFhOTkzYjYxZTcwZDY5YmRjYjJkMTE1ZjhjMDdjZGVmYjhlYjgwYTNlODJiN2VlMTIwNDFmODY2OWVjIn0='
    }

    def start_requests(self):
        yield scrapy.Request(url=self.request_api, callback=self.parse, headers=self.headers)

    def parse(self, response):
        try:
            json_data = json.loads(response.body)
            json_record = json_data.get('data', {}).get('data', [])
            for data in json_record:
                item = dict()
                a_type = data.get('agentType', '')
                fullname = data.get('name', '')
                if 'team' not in a_type:
                    if '/' not in fullname:
                        item['Full Name'] = fullname
                        item['First Name'] = fullname.split(' ')[0].strip()
                        item['Last Name'] = fullname.split(' ')[-1].strip()
                    else:
                        item['Business Name'] = fullname
                else:
                    item['Business Name'] = fullname
                item['Phone Number'] = data.get('phone', '')
                item['Business_Site'] = data.get('websiteUrl', '')
                item['Detail_Url'] = data.get('profileUrl', '')
                item['Email'] = data.get('email', '')
                contact_detail = data.get('office', {}).get('address', '')
                try:
                    states = re.findall(r'\b[A-Z]{2}\b', contact_detail)
                    if len(states) == 2:
                        state = states[-1]
                    else:
                        state = states[0]
                except:
                    state = ''
                try:
                    street = contact_detail.rsplit(state, 1)[0].strip().rstrip(',').strip()
                except:
                    street = ''
                try:
                    zip_code = re.search(r"(?!\A)\b\d{5}(?:-\d{4})?\b", contact_detail).group(0)
                except:
                    zip_code = ''
                item['Street Address'] = street
                item['State'] = state
                item['Zip'] = zip_code
                item['Phone Number 1'] = data.get('office', {}).get('phone', '')
                item['Source_URL'] = 'https://www.atproperties.com/chicagoland/agents/search?page=2&order=first'
                item['Occupation'] = data.get('agentType', '')
                item['Lead_Source'] = 'atproperties'
                item['Record_Type'] = 'Person'
                item['Meta_Description'] = '@properties Real Estate Agents'
                item['Scraped_date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                yield item

            next_url = json_data.get('data', {}).get('next_page_url', '')
            if next_url:
                yield scrapy.Request(url=next_url, callback=self.parse, headers=self.headers)
        except Exception as ex:
            print(ex)
