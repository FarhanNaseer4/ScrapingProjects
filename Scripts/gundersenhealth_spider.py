import json
from datetime import datetime

import scrapy


class GundersenhealthSpiderSpider(scrapy.Spider):
    name = 'gundersenhealth_spider'
    request_api = 'https://providers.gundersenhealth.org/api/search?sort=relevance%2Cnetworks%2Cavailability_density_best&page={}'
    custom_settings = {
        'FEED_URI': 'gundersenhealth.csv',
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
        'authority': 'providers.gundersenhealth.org',
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'cookie': '_gcl_au=1.1.1009043134.1667291221; _gid=GA1.2.320963371.1667291221; tc_ptidexpiry=1730363221148; tc_ptid=6Pm9zB7WoVrjOYzZrW0ayB; _hjSessionUser_2803456=eyJpZCI6IjA2NDE2ZGZkLWQ4MjktNWM3Zi1hM2U0LTBhNjUwMzAzMjBlMyIsImNyZWF0ZWQiOjE2NjcyOTEyMjE0OTQsImV4aXN0aW5nIjp0cnVlfQ==; search_shuffle_token=1a51bef9-7890-492f-ab53-2b097de5a96c; tc_ttid=bLpSwfyTuJorc0AoOR9PK; _hjSession_2803456=eyJpZCI6IjI1NTYzZDJjLTI0YTQtNDY3NC1iMWU4LTJlNzVjMWFmZDI5NCIsImNyZWF0ZWQiOjE2NjczNzE4ODc5MTAsImluU2FtcGxlIjpmYWxzZX0=; _hjAbsoluteSessionInProgress=1; _gat_UA-6138251-1=1; _gat=1; _uetsid=f585581059be11ed8c18b7f4ab72bd19; _uetvid=f5856df059be11ed89d279bd43e6191f; consumer_tracking_token=8eacb147-e101-4b40-a8e9-37fb215758bb; consumer_user_token=afabc45b-2f5d-4791-b9b0-cc09d8cf0279; _ga_3XQ14S88EP=GS1.1.1667371887.2.1.1667372175.0.0.0; _gat_kyruusTracker=1; _gat_UA-157894082-38=1; _ga=GA1.2.2028800953.1667291221; _ga_MH6W26MTLZ=GS1.1.1667371978.2.1.1667372190.0.0.0; consumer_tracking_token=8eacb147-e101-4b40-a8e9-37fb215758bb; consumer_user_token=afabc45b-2f5d-4791-b9b0-cc09d8cf0279; search_shuffle_token=1a51bef9-7890-492f-ab53-2b097de5a96c',
        'referer': 'https://providers.gundersenhealth.org/search?sort=relevance%2Cnetworks%2Cavailability_density_best&page=2',
        'sec-ch-ua': '"Google Chrome";v="107", "Chromium";v="107", "Not=A?Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36',
        'x-csrf-header': '2201dkqz'
    }

    def start_requests(self):
        yield scrapy.Request(url=self.request_api.format(1), callback=self.parse, headers=self.headers)

    def parse(self, response):
        result = json.loads(response.body)
        json_data = result.get('data', {}).get('providers', [])
        for data in json_data:
            item = dict()
            item['Full Name'] = data.get('name', {}).get('full_name', '')
            item['First Name'] = data.get('name', {}).get('first_name', '')
            item['Last Name'] = data.get('name', {}).get('last_name', '')
            loc = data.get('locations', [])
            if loc:
                address = loc[0] if loc[0] else {}
                item['Street Address'] = address.get('street1', '')
                item['State'] = address.get('state', '')
                item['Zip'] = address.get('zip', '')
                item['Business Name'] = address.get('name', '')
                item['Phone Number'] = address.get('phone', '')
            item['Source_URL'] = 'https://providers.gundersenhealth.org/search?sort=relevance%2Cnetworks' \
                                 '%2Cavailability_density_best '
            item['Lead_Source'] = 'gundersenhealth'
            item['Occupation'] = 'Doctor'
            item['Record_Type'] = 'Person'
            item['Scraped_date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            item['Meta_Description'] = 'Find a doctor and information about providers at Gundersen Health System. ' \
                                       'Search by condition, symptom, specialty or physician name. '
            yield item

        current_page = int(result.get('data', {}).get('search_summary', []).get('page', ''))
        total_page = int(result.get('data', {}).get('total_pages', ''))
        if current_page <= total_page:
            next_p = current_page + 1
            yield scrapy.Request(url=self.request_api.format(next_p), callback=self.parse, headers=self.headers)

