import numpy as np
import pandas as pd
import csv
import domain_distance_builder
import action_distance_builder
from Utils import Utils


class TagDistanceCalculator:

    def __init__(self, domains_file_path=None, actions_file_path=None, domains_matrix_file_path=None):

        # Validate Input
        if not self.validate_input(domains_file_path, actions_file_path,
                                   domains_matrix_file_path):
            raise ValueError("Tag calculator should be initialized with two files one for actions and other for domains")

        self.domains_abbv, self.domains_weight ,self.domains_distance_matrix = \
            self.get_domains_data(domains_file_path ,actions_file_path, domains_matrix_file_path)

        # self.actions_abbv, self.actions_weights, self.actions_distance_matrix =\
        #     self.get_actions_data(actions_file_path, action_matrix_file_path)




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

    def read_domains_distance_matrix(self, distance_matrix_file_path):
        with open(distance_matrix_file_path , 'r') as file:
            reader = csv.reader(file)
            rows = [r for r in reader]
            domains_abbv = np.array(rows[0])
            domains_weights = np.array(rows[1] , dtype= "float")
            domains_distance_matrix = np.array(rows[2:] , dtype="float")
            return domains_abbv, domains_weights,domains_distance_matrix

    def generate_domains_distance_matrix(self, domains_file_path , actions_file_path):
        self.ddb = domain_distance_builder.DomainDistanceBuilder(domains_file_path, actions_file_path)
        domains_distance_matrix = self.ddb.build_distance_matrix()
        domains_abbv = self.ddb.get_domains_abbv()
        domains_weights = self.ddb.get_domains_weights()
        return domains_abbv , domains_weights ,  domains_distance_matrix


    # def read_action_distance_matrix(self, distance_matrix_file_path):
    #     with open(distance_matrix_file_path, 'r') as file:
    #         reader = csv.reader(file)
    #         rows = [r for r in reader]
    #         actions_abbv = rows[0]
    #         actions_weight = rows[1]
    #         actions_distance_matrix = np.array(rows[2:], dtype="float")
    #         return actions_abbv,actions_weight, actions_distance_matrix
    #
    # def generate_actions_distance_matrix(self, actions_file_path):
    #     adb = action_distance_builder.ActionDistanceBuilder(actions_file_path)
    #     actions_distance_matrix = adb.build_distance_matrix()
    #     actions_wieght = adb.get_actions_weight()
    #     actions_abbv = adb.get_domains_abbv()
    #     return actions_abbv, actions_wieght, actions_distance_matrix

    def get_domains_data(self,domains_file_path,actions_file_path , domains_matrix_file_path):
        # Get Domains Distance Matrix
        if domains_file_path is not None:
            return self.generate_domains_distance_matrix(domains_file_path, actions_file_path)

        elif domains_matrix_file_path is not None:
            return self.read_domains_distance_matrix(domains_matrix_file_path)

    # def get_actions_data(self, actions_file_path, action_matrix_file_path):
    #     # Get Actions Distance Matrix
    #     if actions_file_path is not None:
    #         return self.generate_actions_distance_matrix(actions_file_path)
    #
    #     elif action_matrix_file_path is not None:
    #         return self.read_action_distance_matrix(action_matrix_file_path)

    #helper functions
    @staticmethod
    def split_tag(tag):
        return tag.split('-')

    def get_abbv_index(self, domain_abbv):
        if domain_abbv in self.domains_abbv:
            return np.where(self.domains_abbv == domain_abbv)[0][0]
        else:
            print("can't find this domain", domain_abbv)

    @staticmethod
    def handle_title_str(title_str , content_width):
        output_title = ""
        lines = title_str.split(Utils.newline)
        for line in lines:
            output_title+= Utils.pad_with_spaces(line, content_width) + Utils.newline
        return output_title

    @staticmethod
    def add_title_to_debug_string(debug_string, titles, padding):

        dstring_rows = debug_string.split(Utils.newline)[:-padding]
        new_rows = []
        title_index = 0
        content_width = len(dstring_rows[0])
        title_row = TagDistanceCalculator.handle_title_str(titles[title_index], content_width)
        new_rows.append(Utils.create_char_line(" ", content_width))  # add separator
        new_rows.append(title_row)
        new_rows.append(Utils.create_char_line("-", content_width))
        title_index +=1
        i = 0
        while i < len(dstring_rows):
            row_string = dstring_rows[i]
            spaces_count = row_string.count(" ")
            if spaces_count == len(row_string):
                new_rows.append(Utils.create_char_line(" ",content_width))  # add separator
                new_rows.append(Utils.create_char_line("=",content_width))  # add separator
                new_rows.append(Utils.create_char_line("/",content_width))  # add separator
                new_rows.append(Utils.create_char_line("=",content_width))  # add separator
                for dummy in range(padding-1):
                    new_rows.append(row_string+Utils.newline)
                    i += 1
                title_row = TagDistanceCalculator.handle_title_str(titles[title_index],spaces_count)
                new_rows.append(title_row)
                new_rows.append(Utils.create_char_line("-" , content_width))
                title_index += 1
            else:
                new_rows.append(row_string+Utils.newline)
            i += 1
        return Utils.merge_strings_vertically(new_rows,padding=0)

    # getters
    def get_domains_abbv(self):
        return self.domains_abbv

    # distance calculations
    def domain2domain_distance(self, domain1, domain2 , debug =False):
        index1 = self.get_abbv_index(domain1)
        index2 = self.get_abbv_index(domain2)
        distance = self.domains_distance_matrix[index1, index2]
        if debug:
            debug_info = self.ddb.calc_distance(domain1, domain2, debug=True)
            return distance, debug_info
        else:
            return distance, " "

    def tag2tag_distance(self, tag1, tag2 , debug=False):
        tag1_parts = self.split_tag(tag1)
        tag2_parts = self.split_tag(tag2)
        distances = []
        debug_info_list = []
        for part1 in tag1_parts:
            part1_index = self.get_abbv_index(part1)
            for part2 in tag2_parts:
                part2_index = self.get_abbv_index(part2)
                if self.domains_weight[part1_index] == 1 and self.domains_weight[part2_index] == 1:
                    distance, debug_info = self.domain2domain_distance(part1, part2, debug)
                    distances.append(distance)
                    debug_info_list.append(debug_info)
                else:
                    debug_info = part1 + "->" + part2 + Utils.newline \
                                 + "not Considered"+Utils.newline
                    debug_info_list.append(debug_info)
            # tag_debug_info = Utils.merge_strings_horiz(debug_info_list)
            Utils.unify_lines_count(debug_info_list)
        return np.average(distances) , debug_info_list

    def multi_tag_distance(self, tag_list1, tag_list2, debug=False):
        distances = []
        debug_info_list = []
        titles = []
        for tag1 in tag_list1:
            for tag2 in tag_list2:
                distance, tag_debug_info = self.tag2tag_distance(tag1, tag2, debug)
                distances.append(distance)
                debug_info_list.append(tag_debug_info)
                titles.append(tag1 +" <-> "+ tag2 +Utils.newline +"Average Path Lenght:" +str(distance) )
        debug_info_list = np.array(debug_info_list)
        if debug:
            cols_strings = []
            for col_list in debug_info_list.T:
                col_string = Utils.merge_strings_vertically(col_list)
                cols_strings.append(col_string)
            skill_debug_string = Utils.merge_strings_horiz(cols_strings)
            skill_debug_string = self.add_title_to_debug_string(skill_debug_string , titles,2)
        else:
            skill_debug_string = " "
        return np.min(distances), skill_debug_string

# print("starting Program")
# tdc = TagDistanceCalculator(domains_file_path="domains.csv" , actions_file_path="actions.csv")
# skill1_tags = ["*-NPROT"]
# skill2_tags = ["*-NSEC", "SECU-BKEND"]
# # dist, debug_info = tdc.tag2tag_distance("TEST-SQL" , "DEV-SQL" , debug=True)
# dist , debug_info = tdc.multi_tag_distance(skill1_tags ,skill2_tags , debug=True)
# Utils.write_str_to_file(debug_info ,"debug-info.txt")
# print(dist)
# print(debug_info)
# print("DEV" in tdc.domains_abbv)
# tdc.read_domain_distance_matrix("domain_distance_matrix.csv")