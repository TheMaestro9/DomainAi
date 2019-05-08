import numpy as np
import pandas as pd
import networkx as nx
import pickle
import csv
from Utils import Utils
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans

class DomainDistanceBuilder:
    # static variables
    NO_CONNECTION_DISTANCE = 15

    def __init__(self , domains_file_path, actions_file_path):
        """
        Extract domains data form file and do some preprocessing and construct the domain forest
        :param domains_file_path: path for the csv file containing the domains data
        """
        # initialize class variables

        # Extract Domains Data and remove all extra spaces
        all_domain_df = pd.read_csv(domains_file_path, delimiter=",", header=0)
        self.domains_names = all_domain_df.Domain.values
        self.domains_abbv = all_domain_df["Abbreviation"].replace(" ","" ,regex=True ).values
        self.domains_children = all_domain_df['Children'].replace(" ","" , regex=True).values
        self.domains_parents = all_domain_df['Parents'].replace(" ","", regex=True).values
        self.domains_comps= all_domain_df['Comp Domains'].replace(" ","",regex=True).values
        self.domains_count = self.domains_abbv.size
        self.domains_graph = nx.DiGraph()

        # Extract Actions Data and remove extra spaces and new lines
        all_action_df = pd.read_csv(actions_file_path, delimiter=",", header=0)
        self.actions_name = all_action_df['Action'].values
        self.actions_abbv = all_action_df['Abbreviation'].replace(" " , "").values  #remove spaces
        self.actions_weight = (all_action_df['Weight'].values).astype('int')
        self.actions_relations = all_action_df[['Excellent', "Very Good", 'Good', "Accepted", 'Week']] \
            .replace("[\n\r ]", '', regex=True).values  # remove spaces and new lines
        self.actions_count = self.actions_name.size

        self.domains_weight = np.concatenate((np.ones(self.domains_count-self.actions_count),self.actions_weight))

        # Do the mandatory functionality
        self.preprocess_data()
        self.construct_domain_forest()

    # Helper Functions

    # Domain helper functions
    @staticmethod
    def split_comps(comps_str):
        return comps_str.split("/")

    @staticmethod
    def split_children(children_str):
        return children_str.split('/')

    @staticmethod
    def split_comp_weight(comp_weight):
        return comp_weight.split('-')

    def get_abbv_index(self, domain_abbv):
        return np.where(self.domains_abbv == domain_abbv)[0][0]

    def get_abbv_children(self, domain_abbv):
        domain_index = np.where(self.domains_abbv == domain_abbv)[0][0]
        domain_children_str = self.domains_children[domain_index]
        if domain_children_str == "-":
            return []
        else:
            return self.split_children(domain_children_str)

    # Actions Helper functions
    @staticmethod
    def split_relations(relations):
        return relations.split('/')

    def get_action_index(self, action_abbv):
        return np.where(self.actions_abbv == action_abbv)[0][0]

    # Preporcessing Functions
    def add_weight_to_comps(self ,comps_list , weight):
        new_comps = np.copy(np.array(comps_list,dtype=object))
        for i, comp in enumerate(comps_list):
            new_comps[i] = comp + "-" + weight
        return new_comps.tolist()

    def remove_weight_from_comps(self,comps_list ):
        comps_without_weights = np.copy(np.array(comps_list,dtype=object))
        for i, comp in enumerate(comps_without_weights):
            comps_without_weights[i] = self.split_comp_weight(comp)[0] #take the complemetary domain only and ignore the weight
        return comps_without_weights.tolist()

    def merge_comps(self, domain_index, new_comps):
        orig_comps_str = self.domains_comps[domain_index]
        if orig_comps_str == "-":
            orig_comps = []
        else:
            orig_comps = self.split_comps(orig_comps_str)
        orig_comps_no_weight = self.remove_weight_from_comps(orig_comps)
        merged_comps = [new_comp for new_comp in new_comps if self.split_comp_weight(new_comp)[0] not in orig_comps_no_weight]
        merged_comps = orig_comps + merged_comps
        merged_comps_str = ""
        for comp in merged_comps:
            merged_comps_str += comp+"/"
        merged_comps_str = merged_comps_str[:-1]  # remove the last '/'
        self.domains_comps[domain_index] = merged_comps_str

    def expand_comp(self):
        # iterate over all the domains
        for index , comps_str in enumerate(self.domains_comps):
            # if no complementary domain for this domain continue
            if comps_str == "-":
                continue

            comps = self.split_comps(comps_str)
            # for each of this domain complementary domains
            for comp_weight in comps:
                new_comps = []
                comp_weight_list = self.split_comp_weight(comp_weight)
                comp = comp_weight_list[0]
                weight = comp_weight_list[1]
                if comp not in self.domains_abbv:
                    print("issue in domain named:" , self.domains_names[index])
                else:
                    new_comps = self.get_abbv_children(comp)
                    new_comps = self.add_weight_to_comps(new_comps , weight)
                # add complementary domain children as complementary to this domain
                if len(new_comps) != 0:
                    self.merge_comps(index,new_comps)
                new_comps.append(comp_weight)
                domain_children_str = self.domains_children[index]
                if domain_children_str != "-":
                    domain_children = self.split_children(domain_children_str)
                    for child in domain_children:
                        if child in self.domains_abbv:
                            child_index = self.get_abbv_index(child)
                            self.merge_comps(child_index, new_comps)
                        else:
                            print("issue in children of the domain named", self.domains_names[index] , "can't find child", child)

    # def remove_spaces(self):
    #     self.domains_children = np.array([children.replace(" ", "") for children in self.domains_children], dtype=object)
    #     self.domains_parents = np.array([parents.replace(" ", "") for parents in self.domains_parents], dtype=object)
    #     self.domains_abbv = np.array([abbv.replace(" ", "") for abbv in self.domains_abbv], dtype=object)
    #     self.domains_comps = np.array([prim_comp.replace(" ", "") for prim_comp in self.domains_comps], dtype=object)
    #     # self.domains_sec_comp = np.array([sec_comp.replace(" ", "") for sec_comp in self.domains_sec_comp],dtype=object)

    def preprocess_data(self):
        self.expand_comp()

    # Graph operations
    def add_nodes(self):
        for index, domain_abbv in enumerate(self.domains_abbv):
            # add node to the graph
            self.domains_graph.add_node(domain_abbv, name=self.domains_names[index])

    def add_endge(self, node1, node2, type, weight1, weight2=None):
        if weight2 is None:
            weight2 = weight1
        self.domains_graph.add_edge(node1, node2, weight1, type=type)
        self.domains_graph.add_edge(node2, node1, weight2, type=type)

    def add_parent_child_edges(self):

        for index, domain_abbv in enumerate(self.domains_abbv):
            parents_str = self.domains_parents[index]
            # if no parents do nothing
            if parents_str != "-":
                parents = parents_str.split('/')
                # add edge for each parent
                for parent in parents:
                    if parent in self.domains_abbv:
                        self.add_endge(domain_abbv, parent,type="Parent", weight1=1)
                        # self.domains_graph.add_edge(domain_abbv, parent, weight=1, type="Parent")
                    else:
                        print("issue Parents of domain Nubmer:", index, "Named", self.domains_names[index])

    def add_complementary_edges(self):

        for index, domain_abbv in enumerate(self.domains_abbv):
            comps_str = self.domains_comps[index]
            # if no complementary domains do nothing
            if comps_str != "-":
                comps = comps_str.split('/')
                # add edge for each parent
                for comp_weight in comps:
                    comp_weight_list = self.split_comp_weight(comp_weight)
                    comp = comp_weight_list[0]
                    weight = int(comp_weight_list[1])
                    if comp in self.domains_abbv:
                        self.add_endge(domain_abbv,comp,type="Comp", weight1=weight)
                        # self.domains_graph.add_edge(domain_abbv, comp , weight=weight , type="Comp")
                    else:
                        print("issue while adding Complementary edge wighted:", weight," of domain number:", index, "named:", self.domains_names[index])

    def add_action_edges(self):

        weights = [1, 2, 3, 4,5]  # [ Excellent, Very Good, Good, Acceptable, week]
        weights_index = 0
        for relation_col in self.actions_relations.T:
            for index, relations_str in enumerate(relation_col):
                self.domains_graph[self.actions_abbv[index]]["ACTION"]["weight"] = self.NO_CONNECTION_DISTANCE
                if relations_str == '-':
                    continue
                relations = self.split_relations(relations_str)
                for relation in relations:
                    if relation in self.actions_abbv:
                        self.add_endge(relation, self.actions_abbv[index], type="Action", weight1=weights[weights_index])
                        # self.domains_graph.add_edge(relation,self.actions_abbv[index], weight=weights[weights_index], type="Action")
                    else:
                        print('issue in action named', self.actions_name[index], 'cant find', relation)

            weights_index += 1


    def construct_domain_forest(self):
        self.add_nodes()
        self.add_parent_child_edges()
        self.add_complementary_edges()
        self.add_action_edges()
        # self.add_complementary_edges(self.domains_sec_comp , 2)

    def calc_distance(self , first_domain, second_domain, debug=False):
        if debug:
            # print("Path Length" , nx.dijkstra_path_length(self.domains_graph,first_domain , second_domain))

            nodes =  nx.dijkstra_path(self.domains_graph,first_domain , second_domain)
            debug_info = "distance of " + first_domain + "->" + second_domain + Utils.newline
            debug_info += "Path Length: " + str(nx.dijkstra_path_length(self.domains_graph,first_domain , second_domain))+ Utils.newline
            for i , node in enumerate(nodes[:-1]):
                debug_info +=  node + "->" + nodes[i+1]  + str(self.domains_graph[node][nodes[i+1]]) + Utils.newline
            return debug_info
        else:
            return nx.dijkstra_path_length( self.domains_graph,first_domain , second_domain)

    def build_distance_matrix(self):
        domains_distaces =np.zeros((self.domains_count, self.domains_count))
        for i, first_domain in enumerate(self.domains_abbv):
            for j, second_domain in enumerate(self.domains_abbv):
                try:
                    domains_distaces[i,j] = self.calc_distance(first_domain ,  second_domain)
                except nx.NetworkXNoPath:
                    domains_distaces[i,j] = self.NO_CONNECTION_DISTANCE
        return domains_distaces

    def extract_distance_matrix(self ,output_file):
        distance_matrix = self.build_distance_matrix()
        with open(output_file,'w',newline="") as file:
            writter =csv.writer(file)
            writter.writerow(self.domains_abbv)
            writter.writerow(self.domains_weight)
            for row in distance_matrix:
                writter.writerow(row)
        print("finihsied writing data to" , output_file)
        # pickle.dump(distance_matrix,output_file)

    # Getters
    def get_domains_abbv(self):
        return self.domains_abbv

    def get_domains_weights(self):
        return self.domains_weight

    # Testing Functions
    def get_comp_of_abbv(self , abbv):
        if(abbv in self.domains_abbv):
            domain_index = np.where(self.domains_abbv == abbv)[0][0]
            return self.domains_comp[domain_index]
        else:
            print("domain Abbriviation:'%s' doesn't exist!" % abbv)

    def get_abbv_adj(self , abbv):
        if(abbv in self.domains_abbv):
            return self.domains_graph.adj[abbv]
        else:
            print("error Wrong abbriviation")
            return ""

def investigate():
    ddb = DomainDistanceBuilder("domains.csv","actions.csv")
    distance_matrix = ddb.build_distance_matrix()
    # kmeans = KMeans(n_clusters=5).fit(distance_matrix.flatten().reshape(-1,1))
    # print(kmeans.cluster_centers_)

    distances,counts  = np.unique(distance_matrix.flatten() , return_counts=True)
    # distances = np.sort(distances)
    print(distances)
    plt.plot(distances , counts)
    plt.show()
    # # unique_dists = np.unique(distances)
    # print(np.sort(distances)[-1])

# investigate()
# ddb = DomainDistanceBuilder("domains.csv","actions.csv")
# print(ddb.get_abbv_adj("SECU"))
# print("before")
# print(ddb.calc_distance("MOBOS", "SQL", debug=True))
# print("after")
# print(ddb.domains_distaces.shape)
# ddb.extract_distance_matrix("domains_distance_matrix.csv")
# print(ddb.get_comp_of_abbv("SQL"))

#
# print(G.nodes['HARD']['name'])
# print(G.adj['OS'])
# print(nx.shortest_path(G, "GAME" , "IMG"))


