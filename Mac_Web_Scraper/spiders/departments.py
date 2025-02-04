import scrapy

class DepartmentsSpider(scrapy.Spider):
    name = "departments"

    start_urls = ['https://academiccalendars.romcmaster.ca/content.php?catoid=38&navoid=8070']

    def parse(self, response):
        dptPrefix = response.xpath("//select[@id='courseprefix']/option")
        dptType = response.xpath("//select[@id='coursetype']/option")
        departments = {}
        for i in range(1, len(dptPrefix)):
            departments[dptPrefix[i].xpath('text()').extract_first()] = dptType[i].xpath('text()').extract_first()
        
        yield {"departments" : departments}