from bs4 import BeautifulSoup

#must be done before requests
from gevent import monkey as curious_george
curious_george.patch_all(thread=False, select=False)

import grequests
import requests

class Subject:
    def __init__(self, code: str):
        self.code = code.lower()

        #initialise variables
        self.name = ''
        self.semesters_available = []
        #the following are lists of codes
        self.non_allowed = []
        self.is_prequisite_for = []
        #the following are lists of relations of codes
        self.prerequisites = [] 
        self.corequisites = []

        #populate the variables
        self.generate_subject()
    
    def __repr__(self) -> str:
        return f'Subject("{self.code.upper()}")'

    def generate_link(self) -> str:
        return f'https://handbook.unimelb.edu.au/2022/subjects/{self.code}'

    def generate_subject(self):
        #fetch subject data
        urls = [
            self.generate_link(),
            self.generate_link()+'/eligibility-and-requirements'
        ]
        r = grequests.map((grequests.get(url) for url in urls))
        main = BeautifulSoup(r[0].content, features="html.parser")
        requirements = BeautifulSoup(r[1].content, features="html.parser")

        #get subject name
        name = main.find('span', {'class': 'header--course-and-subject__main'})
        self.name = name.text

        #get subject availability
        course_box = main.find('div', {'class': 'course__overview-box'})
        self.semesters_available = [
            item.text.split(' - ')[0] for item in course_box.tbody.td
        ]

        #get co/nonrequisites
        entry = requirements.find('h3', string="Corequisites")

        #requires extra testing
        cotable = entry.next_sibling.find('table')
        if cotable:
            self.corequisites = [
                row.td.text.lower() 
                for row in cotable.find_all('tr')
                if row.find('td')
            ]
        
        entry = requirements.find('h3', string="Non-allowed subjects")
        notable = entry.next_sibling.find('table')
        if notable:
            self.non_allowed = [
                row.td.text.lower() 
                for row in notable.find_all('tr')
                if row.find('td')
            ]
    
    def pprint(self):
        print(f'{self.name}:')
        print(self.generate_link())
        print(
            'Semesters available:', 
            ', '.join(self.semesters_available)
        )
        print(
            'Corequisites:', 
            ', '.join([x.upper() for x in self.corequisites])
        )
        print(
            'Non allowed subjects:', 
            ', '.join([x.upper() for x in self.non_allowed])
        )