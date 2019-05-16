import scrapy
from selenium import webdriver
import json
import re

class CourseNamesSpider(scrapy.Spider):
    name = "coursenames"

    # From the departments.json file the first entry (ANTHROP: Anthropology) has been removed because below url starts from first entry itself
    start_urls = ['https://academiccalendars.romcmaster.ca/content.php?filter%5B27%5D=ANTHROP&filter%5B29%5D=&filter%5Bcourse_type%5D=5647&filter%5Bkeyword%5D=&filter%5B32%5D=1&filter%5Bcpage%5D=1&cur_cat_oid=38&expand=&navoid=8070&search_database=Filter&filter%5Bexact_match%5D=1#acalog_template_course_filter']

    def __init__(self):
        options = webdriver.ChromeOptions()
        options.add_argument('headless')
        self.driver = webdriver.Chrome(chrome_options=options)
        self.driver.get("https://academiccalendars.romcmaster.ca/content.php?catoid=38&navoid=8070")
        # self.driver = webdriver.Chrome()

    def parse(self, response):
        # departments = self.readDepartments()      //table[@class='table_default'][2]/tbody/tr/td/a/

        # for i in departments:
        anchorTags = response.xpath("//table[@class='table_default'][2]/tr[position()>2 and position()<last()]/td[2]/a/text()").extract()
        courseNames = {}
        for i in range(len(anchorTags)):
            department = re.search("^[\w]*", anchorTags[i])
            courseCode = re.search(r"\b[A-Z0-9]{4}\b", anchorTags[i])
            yield {
                "fullName" : anchorTags[i],
                "department" : department.group(0),
                "courseCode" : courseCode.group(0)
            }       
            # url = self.changeInputs(i, departments[i])
        

    def readDepartments(self):
        with open("departments.json", "r") as f:
            departments = json.load(f)
        return departments[0]["departments"]

    def changeInputs(self, key, value):
        dptPrefixElement = self.driver.find_element_by_xpath("//select[@id='courseprefix']")
        dptTypeElement = self.driver.find_element_by_xpath("//select[@id='coursetype']")
        filterElement = self.driver.find_element_by_xpath("//input[@id='search-with-filters']")
        dptPrefixElement.send_keys(key)
        dptTypeElement.send_keys(value)
        filterElement.click()
        return self.driver.current_url