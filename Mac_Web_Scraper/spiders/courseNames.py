import scrapy
from selenium import webdriver
import json
import re

'''
Had to use selenium to change the department from the dropdown on the website
'''

class CourseNamesSpider(scrapy.Spider):
    name = "coursenames"

    # start_urls = ["https://academiccalendars.romcmaster.ca/content.php?catoid=38&navoid=8070"]

    def __init__(self):
        options = webdriver.ChromeOptions()
        options.add_argument('headless')
        self.driver = webdriver.Chrome(chrome_options=options)
        self.index = 0
        self.keys = self.readDepartments()[0]
        self.values = self.readDepartments()[1]
        # self.driver.get("https://academiccalendars.romcmaster.ca/content.php?catoid=38&navoid=8070")
        # self.driver = webdriver.Chrome()
    
    def start_requests(self):
        homeurl = "https://academiccalendars.romcmaster.ca/content.php?catoid=38&navoid=8070"
        self.driver.get(homeurl)
        url = self.changeInputs(self.keys[self.index], self.values[self.index])
        yield scrapy.Request(url, self.parse)


    def parse(self, response):
        # print (self.keys)
        # print (self.values)
        self.index += 1
        anchorTags = response.xpath("//table[@class='table_default'][2]/tr[position()>2 and position()<last()]/td[2]/a/text()").extract()
        for i in range(len(anchorTags)):
            fullName = anchorTags[i]
            department = re.search(r"^[\w]*", anchorTags[i])
            courseCode = re.search(r"\b[A-Z0-9]{4}\b", anchorTags[i])
            courseName = re.search(r"(?<= - ).*", anchorTags[i])
            yield {
                "fullName" : fullName.strip(),
                "department" : department.group(0).strip(),
                "courseCode" : courseCode.group(0).strip(),
                "courseName" : courseName.group(0).strip()
            }
        url = self.changeInputs(self.keys[self.index], self.values[self.index])
        yield response.follow(url, self.parse)

    def readDepartments(self):
        with open("departments.json", "r") as f:
            departments = json.load(f)
        departments = departments[0]["departments"]
        keys =  list(departments.keys())
        values = list(departments.values())
        return (keys, values)

    def changeInputs(self, key, value):
        dptPrefixElement = self.driver.find_element_by_xpath("//select[@id='courseprefix']")
        dptTypeElement = self.driver.find_element_by_xpath("//select[@id='coursetype']")
        filterElement = self.driver.find_element_by_xpath("//input[@id='search-with-filters']")
        dptPrefixElement.send_keys(key)
        dptTypeElement.send_keys(value)
        filterElement.click()
        return self.driver.current_url