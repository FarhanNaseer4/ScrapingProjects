import scrapy


class EffinghamcountySpiderSpider(scrapy.Spider):
    name = 'effinghamcounty_spider'
    start_urls = ['https://www.effinghamcounty.com/list']
    custom_settings = {
        'FEED_URI': 'effinghamcounty.csv',
        'FEED_FORMAT': 'csv',
        'FEED_EXPORT_ENCODING': 'utf-8-sig',
        'FEED_EXPORT_FIELDS': ['Business Name', 'Full Name', 'First Name', 'Last Name', 'Street Address',
                               'Valid To', 'State', 'Zip', 'Description', 'Phone Number', 'Phone Number 1', 'Email',
                               'Business_Site', 'Social_Media', 'Record_Type',
                               'Category', 'Rating', 'Reviews', 'Source_URL', 'Detail_Url', 'Services',
                               'Latitude', 'Longitude', 'Occupation',
                               'Business_Type', 'Lead_Source', 'State_Abrv', 'State_TZ', 'State_Type',
                               'SIC_Sectors', 'SIC_Categories',
                               'SIC_Industries', 'NAICS_Code', 'Quick_Occupation']
    }
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,'
                  'application/signed-exchange;v=b3;q=0.9',
        'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/106.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Chromium";v="106", "Google Chrome";v="106", "Not;A=Brand";v="99"',
    }

    def parse(self, response):
        for data in response.css('div[id="mn-alphanumeric"] a'):
            listing_url = data.css('::attr(href)').get()
            yield scrapy.Request(url=listing_url, callback=self.parse_listing, headers=self.headers)

    def parse_listing(self, response):
        for data in response.css('div.mn-listingcontent'):
            item = dict()
            item['Business Name'] = data.css('div.mn-listingcontent div.mn-title a::text').get('').strip()
            item['Detail_Url'] = data.css('div.mn-listingcontent div.mn-title a::attr(href)').get('').strip()
            item['Street Address'] = data.css('div[itemprop="streetAddress"]::text').get('').strip()
            item['State'] = data.css('span[itemprop="addressRegion"]::text').get('').strip()
            item['Zip'] = data.css('span[itemprop="postalCode"]::text').get('').strip()
            item['Phone Number'] = data.css('li.mn-phone::text').get('').strip()
            item['Source_URL'] = 'https://www.effinghamcounty.com/list'
            item['Lead_Source'] = 'effinghamcounty'
            item['Occupation'] = 'Business Service'
            item['Record_Type'] = 'Business'
            yield item
