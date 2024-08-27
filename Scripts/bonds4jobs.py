import csv
import json
from datetime import datetime

import pgeocode
import scrapy


class Bonds4jobsSpider(scrapy.Spider):
    name = 'bonds4jobs'
    request_api = 'https://bonds4jobs.com/wp-admin/admin-ajax.php?action=store_search&lat={}&lng={' \
                  '}&max_results=25&search_radius=200 '
    custom_settings = {
        'FEED_URI': 'bonds4jobs.csv',
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
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,'
                  'application/signed-exchange;v=b3;q=0.9',
        'accept-language': 'en-US,en;q=0.9',
        'sec-ch-ua': '"Google Chrome";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/105.0.0.0 Safari/537.36 '
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.request_zip = self.get_search_zip()

    def get_search_zip(self):
        with open('state_zip.csv', 'r', encoding='utf-8-sig') as reader:
            return list(csv.DictReader(reader))

    def start_requests(self):
        for data in self.request_zip:
            zip_code = data.get('Zip_code', '')
            nomi = pgeocode.Nominatim('us')
            location = nomi.query_postal_code(codes=zip_code)
            lati = location.latitude
            longi = location.longitude
            yield scrapy.Request(url=self.request_api.format(lati, longi), callback=self.parse, headers=self.headers)

    def parse(self, response):
        try:
            json_data = json.loads(response.body)
            for data in json_data:
                item = dict()
                item['Business Name'] = data.get('store', '')
                item['Street Address'] = data.get('address2', '')
                item['State'] = data.get('state', '')
                item['Zip'] = data.get('zip', '')
                item['Phone Number'] = data.get('phone', '')
                item['Email'] = data.get('email', '')
                item['Latitude'] = data.get('lat', '')
                item['Longitude'] = data.get('lng', '')
                item['Meta_Description'] = "In order to obtain a bond, you can contact a State Bonding Coordinator. " \
                                           "Use our interactive map to find the coordinator closest to where you live" \
                                           " and work."
                item['Source_URL'] = 'https://bonds4jobs.com/our-services/directory'
                item['Occupation'] = 'Bonding Coordinator'
                item['Lead_Source'] = 'bonds4jobs'
                item['Record_Type'] = 'Business'
                item['Scraped_date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                yield item
        except Exception as ex:
            print(ex)

