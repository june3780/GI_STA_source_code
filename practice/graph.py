import json
import copy
from uuid import getnode
import pandas as pd
from traitlets import directional_link
import networkx as nx
import matplotlib.pyplot as plt
from networkx.algorithms import tournament
from networkx.drawing.nx_agraph import graphviz_layout, to_agraph
import pygraphviz as pgv



if __name__ == "__main__":
    
    DG = nx.DiGraph()

    DG.add_edge('apple','banana', weight=1)
    DG.add_edge('apple','amango', weight=2)
    DG.add_edge('amango','grape', weight=1)
    DG.add_edge('grape','eeedddxxx',weight=4)
    DG.add_edge('ggoo','eeedddxxx',weight=22)
    DG.nodes['amango']['fruit']=1

    start_nodes=['apple','ggoo']


##    print(nx.algorithms.descendants(DG,'apple')) #### 노드로부터 나가는 방향에 있는 모든 노드들
##    print(nx.algorithms.ancestors(DG,'eeedddxxx')) #### 노드로부터 들어오는 방향에 있는 모든 노드들


    ##print(tournament.is_reachable(DG,'apple',5))


    A= to_agraph(DG)
    A.layout('dot')
    A.draw('abcd.png')

    print(DG.edges('amango'))
'''
    for tdx in range(len(DG.degree())):
        if (DG.degree())[tdx][0]=='apple':
            print('june3780')
'''
    ##print(list(DG.in_edges('eeedddxxx'))[1][0])
    ##print(len(DG.out_edges('apple')))
    
    
nx.draw(DG,with_labels=True)
plt.show()

