# URL Crawler

A simple web crawler.

## Getting Started

Given a starting URL it will start crawling and create a simple text sitemap in json format, showing the links between URLs.
This is intened to be run using AWS serverless services and the output will be uploaded to an S3 bucket. 

### Prerequisites

[Python 3](https://www.python.org/downloads/)
- The crawler uses [Scrapy](https://scrapy.org) (Scrapy is a free and open-source web-crawling framework written in Python).

[AWS Account](https://aws.amazon.com/account/) This is intended to be run in AWS using serverless servicess.

[NodeJs](https://nodejs.org/en/download/)
- The crawler is intended to be run using AWS serverless services (API Gateway, Lambda, Step Functions, S3). Deployment is done via Serverless Framework which can be installed as a node package.

[Serverless Framework](https://serverless.com/framework/docs/getting-started/)

Serverless Framework plugins:
  - [serverless-python-requirements](https://www.npmjs.com/package/serverless-python-requirements)
  - [serverless-pseudo-parameters](https://www.npmjs.com/package/serverless-pseudo-parameters)
  - [serverless-step-functions](https://www.npmjs.com/package/serverless-step-functions)

### Installing and usage

- Get Python 3, this was tested against 3.7 but any 3.x should do.
- Install serverless framework: `npm install -g serverless`
- Change directory to project folder and install serverless plugins:
        - `sls install plugin -n serverless-python-requirements`
        - `sls install plugin -n serverless-python-requirements`
        - `sls install plugin -n serverless-pseudo-parameters`
- Deploy to AWS
        - `sls deploy`

Once deployed, `sls` will output an URL to be used similar to:
```
Serverless StepFunctions OutPuts
endpoints:
  POST - https://7hy0y72rb1.execute-api.eu-west-1.amazonaws.com/dev/startCrawl
 ```
Use the URL provided and post a payload similar to the ones below.
Simple payload:
```
[ 
  {
  "spiderConfig" :
    {
      "url": "http://books.toscrape.com"
    }
  }
]
```
More complex example:
```
[ 
  {
  "spiderConfig" :
    {
      "url": "http://books.toscrape.com",
      "dry_run": "no",
      "scrapy_settings": {
        "LOG_LEVEL": "DEBUG",
        "FEED_URI": "/tmp/results.json",
        "CONCURRENT_ITEMS": "400",
        "CONCURRENT_REQUESTS": "64",
        "CONCURRENT_REQUESTS_PER_DOMAIN": "32",
        "CONCURRENT_REQUESTS_PER_IP": "0",
        "DNSCACHE_ENABLED": "True"
      }
    }
  },
  "Crawler started. Result will be uploaded to s3://url-crawler-account-id"
]
```
  - Required: `url` to be used as a starting point.
  - Optional: `dry_run` tell the spider to start crawling. Values: `yes` or `no` (defaults to `no` if not set).
  - Optional: `scrapy_settings` can be used to set spider settings. For list of possible settings see [Built-in settings reference](https://docs.scrapy.org/en/latest/topics/settings.html?highlight=settings#built-in-settings-reference).
 
The results will be uploaded to an S3 bucket named `url-crawler-#{AWS::AccountId}`.


## Running it locally

To run it locally you'll have to:
        - `virtualenv venv --python=python3`
        - `pip install Scrapy`
`sls invoke local -f crawl -p payload.json`
There is a `payload.json` file to be used as an example; adjust as you see fit.
Results will be sent to `FEED_URI` as set in `payload.json`.


## Deployment

Just run: `sls deloy` with desired parameters if needed (i.e. `-r region -s stage`).