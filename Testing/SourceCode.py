
import sys
import math
import time

B = 4

def main():
    points = [] #List store data points
    n=0 #Count number of points
                    
    with open("DatasetRTree.txt", 'r') as dataset: #https://www.w3schools.com/python/ref_file_readlines.asp
        for data in dataset.readlines():
            data = data.split() #split text to list #https://www.w3schools.com/python/ref_string_split.asp
            points.append({ #https://www.w3schools.com/python/ref_list_append.asp
                'id': int(data[0]), #store item in index 0 to dict object 'id'
                'x': int(data[1]), #store item in index 1 to dict object 'x'
                'y': int(data[2]) #store item in index 2 to dict object 'y'
                   })
            
        #https://stackoverflow.com/questions/17153779/how-can-i-print-variable-and-string-on-same-line-in-python
            n=n+1

    queries=[] #List store query range - rectangle range
    with open("100Queries.txt", 'r') as dataset1:
        for data in dataset1.readlines():
            data=data.split() #split text to list
            queries.append({
                'x1': int(data[0]), #store item in index 0 to dict object 'x1'
                'x2': int(data[1]), #store item in index 1 to dict object 'x2'
                'y1': int(data[2]), #store item in index 2 to dict object 'y1'
                'y2': int(data[3]) #store item in index 3 to dict object 'y2'
            })
    count=[]
    
    def Sequential(p,q): #sequential query
        index=0 #Check index number of data points
        for i in q: #Loop through the queries
            c=0 #count number of data points in the query range
            for j in p: #Loop through the points
                if (j['x'] >= i['x1'] and j['x'] <= i['x2'] and j['y'] >= i['y1'] and j['y'] <= i['y2']): #Check if x, y lie between the query range (x1, x2) and (y1, y2)
                    c=c+1 #If point occur in query range, c increase by 1
                index=index+1
                if (index==(len(p)-1)): #If it reach the last point in dataset, then add the number of data points to the list 'count'. Set the index back to 0, to keep checking the next query.
                    count.append(c)
                    index=0
    seq_time_start=time.time() #Time of starting finding data points in total queries using Sequential
    Sequential(points,queries)
    seq_time_end=time.time() #Time of completing finding data points in total queries using Sequential
    seq_time=seq_time_end-seq_time_start

    print("Total time for Sequential queries", seq_time, "seconds.\n")
    print("Average time for every Sequential query", seq_time/100, "seconds.\n")
    # Call RTree() class to build R-Tree model
    rtree = RTree()

    print("Building the R-Tree: Please wait...\n")
    #The time when start building RTree
    R_Tree_start=time.time() #https://www.programiz.com/python-programming/time
 
    for point in points: #insert data points from the root one by one 
        rtree.insert(rtree.root, point)
    #The time when building RTree completed
    R_Tree_end=time.time() #https://www.programiz.com/python-programming/time
    #The length of time to build RTree
    Used_time=R_Tree_end-R_Tree_start
    print("100.0% \n")
    print("The time-cost of building up the R-Tree is",Used_time,"seconds.\n")

    results = [] #List to store number of data points in every query range
    every_q=[] #List to store
    Answer_query_start=time.time() #Time of starting finding data points in total queries
    for query in queries:
        every_query_start=time.time() #The time start finding data points in every query range
        results.append(rtree.query(rtree.root, query))
        every_query_end=time.time() #The time complete finding data points in every query range
        Answer_every=every_query_end-every_query_start #The length of time finding data points within every query range
        every_q.append(Answer_every)
    Answer_query_end=time.time() #Time of completing finding data points in total queries
    Query_processing_time=Answer_query_end-Answer_query_start #Total time for R-Tree queries
    
    sum=0
    for i in every_q:
        sum=sum+i
    avg_time=sum/100 #Average time for finding data points in every query
    
    print("There are", len(every_q),"queries.\n") #Number of queries
    print ("Total time for R-Tree queries",Query_processing_time,"seconds.\n")
    print ("Average time for every R-Tree query",avg_time,"seconds.\n")
    print ("R-Tree is",(seq_time/100)/avg_time,"times faster than Sequential query.")
    

    # Make a text file named 'outputResult.txt' to store number of data points in every query range
    with open("outputResult.txt","w") as f:
        for item in results:
            f.write(str(item)+'\n')

