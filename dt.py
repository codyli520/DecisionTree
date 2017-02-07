"""
Author: Longfei Li
Class: INF552
Program: Decision Tree
"""
from sys import argv
from collections import OrderedDict
import math
import Queue

# _ , filename = argv

data = open("dt-data.txt")

#get all attribute names
attr_name = data.readline().strip().strip("()").replace(" ","").split(",")

#get all data entries
data_val = []
for line in data:
	line = line.strip()
	if line != "":
		line = line.translate(None, '0123456789:;').replace(" ","").split(",")
		data_val.append(line)

#get all attribute values
attr_val = {}
for i in range(len(attr_name)):
	if not attr_name[i] in attr_val:
		val = []
		for j in range(len(data_val)):
			if data_val[j][i] not in val:
				val.append(data_val[j][i])

		attr_val[attr_name[i]] = val

#reorder some of the attribute values to follow homework instruction
for k in attr_val:
	if k == 'Enjoy' or k == 'FavoriteBeer' or k == 'VIP':
		attr_val[k] = attr_val[k][::-1]
	elif k == 'Location':
		attr_val[k][2],attr_val[k][4] = attr_val[k][4],attr_val[k][2]

#hash the attributes to its index
attr_index = {}
for i in range(len(attr_name)):
		attr_index[attr_name[i]] = i

class Node(object):
	def __init__(self,name):
		'''
		Node class to build a tree-like structure
		'''
		if name != '':
			self.name = name
			self.child = OrderedDict()
			for i in attr_val[name]:
				self.child[i] = Node('')

def entropy(data):
	'''
	Calculates the entropy
	'''
	index = attr_name.index("Enjoy")

	yes,no = 0,0
	for row in data:
		if row[index]=="Yes":
			yes+=1
		elif row[index]=="No":
			no+=1

	p1 = 0.0 if yes == 0 else yes/float(len(data))
	p2 = 0.0 if no == 0 else no/float(len(data))

	entropy =  - (0 if p1 == 0.0 else p1 * math.log(p1, 2)) - (0 if p2 == 0.0 else p2 * math.log(p2, 2))

 	return entropy

def avg_entropy(attr,data):
	'''
	Calculates average entropy
	'''
	values = {i:{'yes':0,'no':0} for i in attr_val[attr]}
	index = attr_name.index(attr)
	e_index = attr_name.index("Enjoy")

	
	for row in data:
		v = row[index]
		if row[e_index] == "Yes":
			values[v]['yes'] +=1
		else:
			values[v]['no'] +=1
	
	gain = 0.0

	for i in values:
		new_data = []
		for row in data:
			if row[index] == i:
				new_data.append(row)
		e = entropy(new_data)
		p = 0 if (values[i]['yes']+values[i]['no']) == 0 else (values[i]['yes']+values[i]['no'])/float(len(data))
		gain += e*p

	return gain

def info_gain(attr_list,data):
	'''
	Calculates information gain then picks the max
	'''
	if len(attr_list) == 1:
		return attr_list[0]
	else:
		a = attr_list[0]
		e = entropy(data)
		gain = e - avg_entropy(attr_list[0],data)

		for i in attr_list:
			v = e - avg_entropy(i,data)

			if i == 'Enjoy':
				pass
			elif v > gain:
				gain = v
				a = i
		return a

def conclude(data):
	'''
	Checks if we can have a conclusion on the decision for the attribute
	'''
	if len(data) == 1 or len(data) == 0:
		return True
	enjoyed = data[0][attr_index['Enjoy']]
	for row in data:
		if enjoyed != row[attr_index['Enjoy']]:
			return False
	return True

def build_tree(attr_list, node, data):
	'''
	Recursively builting the Decision tree
	'''
	if len(attr_list) == 1 or conclude(data):
		node.name = 'Enjoy'
		node.result = data[0][attr_index['Enjoy']]
		node.childNodes = {}
		return
	child_attr_list = []
	for i in attr_name:
		if i != node.name:
			child_attr_list.append(i)

	for v in node.child:
		child_data_set = []
		for row in data:
			if row[attr_index[node.name]] == v:
				child_data_set.append(row)

		if not conclude(child_data_set):
			new_attr = info_gain(child_attr_list,child_data_set)
			node.child[v] = Node(new_attr)

		
		if len(child_data_set) == 0:
			new_attr = 'Enjoy'
			node.child[v] = Node(new_attr)
			node.child[v].result = 'Tie'
			continue

		build_tree(child_attr_list,node.child[v],child_data_set)


def print_node(node, level = 0):
	'''
	Print nodes
	'''
	level+=1
	for i in node.child:
		if hasattr(node.child[i], 'name'):
			print "----"*level+ "[" +i + "]->" + node.child[i].name,
			if hasattr(node.child[i], 'result'):
				print "("+node.child[i].result+")"
			else:
				print "\n"
		if hasattr(node.child[i], 'child'):
			print_node(node.child[i],level)

def print_node_BFS(node):
	'''
	Print nodes by level, result is tree-like
	'''
	Q = Queue.Queue()
	Q.put(node)
	while not Q.empty():
		cur = Q.get()
		if isinstance(cur, basestring):
			print cur,
			continue
		subtree= []
		to_print = []
		if isinstance(cur, list):
			for i in cur:
				if hasattr(i, 'name'):
					if i.name == 'Enjoy':
						subtree.append(i.result)
					else:
						to_print.append(i.name)
						for j in i.child:
							if hasattr(i.child[j], 'name'):
								if i.child[j].name == 'Enjoy':
									subtree.append(i.child[j].result)
								else:
									subtree.append(i.child[j])
				else:
					to_print.append(i)
		if len(to_print) > 0:
			print ",".join(to_print),


		if hasattr(cur, 'name'):
			print cur.name,
			for i in cur.child:
				if hasattr(cur.child[i], 'name'):
					if cur.child[i].name == 'Enjoy':
						subtree.append(cur.child[i].result)
					else:
						subtree.append(cur.child[i])

		Q.put("\n")
		if len(subtree) > 0:
			Q.put(subtree)

def predict(node,data):
	'''
	Predicts the result using Decision tree
	'''
	if node.name == 'Enjoy':
		return node.result
	else:
		node = node.child[data[attr_index[node.name]]]
		return predict(node,data)

if __name__ == "__main__":
	root = Node(info_gain(attr_name,data_val))

	build_tree(attr_name, root, data_val)

	#print_node(root)
	
	print_node_BFS(root)

	#print "\nMy prediction is: "+ predict(root, [ 'Large','Moderate','Cheap','Loud','City-Center','No','No'])
	
		












