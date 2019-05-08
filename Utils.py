import numpy as np
import math


class Utils:
    newline = "\r\n"
    # def __init__(self):
    @staticmethod
    def get_max_len(string_list):
        """
        Calculates the length of the largest string in an array
        :param string_list: list of strings
        :return: int, the maximum length
        """
        maxlen = 0
        for string in string_list:
            length = len(string)
            if length > maxlen:
                maxlen = length
        return maxlen

    @staticmethod
    def merge_strings_horiz(strings_list, padding=2):
        """
        merge two strings horizontally putting each string in table column and stacking columns
        :param strings_list: list of strings to be merges
        :param padding: number of spaces on the left and right between columns
        :return: str, merged string
        """
        output_str = ""
        max_lengths = []
        all_strings_parts = []
        max_parts_count = 0
        for input_string in strings_list:
            string_parts = input_string.split(Utils.newline)
            if len(string_parts) > max_parts_count:
                max_parts_count = len(string_parts)
            all_strings_parts.append(string_parts)
            maxlen = Utils.get_max_len(string_parts)
            max_lengths.append(maxlen)

        for i, string_parts in enumerate(all_strings_parts):
            parts_count = len(string_parts)
            for dummy in range(max_parts_count - parts_count):
                all_strings_parts[i].append(" ")

        all_strings_parts = np.array(all_strings_parts)
        for row_strings in all_strings_parts.T:
            for i, col_string in enumerate(row_strings):
                output_str+= Utils.pad_with_spaces(col_string , max_lengths[i]+2*padding)
            output_str += Utils.newline
        return output_str

    @staticmethod
    def merge_strings_vertically(string_list, padding=2):
        output_string = ""
        for i, string in enumerate(string_list):
            output_string += string
            if len(string_list)-i > 1:
                output_string+= Utils.newline * padding
        return output_string

    @staticmethod
    def pad_with_spaces(string , cell_width):
        left_padding = math.ceil((cell_width - len(string)) / 2)
        right_padding = math.floor((cell_width - len(string)) / 2)
        return " " * left_padding + string + right_padding * " "

    @staticmethod
    def create_char_line(char, width):
        return char * width + Utils.newline
    @staticmethod
    def unify_lines_count(strings_list):
        max_parts_count = 0
        for i, string in enumerate(strings_list):
            parts = string.split(Utils.newline)
            if len(parts) > max_parts_count:
                max_parts_count = len(parts)

        for i , string in enumerate(strings_list):
            parts = string.split(Utils.newline)
            parts_count = len(parts)
            for dummy in range(max_parts_count-parts_count):
                strings_list[i] += " " + Utils.newline

    @staticmethod
    def in_range(value, range_start, range_end):
        return value > range_start and value < range_end

    @staticmethod
    def is_range_intersect(range1, range2):
        range1_start, range1_end = range1
        range2_start, range2_end = range2
        return Utils.in_range(range1_start, range2_start, range2_end) or Utils.in_range(range1_end, range2_start, range2_end)

    @staticmethod
    def write_str_to_file(string, file_name):
        with open(file_name, "w") as text_file:
            text_file.write(string)
# Testing the merging Function
# str1 = "hello" + Utils.newline +"my friend where are you" + Utils.newline + "fun"
# str2 = "hello" + Utils.newline +"my friend where are you" + Utils.newline + "ahlan man"
# input_strings = [str1 , str2]
# print(Utils.merge_strings_horiz(input_strings))