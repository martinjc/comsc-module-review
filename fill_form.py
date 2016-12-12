import os
import requests
import subprocess

from html.parser import HTMLParser
from fdfgen import forge_fdf

from lib.handbookdata import *
from lib.pdfdata import *


class MLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)

SRC_DATA_DIR = os.path.join(os.getcwd(), 'src_data')
OUTPUT_DIR = os.path.join(os.getcwd(), 'dist')
SCRATCH_DIR = os.path.join(os.getcwd(), 'scratch')

filled_fields = []

def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    data = s.get_data()
    lines = data.split('\n')
    data = ''
    for line in lines:
        if line.strip():
            data += '%s\n' % line
    return data

def add_existing_data(key, value):
    filled_fields.append((key, value))

def get_description(descriptions, name):
    for description in descriptions:
        if description['descriptionName']['descriptionCode'] == name:
            return strip_tags(description['descriptionDetail'])
    return None

if __name__ == "__main__":

    for mcode in ['CM1101', 'CM1102', 'CM1103', 'CM1202', 'CM1209', 'CM6112']:
        filled_fields = []
        module_data = get_module_handbook(mcode)
        descriptions = module_data['descriptions']

        add_existing_data("module_name", module_data['module']['moduleName'])
        add_existing_data("delivery", get_description(descriptions, 'MAV_DELM'))
        add_existing_data("delivery_language", module_data['module']['language']['taught'])
        add_existing_data("external_subject_code", module_data['module']['extSubCode'])
        add_existing_data("background_reading", get_description(descriptions, 'MAV_READ2'))
        add_existing_data("essential_reading", get_description(descriptions, 'MAV_READ'))
        add_existing_data("learning_outcomes", get_description(descriptions, 'MAV_LOUT'))
        add_existing_data("level", module_data['module']['levelCode'])
        add_existing_data("assessment", get_description(descriptions, 'MAV_ASSM'))
        add_existing_data("module_code", module_data['module']['moduleCode'])
        add_existing_data("module_description", get_description(descriptions, 'MAV_DESC'))
        module_staff = module_data['occurrences']['staff']['moduleLeader']
        module_leader = '%s %s %s' % (module_staff['title'], module_staff['firstName'], module_staff['surname'])
        add_existing_data("module_leader", module_leader)
        add_existing_data("module_title", module_data['module']['moduleName'])
        add_existing_data("number_of_credits", module_data['module']['moduleCredits'])
        add_existing_data("school_code", module_data['module']['school']['schoolCode'])
        add_existing_data("semester", module_data['occurrences']['semester']['type'])
        add_existing_data("skills", get_description(descriptions, 'MAV_SKIL'))
        add_existing_data("syllabus_content", get_description(descriptions, 'MAV_SYLL'))

        count = 1
        for assessment in module_data['assessments']:
            add_existing_data('%d_assessment_contribution' % count, assessment['percentage'])
            add_existing_data('%d_assessment_title' % count, assessment['name'])
            add_existing_data('%d_assessment_type' % count, assessment['assessmentType']['assessmentType'])
            count += 1

        fdf = forge_fdf("", filled_fields, [], [], [])
        fdf_file = open(os.path.join(OUTPUT_DIR, 'data.fdf'), 'wb')
        fdf_file.write(fdf)
        fdf_file.close()

        subprocess.run(["pdftk", "templates/module_description_template.pdf",  "fill_form",  "dist/data.fdf", "output", "dist/%s.pdf" % mcode])
