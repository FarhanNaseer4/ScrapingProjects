import csv
import json
from datetime import datetime

import scrapy


class KohlerSpider(scrapy.Spider):
    name = 'kohler'
    request_api = 'https://www.kohler.com/apirequest/maps/stores?$format=json&brand=kohler&spatialFilter=nearby(%27{}%27,64)&$select=EntityID,BPnumber,LocationName,AddressLine,AddressLine2,AdminDistrict,PostalCode,LocationType,CountryRegion,Latitude,__Distance,Longitude,Phone,OpenUntil,WeekdayHours,WeekendHours,StateLong,ThreeSixtyImage,HeroImage,ServicesDesign,ServicesInstallation,ServicesContractor,Locality,SalesforceLead&$filter=(LocationType+Eq+%27KOHLER+Store%27+Or+LocationType+Eq+%27Showroom%27+Or+LocationType+Eq+%27Parts+Dealer%27+Or+LocationType+Eq+%27Home+Center%27)'

    custom_settings = {
        'FEED_URI': 'kohler.csv',
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
        'authority': 'www.kohler.com',
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJrY29tLWd1ZXN0LXRva2VuIiwic3ViIjoia2NvbS1ndWVzdC10b2tlbiIsImp0aSI6IjhiZDQ1YWEyLTJjYTQtNDQzNy04ZmVjLTIxZjc3ZTg0OWRhOCIsImlhdCI6MTY2OTI3MDA1NSwiZXhwIjoxNjY5Mjc3MjU1LCJnSWQiOiIwMWQyZDUyOC1mYTQ0LTQ2NTAtYTkwNi0yYmJiMzRhYjFjNDAiLCJzY29wZSI6WyJndWVzdCJdLCJzY3AiOlsiZ3Vlc3QiXX0.MBVa3-wnu42kb7X9PiP82KzALv8t9_WPLA_ponIjn4I',
        'cookie': 'userLocation=AS+PK++KARACHI+24.87+67.05+GMT+5+; s_ecid=MCMID%7C87500011114464419922542046215928435919; _gcl_au=1.1.100066244.1669203244; _mibhv=anon-1669203244761-4949019443_9060; _rdt_uuid=1669203247428.043885e8-32f0-4604-a4d3-65f285044037; rmStore=dmid:8765; _pin_unauth=dWlkPU16UTBabU0xT0RZdFpHUmlaUzAwT1RJM0xXSXdaR0V0TVdGaE5EZGlPR1ZoWkdGbQ; _tt_enable_cookie=1; _ttp=c1afe1e0-2a33-48df-aa02-ad1e57af0191; QuantumMetricUserID=f817be8446a09ea9b03dfb25c6203664; AWSALB=DdEUtPcGNjHIoudxzNO3oUXVaLKvXKrnocprUKSJR15ES0Fkxzp8dA/vUb8RuBB8znPywFAj3+kMHzszBT+zEJlk6paN6RfrPMBeMXEw3lAUwCGF3TTp2JK/81/6; AWSALBCORS=DdEUtPcGNjHIoudxzNO3oUXVaLKvXKrnocprUKSJR15ES0Fkxzp8dA/vUb8RuBB8znPywFAj3+kMHzszBT+zEJlk6paN6RfrPMBeMXEw3lAUwCGF3TTp2JK/81/6; AKA_A2=A; _abck=580546CF6D66C1C091607D21064C2CF5~-1~YAAQDCg0F6ATu5iEAQAAx40/qAg/k3Lr4Jfj8SJioDBC33smr6wrN2QR0g3+v4L+ff94hZXZ+LPbFg5UOYYYYwEH5ePBDHPz80vDcZI7gQI4PyXzozugI0F2Je2bYHD/qvXdsC+FK5Jdf0RreJefNYp8mkDwGn4SyrRkrbGJuNWO13jpNkRQGFQkHhpcxa1oUUcd4BM/hRV4etzUkmcn3v9AYgoDKiin4QLAFM+t0oWff/C4gLh18ViJ/P3UjkMS+e3jfDxYONTbOTZTr1QqTtypDavieFpm60KjQhE5YO1eEkn0SdCAaoQ3XKWHMVnGb1mkCSZoO8OWJWWWneX4A6IErZbhUfSur8eETjlWH1CFj55tGKiM2sRXz7iAbIJ6uNmEyynQaFG1Kw==~-1~-1~-1; bm_sz=2AE8EAD6B8605BBB69113303316720F6~YAAQDCg0F6MTu5iEAQAAx40/qBFnux+UmPyvFrASUVPLgrCaQ+dbgb3T6wYKYHE+AqpQvF2RTRLjnipwMzVmlFKTo4qQMghPrwg0hlccFmMDm22wMQLCap1jr77BS7b6+LK6g9v+yPrms92PqZMrP+FQfBmsrV7N7YMGCuc3H5g9Pe18g4RZbJjFdj1VCW7jCmRyPbzRBO6nN68rmmCw7RKUXiw0SqYu+M/36MSD4z8koEnBbDlcfOQXGxTkEiSHT+lpY1WeOCha5RqYZgDC9tPfgsDQvOCCLpWNXJsKH8ubkig=~3291441~3487288; previousPage=kohler:locations; at_check=true; notice_behavior=implied,eu; bounceClientVisit4643v=N4IgNgDiBcIBYBcEQM4FIDMBBNAmAYnvgO6kB0A1gPZxgCmATmQMZUC2RdAdkWFcwEMEASypd0GfAEdMAEQwA2AIwAGACwgANCAYwQWkMJQB9AOZVjKOihSiuMAGYCwV7UbMRL122MfOrAL5AA; QuantumMetricSessionID=67606890e09eff95680677149b6b2b64; AMCVS_A7C33BC75245AE0B0A490D4D%40AdobeOrg=1; AMCV_A7C33BC75245AE0B0A490D4D%40AdobeOrg=1176715910%7CMCIDTS%7C19320%7CMCMID%7C87500011114464419922542046215928435919%7CMCAAMLH-1669874861%7C3%7CMCAAMB-1669874861%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1669277261s%7CNONE%7CMCAID%7CNONE%7CvVersion%7C5.4.0; s_pers=%20gpv_pn%3Dkohler%253Alocations%7C1669271861175%3B%20gpv_url_np%3Dhttps%253A%252F%252Fwww.kohler.com%252Fen%252Flocations%7C1669271861181%3B; _uetsid=bdb4e4806b2211eda56e83af8cea82d0; _uetvid=bdb528906b2211ed88c3abf0280a6c42; ipe_s=76883d8f-26e3-26ad-778b-557f167279b1; IPE_LandingTime=2022-10-4-11-7-43; ipe.23085.pageViewedCount=1; ipe.23085.pageViewedDay=328; ipe_23085_fov=%7B%22numberOfVisits%22%3A2%2C%22sessionId%22%3A%2276883d8f-26e3-26ad-778b-557f167279b1%22%2C%22expiry%22%3A%222022-12-23T11%3A34%3A08.941Z%22%2C%22lastVisit%22%3A%222022-11-24T06%3A07%3A43.303Z%22%7D; s_sess=%20s_tp%3D2735%3B%20s_cc%3Dtrue%3B%20s_ppv%3Dkohler%25253Alocations%252C46%252C45%252C1266%3B; mbox=PC#8ebd7db0692d45208c478b03a1660e52.38_0#1732514935|session#866960435211413a97e363f7f1c4651b#1669271995; RT="z=1&dm=www.kohler.com&si=166af1c5-2bfb-4403-a88a-e85e57207bd2&ss=lauoc63c&sl=1&tt=3bi&rl=1&ld=3bo"; ak_bmsc=D0E265403FD4E8EC6A8DB24DFFC1B9D9~000000000000000000000000000000~YAAQDCg0F3MVu5iEAQAAHfNAqBEMYCjsd+7ZN7y3HUU2IRzK68Sln/DQ6Qwxb8pVkjMHox4ebBjZdzVh39Ed+hwKMzEDl2B6kzGrWhVujP3Plm1zRoZ4zbtVO6iACoDRTN/VZVN3x4Zm4zfBw5EwzUOEIFhFgIBWnMdui47O/pmFtanPZ32dxETRJ25cbSgt9kjwDVT6HNB22zmixhmeJlHCr64q2BrySA7fFtU9HV89Rb4swO+io9qNl/Sz2O7J4LsueB5cDRRYjR57VjqcL3SA3h3Z4pynEjsa/XSxFfHndb6CsqKpgT0aS8xFTae4td1qyiPC0ga/LGherNCur+iZQuvPkesfanz6JuKvuwWU/zyIb62HzEPsb1cHqbWWKn3Ir47FLHtpF6SkP4T32F6v5qJ57h7hVyN3OO+iOro/n5d08ASnrAdFla35eJfLV7Ql4MM6XB6oMKsiilRNnfuKVxzXOMUASrGoGQyz691AbbVzJw4715EftFt7T2N57g==; bm_sv=FDDB14ED912CE27D01A785A81182F5E0~YAAQDCg0F3QVu5iEAQAAHfNAqBHNIVY2IFTzvCmyiAVRi07INXBukD1S8Nx7fwimrgHOq3BgYXs6KFE/adswRIkwFNQTh8Q2RtgD3HG8HOF9LmStJCuvmRgP6wUhjlnQHRi6SMKq32xzQ8GImUBEX84gcl8MK9LJP2bhjjM1WYAkhywhRac3Ty4ZrOpZ0q18J4CpqtYawe9aHVhpyL2noGoE3SG16kjrl7X5p4ry7P4IQ003vN8XSdy5CPQV4kYznQ==~1; ak_bmsc=D0E265403FD4E8EC6A8DB24DFFC1B9D9~000000000000000000000000000000~YAAQF54QAoOsvISEAQAAFFpDqBF/05Mw86ABvVupc0om84ZYd5S7ie+9ZGbOE/w1cs4T0EX7mvBDoXwGnbuL+WTDco4BJnKAoxBCKAmRLIw0Bs5VzeZXrTmJRmCxDlMpSj+iiHnN6DBzbOToXu/B2lA507nJcdZj0RetYJK/07RMVcKeEeMEBp3ZINKbPAtvPNnva0GxlxwFd88z9cmEWVBA/vI/9NdgIAAzub3awBk3Pjz4qGrkceBujmIJ5BnsifXZ153ymplAw3peDRfN/ccfYUqJ9sN3uYxz5oXg8kuHntD6sDqXjKNN83MprM2aHcjHy6ePW3QMloHhx1TECOzmDXIb3NwsxkRUe7jqy3btjYnjXMa7pjohoI9r3aU+WgQiwSsvMy/Iwrz+srC5VuXl1sDdap/LZ1UdoihgQRnEGLMu3khQNzVOCs3//UtvChHF8AWLgnGAv0q6sBXzs3Xca3TP56dVxlVYbwvpwutSpT4=; bm_sv=FDDB14ED912CE27D01A785A81182F5E0~YAAQF54QAoSsvISEAQAAFFpDqBGRV2iIvdi8wmGd8sZ9zvXHrahw35atrd36g1Q5FevfVEhoJEeUQHRHH4TIvnVVI5VrkgsUzh3sM2RqgEY0IViUn1c+zMYvCbJmGvepzGteRGOgZXPbz/THFyAbZNjOsnJmxFjs2Pf4xIFkc037LssZgiS9CRWOwJQVd2NImAZMnbXGZ7JGuTFTfSKzDtb8PTp+PAhg71VNQX0M41GTlT34XQqk6ikrBzFjo1V4ng==~1; userLocation=AS+PK++KARACHI+24.87+67.05+GMT+5+',
        'newrelic': 'eyJ2IjpbMCwxXSwiZCI6eyJ0eSI6IkJyb3dzZXIiLCJhYyI6IjMxMzAzMzAiLCJhcCI6IjEzODU4NzcyNDYiLCJpZCI6ImYxNGRhYWY4NDU3YWFlYmIiLCJ0ciI6IjNmNWU4NGFmNGY1NDY5OWRlNTU0ZDE2YmVhNDQzNzcwIiwidGkiOjE2NjkyNzAxNDAxMjV9fQ==',
        'referer': 'https://www.kohler.com/en/locations?q=36104',
        'sec-ch-ua': '"Google Chrome";v="107", "Chromium";v="107", "Not=A?Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'traceparent': '00-3f5e84af4f54699de554d16bea443770-f14daaf8457aaebb-01',
        'tracestate': '3130330@nr=0-1-3130330-1385877246-f14daaf8457aaebb----1669270140125',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.request_zip = self.get_search_zip()

    def get_search_zip(self):
        with open('state_zip.csv', 'r', encoding='utf-8-sig') as reader:
            return list(csv.DictReader(reader))

    def start_requests(self):
        for data in self.request_zip:
            yield scrapy.Request(url=self.request_api.format(data.get('Zip_code', '')),
                                 callback=self.parse, headers=self.headers)

    def parse(self, response):
        try:
            json_data = json.loads(response.body)
            result = json_data.get('d', {}).get('results', [])
            for data in result:
                item = dict()
                item['Business Name'] = data.get('LocationName', '')
                item['Street Address'] = data.get('AddressLine', '')
                item['State'] = data.get('AdminDistrict', '')
                item['Zip'] = data.get('PostalCode', '')
                item['Phone Number'] = data.get('Phone', '')
                item['Latitude'] = data.get('Latitude', '')
                item['Longitude'] = data.get('Longitude', '')
                item['Source_URL'] = 'https://www.kohler.com/en/locations'
                item['Lead_Source'] = 'kohler'
                item[
                    'Meta_Description'] = "Planning a bathroom or kitchen refresh or renovation? Visit a KOHLER Store " \
                                          "to get inspiration and design advice, and explore products. Find a store " \
                                          "near you. "
                item['Occupation'] = data.get('LocationType', '')
                item['Record_Type'] = 'Business'
                item['Scraped_date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                yield item

        except Exception as ex:
            print(ex)
