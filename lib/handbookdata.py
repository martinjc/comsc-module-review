import os
import json
import requests

from datetime import datetime

FIELD_NAMES = ["module_name","module_code","level","delivery_language","module_leader","school_code","external_subject_code","number_of_credits","module_description","semester","learning_outcomes","delivery","skills","assessment","1_assessment_title","1_assessment_type","1_assessment_contribution","1_assessment_date","2_assessment_title","2_assessment_type","2_assessment_contribution","2_assessment_date","3_assessment_title","3_assessment_type","3_assessment_contribution","3_assessment_date","4_assessment_title","4_assessment_type","4_assessment_contribution","4_assessment_date","5_assessment_title","5_assessment_type","5_assessment_contribution","5_assessment_date","6_assessment_title","6_assessment_type","6_assessment_contribution","6_assessment_date","syllabus_content","essential_reading","background_reading"]

NON_ASSESSMENT_FIELD_NAMES = [
    "module_name","module_code","level","delivery_language","module_leader","school_code","external_subject_code","number_of_credits","module_description","semester","learning_outcomes","delivery","skills","assessment","syllabus_content","essential_reading","background_reading"
]

FIELD_NAMES_AND_LABELS = {
    "module_name": "Module Name",
    "module_code": "Module Code",
    "level": "Level",
    "delivery_language": "Language of Delivery",
    "module_leader": "Module Leader",
    "school_code": "School Code",
    "external_subject_code": "External Subject Code",
    "number_of_credits": "Number of Credits",
    "module_description": "Outline Description of Module",
    "semester": "Semester",
    "learning_outcomes": "Learning Outcomes - On completion of the module a student should be able to",
    "delivery": "How the module will be delivered",
    "skills": "Skills that will be practiced and developed",
    "assessment": "How the module will be assessed",
    "syllabus_content": "Syllabus Content",
    "essential_reading": "Essential Reading and Resource List",
    "background_reading": "Background Reading and Resource List"
}

ASSESSMENT_NAMES_AND_LABELS = {
    "_assessment_type": "Type",
    "_assessment_contribution": "Contribution (%)",
    "_assessment_title": "Title",
    "_assessment_date": "Week"
}

YEAR1 = ['CM1101', 'CM1102', 'CM1103', 'CM1104', 'CM1201', 'CM1202', 'CM1204', 'CM1205', 'CM1206', 'CM1208', 'CM1209']
YEAR2 = ['CM2101', 'CM2102', 'CM2103', 'CM2104', 'CM2105', 'CM2201', 'CM2203', 'CM2205', 'CM2206', 'CM2207', 'CM2208', 'CM2302', 'CM2303', 'CM2305', 'CM2500']
YEAR3 = ['CM3101', 'CM3103', 'CM3104', 'CM3105', 'CM3106', 'CM3107', 'CM3109', 'CM3110', 'CM3111', 'CM3112', 'CM3113', 'CM3114', 'CM3201', 'CM3202', 'CM3203', 'CM3301', 'CM3302', 'CM3303', 'CM3304']
MSC = ['CMT102', 'CMT103', 'CMT104', 'CMT105', 'CMT106', 'CMT107', 'CMT108', 'CMT111', 'CMT112', 'CMT202', 'CMT205', 'CMT206', 'CMT207', 'CMT209', 'CMT212', 'CMT213', 'CMT301', 'CMT302', 'CMT303', 'CMT304', 'CMT305', 'CMT306', 'CMT400']
NSA_YEAR1 = ['CM6112', 'CM6113', 'CM6114', 'CM6121', 'CM6122', 'CM6123']
NSA_YEAR2 = ['CM6211', 'CM6212', 'CM6213', 'CM6221', 'CM6222', 'CM6223']
NSA_YEAR3 = ['CM6311', 'CM6312', 'CM6321', 'CM6331', 'CM6332']

PFMSADSA = ['CMT304', 'CMT302', 'CMT306', 'CMT106', 'CMT209', 'CMT107', 'CMT105', 'CMT213', 'CMT202', 'CMT108', 'CMT206', 'CMT104', 'CMT111']
PFMSCITA = ['CMT302', 'CMT301', 'CMT103', 'CMT112', 'CMT207', 'CMT212', 'CMT202', 'CMT206']
PFMSCMPA = ['CMT303', 'CMT103', 'CMT205', 'CMT112', 'CMT102', 'CMT302', 'CMT212', 'CMT111', 'CMT202', 'CMT206', 'CMT207']
PFMSDSYA = ['CMT108', 'CMT112', 'CMT103', 'CMT209', 'CMT212', 'CMT111', 'CMT202']
PFMSISPA = ['CMT301', 'CMT306', 'CMT105', 'CMT213', 'CMT104', 'CMT202']
PFMSCDJ = ['CMT112', 'CMT103', 'CMT212', 'CMT111', 'CMT206']

