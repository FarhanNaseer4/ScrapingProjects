from datetime import datetime

import scrapy


class FallonchamberSpiderSpider(scrapy.Spider):
    name = 'fallonchamber_spider'
    start_urls = ['https://www.fallonchamber.com/member-directory/member-search-results/?searchtext&buscat#038;buscat']
    custom_settings = {
        'FEED_URI': 'fallonchamber.csv',
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

    def parse(self, response):
        for data in response.css('div.search-result'):
            item = dict()
            item['Business Name'] = data.css('h2.business-name a::text').get('').strip()
            detail_url = data.css('h2.business-name a::attr(href)').get()
            if detail_url:
                item['Detail_Url'] = detail_url
            item['Category'] = ', '.join(cate.css('::text').get('') for cate in response.css('p.categories a'))
            street = data.xpath('.//p[@class="address"]//text()').get('').strip()
            if 'USA' not in street:
                if 'United States' not in street:
                    item['Street Address'] = street
                else:
                    item['Street Address'] = ''
            else:
                item['Street Address'] = ''
            state = data.xpath('.//p[@class="address"]/br/following-sibling::text()').get()
            if state:
                state_abb = state.split(',')[-1].strip()
                if len(state_abb.split('\xa0')) > 1:
                    item['State'] = state_abb.split('\xa0')[0].strip()
                    item['Zip'] = state_abb.split('\xa0')[1].strip()
            item['Phone Number'] = data.css('p.phone a::attr(href)').get('').replace('tel:', '').strip()
            item['Business_Site'] = data.css('p.website a::attr(href)').get('').strip()
            item['Email'] = data.css('p.email a::attr(href)').get('').replace('mailto:', '').strip()
            item['Social_Media'] = ', '.join(social.css('::attr(href)').get('') for social in response.css('div.cdash-social-media ul a'))
            item['Source_URL'] = 'https://www.fallonchamber.com/member-directory/member-search-results/?searchtext' \
                                 '&buscat#038;buscat '
            item['Meta_Description'] = response.xpath('//meta[@name="description" or '
                                                      '@property="og:description"]/@content').get('').strip()
            item['Occupation'] = 'Business Service'
            item['Lead_Source'] = 'fallonchamber'
            item['Detail_Url'] = response.url
            item['Record_Type'] = 'Business'
            item['Scraped_date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            yield item

        next_page = response.css('a.next::attr(href)').get()
        if next_page:
            yield response.follow(url=next_page, callback=self.parse, headers=self.headers)

