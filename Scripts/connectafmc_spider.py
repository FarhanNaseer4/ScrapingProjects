from datetime import datetime

import scrapy


class ConnectafmcSpiderSpider(scrapy.Spider):
    name = 'connectafmc_spider'
    request_url = 'https://connectafmc.force.com/connections/apex/ConnectCare_Provider_Table?id={}&tour=&isdtp=p1&sfdcIFrameOrigin=https://connectafmc.force.com&nonce=&clc=0&sfdcIFrameHost=web'
    first_request = 'https://connectafmc.force.com/connections/apex/ConnectCare_Provider_Table?id=a5Y0G0000012A7xUAE&tour=&isdtp=p1&sfdcIFrameOrigin=https://connectafmc.force.com&nonce=&clc=0&sfdcIFrameHost=web'
    custom_settings = {
        'FEED_URI': 'connectafmc.csv',
        'FEED_FORMAT': 'csv',
        'FEED_EXPORT_ENCODING': 'utf-8-sig',
        'FEED_EXPORT_FIELDS': ['Business Name', 'Full Name', 'First Name', 'Last Name', 'Street Address',
                               'Valid To', 'State', 'Zip', 'Description', 'Phone Number', 'Phone Number 1', 'Email',
                               'Business_Site', 'Social_Media', 'Record_Type',
                               'Category', 'Rating', 'Reviews', 'Source_URL', 'Detail_Url', 'Services',
                               'Latitude', 'Longitude', 'Occupation',
                               'Business_Type', 'Lead_Source', 'State_Abrv', 'State_TZ', 'State_Type',
                               'SIC_Sectors', 'SIC_Categories',
                               'SIC_Industries', 'NAICS_Code', 'Quick_Occupation', 'Scraped_date']
    }
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'Connection': 'keep-alive',
        # 'Cookie': 'BrowserId_sec=NYOodULoEe2BYkusFtKqBA; CookieConsentPolicy=0:1; LSKey-c$CookieConsentPolicy=0:1; sfdc-stream=!pb6LErQm9M/aWY2iCXfG13Hm/GpyChkYYmGdaFWrIefamiXt1SpA4/dF6YsvwUlR/Yktu2czGHR0dQ==; force-proxy-stream=!M5R9MQy8ZSgm+sv4Zfgr7VhjytKdRtClsxtBfaBNOlYsSs5SJfels+tRbm6jRymlOBgRDFtXnIJfvQ==; force-stream=!pb6LErQm9M/aWY2iCXfG13Hm/GpyChkYYmGdaFWrIefamiXt1SpA4/dF6YsvwUlR/Yktu2czGHR0dQ==; pctrk=8e40fd55-51c7-4961-8eac-87dd37cb0a99',
        # 'Referer': 'https://connectafmc.force.com/connections/s/county-object/a5Y0G0000012A7yUAE/ashley',
        'Sec-Fetch-Dest': 'iframe',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/107.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Google Chrome";v="107", "Chromium";v="107", "Not=A?Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"'
    }

    def start_requests(self):
        yield scrapy.Request(url=self.first_request, callback=self.parse, headers=self.headers)

    def parse(self, response):
        for data in response.xpath('//select[@id="countySelector"]/option/following-sibling::option'):
            value = data.xpath('./@value').get()
            req_id = value.split('/')[-1]
            yield scrapy.Request(url=self.request_url.format(req_id), callback=self.parse_data, headers=self.headers)

    def parse_data(self, response):
        for data in response.xpath('//table[@id="providerTable"]//tr/following::tr'):
            item = dict()
            item['Business Name'] = data.css('th[data-label="Provider Name"] div a::text').get('').strip()
            item['Street Address'] = data.css('td[data-label="Address"] div::text').get('').strip()
            item['State'] = data.css('td[data-label="State"] div::text').get('').strip()
            item['Phone Number'] = data.css('td[data-label="Phone Number"] div::text').get('').strip()
            item['Source_URL'] = 'https://connectafmc.force.com/connections/s/county-object/a5Y0G0000012A7yUAE/ashley'
            item['Lead_Source'] = 'connectafmc'
            item['Occupation'] = data.css('td[data-label="Accepting New Patients"] div::text').get('').strip()
            item['Record_Type'] = 'Business'
            item['Scraped_date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            yield item
