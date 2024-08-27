from datetime import datetime

import scrapy


class AgentTravelerSpider(scrapy.Spider):
    name = 'agent_traveler'
    start_urls = ['https://agent.travelers.com/']
    custom_settings = {
        'FEED_URI': 'agent.travelers.csv',
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
        'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/106.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Chromium";v="106", "Google Chrome";v="106", "Not;A=Brand";v="99"',
    }

    def parse(self, response):
        for data in response.css('a.Directory-listLink'):
            state_url = data.css('::attr(href)').get()
            if state_url:
                yield response.follow(url=state_url, callback=self.parse_city, headers=self.headers)

    def parse_city(self, response):
        for data in response.css('a.Directory-listLink'):
            city_url = data.css('::attr(href)').get()
            if city_url:
                yield response.follow(url=city_url, callback=self.parse_listing, headers=self.headers)

    def parse_listing(self, response):
        for data in response.css('h2 a.Teaser-titleLink'):
            detail_url = data.css('::attr(href)').get()
            if detail_url:
                yield response.follow(url=detail_url, callback=self.parse_detail, headers=self.headers)

    def parse_detail(self, response):
        item = dict()
        item['Business Name'] = response.css('h1[itemprop="name"]::text').get('').strip()
        item['Street Address'] = response.css('span.c-address-street-1::text').get('').strip()
        item['State'] = response.css('span.c-address-state::text').get('').strip()
        item['Zip'] = response.css('span.c-address-postal-code::text').get('').strip()
        item['Phone Number'] = response.css('div[itemprop="telephone"]::text').get('').strip()
        item['Business_Site'] = response.css('div.Core-website a::attr(href)').get('').strip()
        item['Social_Media'] = ', '.join(data.css('::attr(href)').get('') for data in response.css('div.Core-social a'))
        item['Detail_Url'] = response.url
        fullname = response.css('div.Core-agentName::text').get('').strip()
        if fullname:
            item['Full Name'] = fullname
            item['First Name'] = fullname.split(' ')[0].strip()
            item['Last Name'] = fullname.split(' ')[-1].strip()
        item['Source_URL'] = 'https://agent.travelers.com/'
        item['Lead_Source'] = 'agent.travelers'
        item[
            'Meta_Description'] = 'Browse all Travelers Insurance agencies to learn more about home, auto, business ' \
                                  'and ' \
                                  'renters insurance'
        item['Occupation'] = 'Travel Insurance Agency'
        item['Record_Type'] = 'Business'
        item['Scraped_date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        yield item
