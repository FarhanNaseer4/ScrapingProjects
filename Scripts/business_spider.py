import scrapy


class BusinessSpiderSpider(scrapy.Spider):
    name = 'business_spider'
    start_urls = ['https://www.alabama-webbusiness.com/search.php?q=hotel']
    base_url = 'https://arizona-businessdirectory.com{}'
    detail_base = 'https://arizona-businessdirectory.com/{}'
    custom_settings = {
        'FEED_URI': 'alabama_business.csv',
        'FEED_FORMAT': 'csv',
        'FEED_EXPORT_ENCODING': 'utf-8-sig',
        'FEED_EXPORT_FIELDS': ['Business Name', 'Full Name', 'First Name', 'Last Name', 'Street Address',
                               'Valid To', 'State', 'Zip', 'Description', 'Phone Number', 'Phone Number 1', 'Email',
                               'Business_Site', 'Social_Media',
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
                      'Chrome/105.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Google Chrome";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
    }

    def parse(self, response):
        for data in response.css('div[id="content_enterprises_2"] li'):
            item = dict()
            item['Business Name'] = data.css('div.group-info a[title]::text').get('').strip()
            detail_url = data.css('div.group-info a[title]::attr(href)').get('').strip()
            item['Street Address'] = data.css('div.content-info-comp p:nth-child(1)::text').get('').strip()
            item['Phone Number'] = data.css('div.content-info-comp p:nth-child(2)::text').get('').strip().replace(
                "\xad", '')
            item['Description'] = data.css('div.info-map-bottom p::text').get('').strip()
            item['Occupation'] = 'Hotels'
            item['Source_URL'] = 'https://www.alabama-webbusiness.com/search.php?q=hotel'
            item['Lead_Source'] = 'alabama-webbusiness'
            if detail_url:
                item['Detail_Url'] = self.detail_base.format(detail_url)
            yield item

        next_page = response.xpath('//a[contains(text(), "next")]/@href').get()
        if next_page:
            yield scrapy.Request(url=self.base_url.format(next_page), callback=self.parse, headers=self.headers)



