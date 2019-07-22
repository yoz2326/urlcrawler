import os
import boto3
import scrapy

from scrapy.crawler import CrawlerProcess
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import Rule, CrawlSpider
from scrapy.utils.project import get_project_settings

from urllib.parse import urlparse
from datetime import datetime

# https://stackoverflow.com/a/54341505 (AWS Lambda installs its own handlers on the root logger, so you need to remove those handlers before you use Scrapy)
from logging import getLogger
getLogger().handlers = []

s3 = boto3.client('s3')
bucket_name = os.environ.get('BUCKET_NAME')

class UrlScraperItem(scrapy.Item):
    url_from = scrapy.Field()
    url_to = scrapy.Field()

class UrlCrawler(CrawlSpider):
    name = "urlcrawler"

    def parse_items(self, response):
        items = []
        # Only extract canonicalized and unique links (with respect to the current page)
        links = LinkExtractor(canonicalize=True, unique=True).extract_links(response)

        for link in links:
            is_allowed = False
            for allowed_domain in self.allowed_domains:
                if allowed_domain in link.url:
                    is_allowed = True
            if is_allowed:
                item = UrlScraperItem()
                item['url_from'] = response.url
                item['url_to'] = link.url
                items.append(item)
        return items

def crawl(event, context):
    try:
        # AWS Step Machine adds the output of the calling function to a list, pull configs from correct index
        for item in event:
            if 'spiderConfig' in item:
                indexNo = event.index(item)
        spiderConfig = event[indexNo]["spiderConfig"]
        print(f"Using payload: {spiderConfig}")

        start_url = spiderConfig["url"]
        domain = urlparse(spiderConfig["url"]).netloc
        time = datetime.now().strftime("%Y-%d-%m-%H-%M-%S")

        # some default scrapy settings
        settings = ({
            'USER_AGENT': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36',
            'LOG_LEVEL': 'ERROR',
            'FEED_FORMAT': 'json',
            'FEED_URI': f"s3://{bucket_name}/{domain}-{time}-results.json"
        })

        # allow overridding scrapy settings if needed
        if 'scrapy_settings' in spiderConfig:
            settings.update(spiderConfig["scrapy_settings"])
        
        process = CrawlerProcess(settings)
        CrawlerProcess(get_project_settings()) # log settings so we know what's used

        UrlCrawler.allowed_domains = [domain]
        UrlCrawler.start_urls = [start_url]

        UrlCrawler.rules = [
            Rule(
                LinkExtractor(
                    canonicalize = True,
                    unique = True,
                    allow = [start_url] # Do not crawl subdomains (limit to `start_url`)
                ),
                follow = True,
                callback = "parse_items"
            )
        ]

        process.crawl(UrlCrawler)
        if 'dry_run' not in spiderConfig.keys() or spiderConfig["dry_run"] != "yes":
            print(f"Starting UrlCrawler using URL: {start_url}")
            process.start() # the script will block here until the crawling is finished
        else:
            print("This is a dry run, not starting the crawling process.")


        print('All done.')
    except Exception as e:
        print(e)
        raise

if __name__ == "__main__":
    crawl('', '')