import copy
from math import inf
from dvsim import Packet, NUM_NODES


class Node:
    """
    a node in the network
    """
    def __init__(self, nodeid: int, simulator):
        """
        Constructing a node in the network
        """
        self.nodeid = nodeid        # nodeid is the node number
        self.simulator = simulator
        self.neighbours = self.find_neighbours()  # add node's neighbours to self.neighbours  
        self.send_pkt(self.simulator.cost[self.nodeid]) # send packet to node's neighbours  
        # simulator is passed here so that the node can access 
        # - simulator.cost[nodeid] (only access the costs of this node's links) and
        # - simulator.to_link_layer() to send the message
        # You should not access anything else inside the simulator,

        # self.dist_table has the distance vectors as known by this node
        # It is an NxN matrix where N is NUM_NODES.
        # You need to make sure the dist_table is correctly updated throughout
        # the algorithm's execution.
        # Tip: although dist_table has N rows, each node might only access and
        # update a subset of the rows.
        self.dist_table = [[inf for _ in range(NUM_NODES)] for _ in range(NUM_NODES)]  
        self.dist_table[self.nodeid] = self.simulator.cost[self.nodeid][:]  
  
        # self.predessor is a list of int  
        # self.predecessor keeps a list of the predecessor of this node in the  
        # path to each of the other nodes in the graph  
        self.predecessors = [i for i in range(NUM_NODES)] # initialize self.predecessors list  
        self.predecessors[self.nodeid] = None  

    def get_link_cost(self, other):
        """
        Get the cost of the link between this node and other.
        Note: This is the ONLY method that you're allowed use to get the cost of
        a link, i.e., do NOT access self.simulator.cost anywhere else in this
        class.
        DO NOT MODIFY THIS METHOD
        """
        return self.simulator.cost[self.nodeid][other]

    def get_dist_vector(self):
        """
        Get the distance vector of this node
        DO NOT MODIFY THIS METHOD
        """
        return self.dist_table[self.nodeid]

    def get_predecessor(self, other: int) -> int:
        """
        Get the predecessor of this node in the path to other
        DO NOT MODIFY THIS METHOD
        """
        return self.predecessors[other]

    def find_neighbours(self):
        """
        find neighbours from cost table
        inf col meaning not neighbours
        """
        neighbours = []
        cost_row = self.simulator.cost[self.nodeid]
        for i in range(NUM_NODES):
            if i != self.nodeid and cost_row[i] != inf:
                neighbours.append(i)
        return neighbours

    def send_pkt(self, vector):  
        """
        send packet to self node's neighbors 
        """
        for i in range(NUM_NODES):  
            if i in self.neighbours:  
                p = Packet(self.nodeid, i, vector)  
                self.simulator.to_link_layer(p)  

    def update(self, pkt: Packet):
        """
        Handle updates when a packet is received. May need to call
        self.simulator.to_link_layer() with new packets based upon what after
        the update. Be careful to construct the source and destination of the
        packet correctly. Read dvsim.py for more details about the potential
        errors.
        """
        # copy sender vector  
        self.dist_table[pkt.src] = pkt.dist_vector  
        self_vector = self.get_dist_vector()  
        old_vector = self_vector[:]  
        for dst in range(len(self_vector)):  
            if dst != self.nodeid:  # recalculate distance vectors to other nodes expect itself  
                min_path_to_dst = inf  
                for neighbor in self.neighbours:  
                    new_path = self.get_link_cost(neighbor) + self.dist_table[neighbor][dst]  
                    if new_path < min_path_to_dst: # if we find a new path smaller than the minimum path to destination node  
                        min_path_to_dst = new_path  
                        self.predecessors[dst] = neighbor  
                # printout statement for report  
                # if min_path_to_dst < self_vector[dst]:  
                #     print("Node " + str(self.nodeid) + " " + "original shortest path to Node " + str(dst) + " with distance " + str(self_vector[dst]))  
                #     print("Node " + str(self.nodeid) + " " + "New shortest path to Node " + str(dst) + " with distance " + str(min_path_to_dst))  
  
                self_vector[dst] = min_path_to_dst  # update the distance to destination node to new calculated minimum path  
        # if some vector value in self_vector changes, tell neighbours  
        if self_vector != old_vector:  
            self.send_pkt(self_vector) 

    def link_cost_change_handler(self, which_link: int, new_cost: int):
        """
        Handles the link-change event. The cost of the link between this node
        and which_link has been changed to new_cost. Need to update the
        information that is stored at this node, and notify the neighbours if
        necessary.
        """
        if new_cost == inf: # handle edge case, when we set new_cost to inf, it means   
                            # which_link no longer connects with self node  
            self.neighbours.remove(which_link)  
        self.dist_table[self.nodeid][which_link] = new_cost # update dist_table to new_cost  
        self.send_pkt(self.dist_table[self.nodeid]) # tell neighbors that new cost change  

    def print_dist_table(self):
        """
        Prints the distance table stored at this node. Useful for debugging.
        DO NOT MODIFY THIS METHOD
        """
        print(" D{}|".format(self.nodeid).rjust(5), end="")
        for i in range(NUM_NODES):
            print("    {}".format(i), end="")
        print("\n----+{}".format("-----"*NUM_NODES))
        for i in range(NUM_NODES):
            print("{:4d}|".format(i), end="")
            for j in range(NUM_NODES):
                print(str(self.dist_table[i][j]).rjust(5), end="")
            print()