class Node(object): #node class
    def __init__(self):
        self.id = 0
        self.child_nodes = [] #save all the child nodes if it has for internal nodes
        self.data_points = [] #save the data points included in a node, for leaf nodes
        self.parent = None # initial value of parent
        self.MBR = {
            'x1': -1,   #initial value of MBR
            'y1': -1,
            'x2': -1,
            'y2': -1,
        }
    def perimeter(self):
        # only calculate the half perimeter here
        return (self.MBR['x2'] - self.MBR['x1']) + (self.MBR['y2'] - self.MBR['y1'])

    def is_overflow(self):
        if self.is_leaf():
            if self.data_points.__len__() > B: #Checking if the number of data points is overflows (>B, where B is the upper bound)
                return True
            else:
                return False
        else:
            if self.child_nodes.__len__() > B: #Checking if the number of child nodes is overflows (>B, where B is the upper bound)
                return True
            else:
                return False

    def is_root(self):
        if self.parent is None: #If the data point is not a child node (do not have parent node), then it becomes the root
            return True
        else:
            return False

    def is_leaf(self):
        if self.child_nodes.__len__() == 0: #If the data point has no child node, then it become the leaf
            return True
        else:
            return False

class RTree(object): #R tree class
    def __init__(self):
        self.root = Node() #Create a root

    def query(self, node, query): #run to answer the query
        num = 0
        if node.is_leaf(): #check if a data point is included in a leaf node
            for point in node.data_points:
                if self.is_covered(point, query):
                    num = num + 1
                    #print("Point: ", point, "Query: ", query)
            return num
        else:
            for child in node.child_nodes: #If it is an MBR, check all the child nodes to see whether there is an interaction
                if self.is_intersect(child, query): #If there is an interaction, keep continue to check the child nodes in the next layer till the leaf nodes
                    num = num + self.query(child, query)
            return num

    def is_covered(self, point, query):
        x1, x2, y1, y2 = query['x1'], query['x2'], query['y1'], query['y2']
        if x1 <= point['x'] <= x2 and y1 <= point['y'] <= y2:
            return True
        else:
            return False    

    def is_intersect(self, node, query): #https://stackoverflow.com/questions/9734821/how-to-find-the-center-coordinate-of-rectangle
        # if two mbrs are intersected, then:
        # |center1_x - center2_x| <= length1 / 2 + length2 / 2 and:
        # |center1_y - center2_y| <= width1 / 2 + width2 / 2
        center1_x = (node.MBR['x2'] + node.MBR['x1']) / 2 # x coordinate of center point in rectangle MBR
        center1_y = (node.MBR['y2'] + node.MBR['y1']) / 2 # y coordinate of center point in rectangle MBR
        length1 = node.MBR['x2'] - node.MBR['x1'] #Length of rectangle MBR
        width1 = node.MBR['y2'] - node.MBR['y1'] #Width of rectangle MBR
        center2_x = (query['x2'] + query['x1']) / 2 # x coordinate of center point in rectangle query
        center2_y = (query['y2'] + query['y1']) / 2 # y coordinate of center point in rectangle query
        length2 = query['x2'] - query['x1'] #Length of rectangle query
        width2 = query['y2'] - query['y1'] #Width of rectangle query
        if abs(center1_x - center2_x) <= length1 / 2 + length2 / 2 and\
                abs(center1_y - center2_y) <= width1 / 2 + width2 / 2:  #we check the absolute value
            return True
        else:
            return False                    


    def insert(self, u, p): # insert p(data point) to u (MBR)
        if u.is_leaf(): #If u is a leaf node, then
            self.add_data_point(u, p) #add the data point p into the leaf node and update the corresponding MBR
            if u.is_overflow():
                self.handle_overflow(u) #handle overflow for leaf nodes
        else: #If point p is not in any of existing MBRs, need to find 1 to cover the point or extend the closest MBR (with min perimeter) to cover point p
            v = self.choose_subtree(u, p)
            #choose a subtree to insert the point p to miminize sum of perimeter
            self.insert(v, p) #keep continue to check the next layer recursively
            self.update_mbr(v) #update the MBR for inserting the data point

    def choose_subtree(self, u, p): 
        if u.is_leaf(): #find the leaf and insert the data point
            return u
        else:
            min_increase = sys.maxsize #set an initial value, which is the largest value
            best_child = None
            for child in u.child_nodes: #check each child to find the best node to insert the point (find the min value that the perimeter has to increase)
                if min_increase > self.peri_increase(child, p):
                    min_increase = self.peri_increase(child, p)
                    best_child = child
            return best_child

    def peri_increase(self, node, p): # calculate the increase of the perimeter after inserting a new data point p
        # perimeter to new data point - original perimeter = the increase of perimeter (increase)
        origin_mbr = node.MBR #original perimeter
        x1, x2, y1, y2 = origin_mbr['x1'], origin_mbr['x2'], origin_mbr['y1'], origin_mbr['y2']
        increase = (max([x1, x2, p['x']]) - min([x1, x2, p['x']]) +
                    max([y1, y2, p['y']]) - min([y1, y2, p['y']])) - node.perimeter()
        return increase


    def handle_overflow(self, u):
        u1, u2 = self.split(u) #if leaf node is overflow, then use split() to split u into u1 and u2
        # if u is a root, create a new root with u1 and u2 as its' child nodes
        if u.is_root():
            new_root = Node() #create a new root
            self.add_child(new_root, u1) #add u1 add child node
            self.add_child(new_root, u2) #add u2 add child node
            self.root = new_root
            self.update_mbr(new_root)
        # if u is not a root, delete u, and set u1 and u2 as child node of w which is u's parent.
        else:
            w = u.parent #Set w to be u's parent
            w.child_nodes.remove(u) #Delete u
            self.add_child(w, u1) #add u1 and u2 as child nodes of w and update the corresponding MBR
            self.add_child(w, u2)
            if w.is_overflow(): #check the parent node recursively
                self.handle_overflow(w) #if parent node is overflow, then repeat the previous steps
            
    def split(self, u):
        # split u into s1 and s2
        best_s1 = Node()
        best_s2 = Node()
        best_perimeter = sys.maxsize
        if u.is_leaf(): #If u is a leaf node
            m = u.data_points.__len__() #Number of points in u
            # create two different kinds of divides
            divides = [sorted(u.data_points, key=lambda data_point: data_point['x']),
                       sorted(u.data_points, key=lambda data_point: data_point['y'])] #sorting the points based on X dimension and Y dimension
            for divide in divides:
                for i in range(math.ceil(0.4 * B), m - math.ceil(0.4 * B) + 1): #check the combinations to find a near-optimal one
                    s1 = Node()
                    s1.data_points = divide[0: i]
                    self.update_mbr(s1)
                    s2 = Node()
                    s2.data_points = divide[i: divide.__len__()]
                    self.update_mbr(s2) #Sorting based on minimizing the sum of perimeter
                    if best_perimeter > s1.perimeter() + s2.perimeter(): 
                        best_perimeter = s1.perimeter() + s2.perimeter()
                        best_s1 = s1
                        best_s2 = s2

        # u is an internal node
        else:
            # create four different kinds of divides
            m = u.child_nodes.__len__()
            divides = [sorted(u.child_nodes, key=lambda child_node: child_node.MBR['x1']), #sorting based on MBRs
                       sorted(u.child_nodes, key=lambda child_node: child_node.MBR['x2']),
                       sorted(u.child_nodes, key=lambda child_node: child_node.MBR['y1']),
                       sorted(u.child_nodes, key=lambda child_node: child_node.MBR['y2'])]
            for divide in divides:
                for i in range(math.ceil(0.4 * B), m - math.ceil(0.4 * B) + 1): #check the combinations
                    s1 = Node()
                    s1.child_nodes = divide[0: i]
                    self.update_mbr(s1)
                    s2 = Node()
                    s2.child_nodes = divide[i: divide.__len__()]
                    self.update_mbr(s2)
                    if best_perimeter > s1.perimeter() + s2.perimeter():
                        best_perimeter = s1.perimeter() + s2.perimeter()
                        best_s1 = s1
                        best_s2 = s2

        for child in best_s1.child_nodes:
            child.parent = best_s1
        for child in best_s2.child_nodes:
            child.parent = best_s2

        return best_s1, best_s2


    def add_child(self, node, child):
        node.child_nodes.append(child) #add child nodes to the current parent (node) and update the MBRs. It is used in handeling overflows
        child.parent = node
        if child.MBR['x1'] < node.MBR['x1']:
            node.MBR['x1'] = child.MBR['x1']
        if child.MBR['x2'] > node.MBR['x2']:
            node.MBR['x2'] = child.MBR['x2']
        if child.MBR['y1'] < node.MBR['y1']:
            node.MBR['y1'] = child.MBR['y1']
        if child.MBR['y2'] > node.MBR['y2']:
            node.MBR['y2'] = child.MBR['y2']
    # return the child whose MBR requires the minimum increase in perimeter to cover p

    def add_data_point(self, node, data_point): #add data points and update the MBR
        node.data_points.append(data_point)
        if data_point['x'] < node.MBR['x1']: #if x coordinate of point <
            node.MBR['x1'] = data_point['x']
        if data_point['x'] > node.MBR['x2']:
            node.MBR['x2'] = data_point['x']
        if data_point['y'] < node.MBR['y1']:
            node.MBR['y1'] = data_point['y']
        if data_point['y'] > node.MBR['y2']:
            node.MBR['y2'] = data_point['y']


    def update_mbr(self, node): #update MBRs when forming a new MBR. It is used in checking the combinations and update the root
        x_list = []
        y_list = []
        if node.is_leaf():
            x_list = [point['x'] for point in node.data_points]
            y_list = [point['y'] for point in node.data_points]
        else:
            x_list = [child.MBR['x1'] for child in node.child_nodes] + [child.MBR['x2'] for child in node.child_nodes]
            y_list = [child.MBR['y1'] for child in node.child_nodes] + [child.MBR['y2'] for child in node.child_nodes]
        new_mbr = {
            'x1': min(x_list),
            'x2': max(x_list),
            'y1': min(y_list),
            'y2': max(y_list)
        }
        node.MBR = new_mbr


if __name__ == '__main__':
    main()

