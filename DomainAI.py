import numpy as np
import pandas as pd
import numpy.core.defchararray as np_f


# creates domain graph from domain child realtionship list
def create_domian_graph(domains_abbv, domains_children):
    domain_count = domains_abbv.size
    domain_graph = np.zeros((domain_count, domain_count), dtype=np.int8)
    for domain_index, children_str in enumerate(domains_children):
        children = children_str.split("/")
        children_indecies = []
        for child in children:
            if child != '-':
                if child in domains_abbv:
                    children_indecies.append(np.where(domains_abbv == child)[0][0])
                else:
                    print("issue in domain number", domain_index)
        children_indecies = np.array(children_indecies, dtype='int')
        domain_graph[domain_index, children_indecies] = 1

    return domain_graph

def get_parents( domain_abbv , domain_graph , domains_abbv):
    if domain_abbv in domains_abbv:
        domain_index = np.where(domains_abbv == domain_abbv)[0][0]
        domain_parents_relations = domain_graph[: , domain_index]
        parents_indecies = np.where(domain_parents_relations == 1)[0]
        return parents_indecies
    else :
        return -1


def get_children( domain_abbv , domain_graph , domains_abbv):
    if domain_abbv in domains_abbv:
        domain_index = np.where(domains_abbv == domain_abbv)[0][0]
        domain_children_relations = domain_graph[domain_index , :]
        children_indecies = np.where(domain_children_relations == 1)[0]
        return children_indecies
    else :
        return -1

###########################
# data extraction
##########################

all_domain_df = pd.read_csv("Domains.csv" , delimiter="," , header=0)
domains_names = all_domain_df.Domain.values
domains_abbv = all_domain_df.Abbreviation.values
domains_children = all_domain_df.Children.values
domains_parents = all_domain_df.Parents.values

###########################
# data preprocessing
##########################

# remove extra spaces
domains_children = np.array([children.replace(" ", "") for children in domains_children])
domains_Parents = np.array([parents.replace(" ", "") for parents in domains_parents])
domains_abbv = np.array([abbv.replace(" ", "") for abbv in domains_abbv])


# index = 9
# print(domains_children[index])
# print(np.where(domains_abbv == domains_children[index].split('/')[0]))

domain_graph = create_domian_graph(domains_abbv , domains_children)

# print(domain_graph)

print(domains_names[get_parents("NINF" , domain_graph , domains_abbv)])
print(domains_names[get_children("NET" , domain_graph , domains_abbv)])