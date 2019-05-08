import numpy as np
import pandas as pd
import re
from Utils import Utils
from Tag_distance_calculator import TagDistanceCalculator


class SkillsDB:
    def __init__(self , skills_file_path , domains_file_path=None, actions_file_path=None,
                 domains_distance_matrix_path=None):

        print("Reading skills file...")
        all_skills_df = pd.read_csv(skills_file_path, delimiter=",", header=0)
        self.skills_names = all_skills_df["Skill"].values
        self.skills_prim_tags = all_skills_df["Primary Tag"].replace(" ", "", regex=True).values
        self.skills_sec_tags = all_skills_df["Secondary Tag"].replace(" ", "", regex=True).values
        self.skills_class = all_skills_df["Skill Class"].replace(" ", "", regex=True).values

        if not self.validate_input(domains_file_path, actions_file_path,
                                   domains_distance_matrix_path):
            raise ValueError(
                "Skills DB should be initialized with two files one for actions and other for domains "
                "or one Matrix file")

        if domains_distance_matrix_path is not None:
            print("Getting Domain Distance matrix from the file...")
            self.tdc = TagDistanceCalculator(domains_matrix_file_path=domains_distance_matrix_path)
        else:
            print("Reading Domains and Constructing the Graph...")
            self.tdc = TagDistanceCalculator(domains_file_path= domains_file_path,
                                             actions_file_path= actions_file_path)

        self.domains_abbv = self.tdc.get_domains_abbv()

        self.preprocess_tags(self.skills_prim_tags)
        self.preprocess_tags(self.skills_sec_tags)
        if self.validate_data():
            print("Data is Valid")

    def validate_input(self, domains_file_path, actions_file_path, domains_matrix_file_path):
        """
        checks if inputs is domain_matrix file or (domains_file_path and actions_file_path) no other input is allowed
        :param domains_file_path: path of the domains data
        :param actions_file_path: path of the actions data
        :param domains_matrix_file_path: path of the domain distance matrix
        :return: boolean whether to accept the input or not
        """
        validation_sum = 0
        if domains_file_path is not None:
            validation_sum += 1
        if actions_file_path is not None:
            validation_sum += 2
        if domains_matrix_file_path is not None:
            validation_sum += 3

        if validation_sum == 3:
            return True
        else:
            return False

    @staticmethod
    def handle_double_brackets_list( double_brackets_list):
        output_tags = []
        for double in double_brackets_list:
            actions_str, domains_str = tuple(re.sub("[()]", "", double).split("-"))
            actions = actions_str.split("/")
            domains = domains_str.split("/")
            for action in actions:
                for domain in domains:
                    output_tags.append(action + "-" + domain)

        return output_tags

    @staticmethod
    def handle_single_brackets_list( brackets_list, next_to_brackets_list):
        output_tags = []
        for i, bracket in enumerate(brackets_list):
            bracket_elements = re.sub("[()]", "", bracket).split("/")
            ntb_element = next_to_brackets_list[i]
            for bracket_element in bracket_elements:
                if ntb_element[0] == '-':
                    tag = bracket_element + ntb_element
                else:
                    tag = ntb_element + bracket_element
                output_tags.append(tag)

        return output_tags

    @staticmethod
    def parse_tags(tags_str):

        if tags_str == "-":  # if no tags
            return []

        brackets_pattern = re.compile("\(.*?\)")
        next_to_brackets_pattern = re.compile("[\w+\*]+-\(|\)-[\w+\*]+")
        no_brackets_pattern = re.compile("[\w+\*]+-[\w+\*]+")
        double_brackets_pattern = re.compile("\([^-]*?\)-\([^-]*?\)")

        brackets_list = []
        next_to_brackets_list = []
        no_brackets_list = []
        double_brackets_list = []
        forbeden_zones = []

        for element in double_brackets_pattern.finditer(tags_str):
            double_brackets_list.append(element.group())
            forbeden_zones.append(element.span())

        for element in brackets_pattern.finditer(tags_str):
            add_it = True
            for forbeden_zone in forbeden_zones:
                if Utils.is_range_intersect(element.span(), forbeden_zone):
                    add_it = False
                    break
            if add_it:
                brackets_list.append(element.group())

        for element in no_brackets_pattern.finditer(tags_str):
            no_brackets_list.append(element.group())

        for element in next_to_brackets_pattern.finditer(tags_str):
            element_active_text = re.sub("[()]", "", element.group())
            next_to_brackets_list.append(element_active_text)

        all_tags = SkillsDB.handle_double_brackets_list(double_brackets_list)
        all_tags = all_tags + SkillsDB.handle_single_brackets_list(brackets_list, next_to_brackets_list)
        all_tags = all_tags + no_brackets_list

        return all_tags

    def preprocess_tags(self, skills_tags):
        for i, skill_tags_str in enumerate(skills_tags):
            skills_tags[i] = self.parse_tags(skill_tags_str)

    def validate_tags(self , skills_tags):
        valid_data = True
        for i , skill_tags in enumerate(skills_tags):
            for tag in skill_tags:
                tag_parts = tag.split("-")
                for tag_part in tag_parts:
                    if tag_part not in self.domains_abbv:
                        print("issue in skill",self.skills_names[i], "number", i+2, "domain'", tag_part, "'doesn't Exist" )
                        valid_data = False
        return valid_data

    def validate_data(self):
        valid_data = self.validate_tags(self.skills_prim_tags) and self.validate_tags(self.skills_sec_tags)
        return valid_data

    def get_skill_name_index(self, skill_name):
        return np.where(self.skills_names == skill_name)[0][0]

    def calc_skills_distance(self, skill1_name , skill2_name, debug=False):
        skill1_index = self.get_skill_name_index(skill1_name)
        skill2_index = self.get_skill_name_index(skill2_name)
        return self.tdc.multi_tag_distance(self.skills_prim_tags[skill1_index] , self.skills_prim_tags[skill2_index] ,debug=debug)

    # getters


# sdb = SkillsDB("skills.csv" , domains_distance_matrix_path="domains_distance_matrix.csv")
# sdb = SkillsDB("skills.csv" , domains_file_path="domains.csv" , actions_file_path="actions.csv")
#
# distance , debug_info = sdb.calc_skills_distance("ActionScript" , "C++", debug=True)
# print("Distance" , distance)
# print(debug_info)