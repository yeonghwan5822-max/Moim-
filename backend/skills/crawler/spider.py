import scrapy
from .items import PostItem

class CommunitySpider(scrapy.Spider):
    name = "community_spider"
    
    def __init__(self, start_urls=None, cookies=None, *args, **kwargs):
        super(CommunitySpider, self).__init__(*args, **kwargs)
        self.start_urls = start_urls if start_urls else []
        self.cookies = cookies if cookies else {}

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url=url,
                cookies=self.cookies,
                callback=self.parse
            )

    def parse(self, response):
        # Placeholder selector logic - NEEDS TO BE UPDATED based on actual site structure
        # This looks for common board lists
        posts = response.css('tr.board_list_row') # Example selector
        if not posts:
            posts = response.css('li.post_item') # Alternative example

        for post in posts:
            item = PostItem()
            item['title'] = post.css('.title a::text').get()
            item['url'] = response.urljoin(post.css('.title a::attr(href)').get())
            item['author'] = post.css('.author::text').get()
            item['date'] = post.css('.date::text').get()
            item['source'] = 'ebc_blue'
            
            if item['url']:
                yield scrapy.Request(item['url'], callback=self.parse_detail, meta={'item': item}, cookies=self.cookies)

        # Pagination
        next_page = response.css('.pagination .next::attr(href)').get()
        if next_page:
            yield response.follow(next_page, callback=self.parse, cookies=self.cookies)

    def parse_detail(self, response):
        item = response.meta['item']
        # Extract full content
        # Common content containers
        content = response.css('.post_content::text').getall() 
        if not content:
             content = response.css('#article_body::text').getall()
             
        item['content'] = ' '.join([c.strip() for c in content if c.strip()])
        yield item
