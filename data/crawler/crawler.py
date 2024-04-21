from typing import Any, Iterable
import scrapy, asyncio
import os, re
import json, requests
from scrapy.http import Response, Request

class KLSpider(scrapy.Spider):
    name = 'kl-spider'
    # content_topics = ['medical negligence']


    # custom_settings = {
    #     'DUPEFILTER_CLASS': None,
    # }
    # start_urls = ['http://kenyalaw.org/caselaw/#specific-search']

    def start_requests(self) -> Iterable[Request]:
        self.folder = input('Please input subject content you desire to scrape here: ')
        self.path = f'../files/{self.folder}'
        if not os.path.exists(self.path):
            os.makedirs(self.path)

        with open(f'{self.path}/{self.folder}.json', 'w+') as f:
            f.write('{}')

        self.payload = {
            "content": self.folder,
            "subject": "",
            "case_number": "",
            "parties": "",
            "date_from": "01 Jan 2013",
            "date_to": "01 Jan 2024",
            "submit": "Search"
        }

        self.headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8,fr;q=0.7",
            "Cache-Control": "max-age=0",
            # "Connection": "keep-alive",
            # "Content-Length": "113",
            # "Content-Type": "application/x-www-form-urlencoded",
            # "Cookie": "_ga_TP7XYRXK16=GS1.1.1709795094.1.0.1709795094.0.0.0; _gid=GA1.2.1457139823.1711359305; _ga=GA1.2.1417702227.1709795014; _ga_SCV6JN18JH=GS1.1.1711363403.5.1.1711363534.0.0.0; cisession=a%3A4%3A%7Bs%3A10%3A%22session_id%22%3Bs%3A32%3A%2281a38e5f738b7ac81806277b2b91336c%22%3Bs%3A10%3A%22ip_address%22%3Bs%3A15%3A%22192.168.100.101%22%3Bs%3A10%3A%22user_agent%22%3Bs%3A101%3A%22Mozilla%2F5.0+%28X11%3B+Linux+x86_64%29+AppleWebKit%2F537.36+%28KHTML%2C+like+Gecko%29+Chrome%2F123.0.0.0+Safari%2F537.36%22%3Bs%3A13%3A%22last_activity%22%3Bi%3A1711442062%3B%7Ddebd2b317788342ef1a43e613177c5c2; _gat=1",
            # "Host": "kenyalaw.org",
            # "Origin": "http://kenyalaw.org",
            # "Referer": "http://kenyalaw.org/caselaw/cases/advanced_search/",
            # "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
        }
        # sc_request = Request(
        #     method='POST',
        #     url='http://kenyalaw.org/caselaw/cases/advanced_search/',
        #     body=json.dumps(payload),
        #     headers=headers,
        # )

        # for content in self.content_topics:
        #     self.payload['content'] = content
        #     self.folder = content
            
        self.last_page = None
        yield scrapy.FormRequest(
            'http://kenyalaw.org/caselaw/cases/advanced_search',
            callback=self.parse,
            method='POST',
            meta={'folder': self.folder},
            formdata=self.payload,
            dont_filter = True,
            )
            
    def parse_content_type(self, response):
        content_type = response.request.meta['folder']

        # current_page = int(response.request.url.split('/')[-2])
        if response.request.url == 'http://kenyalaw.org/caselaw/cases/advanced_search':
            current_page = 0
        else:
            current_page = int(response.request.url.split('/')[-2])
        print(f'{content_type} -> Page {current_page}')

        next_page_url = f'http://kenyalaw.org/caselaw/cases/advanced_search/page/{current_page + 10}/'

        if current_page + 10 <= self.last_page and response.request.meta['folder'] == content_type:
            self.payload['content'] = content_type
            yield scrapy.FormRequest(
                next_page_url,
                callback=self.parse,
                method='POST',
                meta={'folder': content_type},
                formdata=self.payload,
                dont_filter=True,
            )

    def parse(self, response: Response) -> Any:
        folder = response.meta['folder']
        files = response.xpath('//*[@id="google-search"]/div[@class="post"]')
        print('=======================================================', '\n')
        print(f"{folder} -> {response.request.url}", '\n')
        print('=======================================================')

        # folder_path = f"/home/kafka/Class/CSI/data/files/{folder}"
        # os.mkdir(folder_path)

        if not self.last_page:
            last_page_link = response.xpath('//*[@class="pagination"]')[0].xpath('div[1]/ul/li[@class="last"]/a/@href').extract()
            # /html/body/div[5]/div[1]/div/div[2]/div[2]/div/div[1]/div[3]/div[1]/ul/li[13]/a
            # print(last_page_link)
            self.last_page = int(last_page_link[0].split('/')[-2])
            # print(self.last_page)
        
        for file in files:
            print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
            # print(file.xpath('table/tr[1]/td/h2/text()').extract())
            link_to_file = file.xpath('a/@href').extract()[0]
            id = link_to_file.split('/')[-2]
            # print(id)

            try:
                judges = file.xpath('p[1]/text()').extract()[0].split(',')
            except:
                judges = file.xpath('p[1]/text()').extract()

            details = {
                'case_number': file.xpath('table/tr[2]/td[1]/text()').extract()[1].strip(' '),
                'date_delivered': file.xpath('table/tr[2]/td[2]/text()').extract()[0].strip(' '),
                'judges': judges,
                'court': file.xpath('p[2]/text()').extract()[0],
                'parties': file.xpath('p[3]/text()').extract()[0].split(' v '),
                'advocates': file.xpath('p[4]/text()').extract(),
                'citation': file.xpath('p[5]/text()').extract()[0].strip('\n '),
                # 'date': file.xpath('table/tr[2]/td[2]/text()').extract()[0],
                'title': file.xpath('table/tr[1]/td/h2/text()').extract()[0].strip('\n '),
                'file_page_url': f'http://kenyalaw.org/caselaw/caselawreport/?id={id}',
                'file_download_url': f'http://kenyalaw.org/caselaw/cases/export/{id}/pdf'
            }
            download_url = details['file_download_url']
            title = details["title"].strip('\n ')
            case_number = details['case_number']
            print(title)
            print(case_number)
            # print(details['judges'])
            # print(details['date_delivered'])
            print(download_url)
            # self.save_pdf(download_url, case_number, folder)

            with open(f'{self.path}/{self.folder}.json', 'r') as f:
                data = json.load(f)
                data[folder] = data.get(folder, {})
                data[folder]['headers'] = data[folder].get('headers', self.headers)
                data[folder]['payload'] = data[folder].get('payload', self.payload)
                data[folder]['cases'] = data[folder].get('cases', [])
                data[folder]['cases'].append(details)
            
            with open(f'{self.path}/{self.folder}.json', 'w') as f:
                json.dump(data, f)

            # pattern1 = r'\((.*?)\)'
            # pattern1 = r'\((\([^()]+\)*)\)'
            # pattern1 = r'\(([^()]*(?:\([^()]+\))*[^()]*)\)'
            # pattern2 = r'\b(?:Case|Civil|Petition|Appeal|Judicial|Cause)'
            # matches = re.findall(pattern1, title)
            # final_matches = [match for match in matches if re.search(pattern2, match)]

            # try:
            #     case_name = final_matches[0]
            # except:
            #     case_name = title
            # print(details['Case Number'])
            print("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")

            # self.save_pdf(download_url)
        
        # next_page = response.xpath('//*[@id="google-search"]/div[14]/div[1]/ul/li[6]/a/@href').extract()[0]
        # if next_page:
        # try:
        #     if response.request.url == 'http://kenyalaw.org/caselaw/cases/advanced_search':
        #         number = 10
        #     else:
        #         number = int(response.request.url.split('/')[-2]) + 10
        #     print(number)
        #     next_page = f'http://kenyalaw.org/caselaw/cases/advanced_search/page/{number}/'
        #     print(f'/////////////////////////////>>>{next_page}')
        #     yield scrapy.FormRequest(
        #         next_page,
        #         callback=self.parse,
        #         method='POST',
        #         meta={'folder': self.folder},
        #         formdata=self.payload,
        #         # dont_filter = True,
        #         )
        # except Exception as e:
        #     print(e)
        
        yield scrapy.Request(response.url, callback=self.parse_content_type, meta=response.meta, dont_filter=True)

    
    def save_pdf(self, url, name, folder, base_folder='/home/kafka/Class/CSI/data/files/'):
        path = base_folder + folder
        if not os.path.exists(path):
            os.makedirs(path)

        response = requests.get(url)
        file = f"{path}/{name}.pdf"
        self.logger.info('Saving PDF %s', file)

        with open(file, 'wb') as f:
            f.write(response.content)