MD_ASSESSMENT_FIELDS = [
    "1_assessment_title","1_assessment_type","1_assessment_contribution","1_assessment_date",
    "2_assessment_title","2_assessment_type","2_assessment_contribution","2_assessment_date",
    "3_assessment_title","3_assessment_type","3_assessment_contribution","3_assessment_date",
    "4_assessment_title","4_assessment_type","4_assessment_contribution","4_assessment_date",
    "5_assessment_title","5_assessment_type","5_assessment_contribution","5_assessment_date",
    "6_assessment_title","6_assessment_type","6_assessment_contribution","6_assessment_date"]
TF_ASSESSMENT_FIELDS = [
    "4-textbox-assessment1-title", "4-dropdown-assessment1-type", "4-textbox-assessment1-weighting", "4-textbox-assessment1-duration", "4-textbox-assessment1-hand_out_week", "4-textbox-assessment1-hand_in_week",
    "4-textbox-assessment2-title", "4-dropdown-assessment2-type", "4-textbox-assessment2-weighting", "4-textbox-assessment2-duration", "4-textbox-assessment2-hand_out_week", "4-textbox-assessment2-hand_in_week",
    "4-textbox-assessment3-title", "4-dropdown-assessment3-type", "4-textbox-assessment3-weighting", "4-textbox-assessment3-duration", "4-textbox-assessment3-hand_out_week", "4-textbox-assessment3-hand_in_week",
    "4-textbox-assessment4-title", "4-dropdown-assessment4-type", "4-textbox-assessment4-weighting", "4-textbox-assessment4-duration", "4-textbox-assessment4-hand_out_week", "4-textbox-assessment4-hand_in_week"
    ]

TF_SUPPORT_FIELDS = ["3-radio-require_phd_support_tutorials", "3-radio-no-require_phd_support_labs", "3-textbox-skills_for_lab_tutors", "3-textbox-skills_for_tutorial_tutors"]
TF_SOFTWARE_FIELDS = ["5-textbox-software_lab_requirements"]
TF_KIS_FIELDS = ["2-textbox-classroom_based_lectures", "2-textbox-classroom_based_seminars", "2-textbox-scheduled_online_activities", "2-textbox-practical_classes_and_workshops", "2-textbox-supervised_laboratory_time", "2-textbox-fieldwork", "2-textbox-exernal_visits", "2-textbox-work_based_learning", "2-textbox-scheduled_examination_assessment", "2-textbox-placement", "2-textbox-total_scheduled_teaching"]

BASE_URL = 'https://handbooks.data.cardiff.ac.uk'
ASPECTS = {
    'module_list': 'modulesrunning',
    'module': 'module'
}

def get_module_list(school, year=datetime.now().year):
    """
    Retrieves the list of all modules running in the supplied school and year

    If no module list is returned from the API, returns None
    """

    # API expects uppercase school acronym
    school = school.upper()

    # Construct the API url
    module_list_url = '%s/%s/%s/%s' % (BASE_URL, ASPECTS['module_list'], school, year)

    # Retrieve the data
    r = requests.get(module_list_url)
    data = r.json()

    # Check we got something back
    if data.get('modRunning'):
        return data['modRunning']
    else:
        return None

def get_module_handbook(module_code, occurence = ''):
    """
    Retrieves the module handbook for the supplied module code and occurence (if any)
    """

    module_code = module_code.upper()

    # Construct the API url
    module_handbook_url = '%s/%s/%s/%s' % (BASE_URL, ASPECTS['module'], module_code, occurence)

    # Retrieve and return the data
    r = requests.get(module_handbook_url)
    data = r.json()

    return data


if __name__ == '__main__':
    with open(os.path.join(os.getcwd(), 'src_data', 'COMSC_modules.json'), 'w') as output_file:
        module_list = get_module_list('COMSC')
        print(module_list)
        json.dump(module_list, output_file)
    with open(os.path.join(os.getcwd(), 'src_data', 'sample_module_description.json'), 'w') as output_file:
        module_details = get_module_handbook('CMT112')
        print(module_details)
        json.dump(module_details, output_file)
