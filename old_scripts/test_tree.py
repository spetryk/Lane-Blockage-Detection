from treelib import Node, Tree
from classes import *

tree = Tree()

intersection = Intersection(name='Test_intersection',externalID=1000, cycleTime=90)
approach = Approach(name='Test_approach', section=1) 
det1 = Detector('Det1', externalID=100001, category='Advanced', movements=['Left'], length=30, satVelocity=20)

tree.add_node(intersection)
tree.show()
print(tree.all_nodes())

approach.bpointer = intersection.externalID # could also do intersection.identifier (but try to avoid using treelib's field names)
tree.add_node(approach, intersection.externalID)
tree.show()

print(tree.root)
tree.root = intersection.identifier
print(tree.root)
tree.show()

tree.add_node(det1, approach.identifier)
#approach.update_fpointer(det1.identifier, mode=Node.ADD)
tree.show()

print(tree.children(approach.identifier))


