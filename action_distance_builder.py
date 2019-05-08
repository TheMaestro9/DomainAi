import numpy as np
import pandas as pd
import csv


class ActionDistanceBuilder:

    def __init__(self , actions_file_path):
        """
        Initializes all data needed to build distance matrix
        :param actions_file_path: path to csv file containing actions data
        """
        all_action_df = pd.read_csv(actions_file_path, delimiter=",", header=0)
        self.actions_name = all_action_df['Action'].values
        self.actions_abbv = all_action_df['Abbreviation'].values
        self.weights = (all_action_df['Weight'].values).astype('int')
        # remove spaces and new lines form this part of the df
        self.actions_relations = all_action_df[['Excellent', "Very Good", 'Good', "Accepted", 'Week']]\
            .replace("[\n\r ]" , '', regex=True).values
        self.actions_count = self.actions_name.size

    @staticmethod
    def split_relations(relations):
        return relations.split('/')

    def get_action_index(self, action_abbv):
        return np.where(self.actions_abbv == action_abbv)[0][0]

    def build_distance_matrix(self):
        """
        function that builds the distance matrix between the actions
        where matrix[i,j] contains the distance between action[i] and action[j]
        :return: numpy array Distance matrix
        """
        # initialize distance matrix with 100
        distance_matrix = np.ones((self.actions_count, self.actions_count)) * 100
        step = 20
        distance = step

        for relation_col in self.actions_relations.T:
            for index , relations_str in enumerate(relation_col):
                if relations_str == '-':
                    continue
                relations = self.split_relations(relations_str)
                for relation in relations:
                    if relation in self.actions_abbv:
                        relation_index = self.get_action_index(relation)
                        distance_matrix[index][relation_index] = distance
                    else:
                        print('issue in action named' , self.actions_name[index] , 'cant find', relation)

            distance += step
        return distance_matrix

    def extract_distance_matrix(self, output_file):
        """
        function to write action distances data to a file
        :param output_file: path of the output file to which the action distance data will be written
        :return: nothing
        """
        distance_matrix = self.build_distance_matrix()
        with open(output_file, 'w', newline="") as file:
            writter = csv.writer(file)
            writter.writerow(self.actions_abbv)
            writter.writerow(self.weights)
            for row in distance_matrix:
                writter.writerow(row)
        print("finihsied writing data to", output_file)

    # Getters
    def get_actions_abbv(self):
        return self.actions_abbv

    def get_actions_weights(self):
        return self.weights

    # testing function
    def get_distance(self, distance_matrix, first_action , second_action):
        """
        function that gets the distance between two actions given their abbreviations
        :param distance_matrix: matrix containing the distances between actions (numpy array)
        :param first_action: abbreviation of the first action
        :param second_action: abbreviation of the second action
        :return: float representing the distance between the two actions
        """
        first_index = self.get_action_index(first_action)
        second_index = self.get_action_index(second_action)
        return distance_matrix[first_index, second_index]


