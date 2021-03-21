import copy
from math import inf
from dvsim import Packet, NUM_NODES

class Node:
    '''
    a node in the network
    '''
    def __init__(self, nodeid: int, simulator):
        '''
        Constructing a node in the network
        '''
        self.nodeid = nodeid        # nodeid is the node number
        self.simulator = simulator
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

        # self.predessor is a list of int
        # self.predecessor keeps a list of the predecessor of this node in the
        # path to each of the other nodes in the graph
        # You need to make sure this predecessors list is correctly updated
        # throughout the algorithm's execution
        self.predecessors = [None for _ in range(NUM_NODES)]

        # TODO: complete this method
        pass

    def get_link_cost(self, other):
        '''
        Get the cost of the link between this node and other.
        Note: This is the ONLY method that you're allowed use to get the cost of
        a link, i.e., do NOT access self.simulator.cost anywhere else in this
        class.
        DO NOT MODIFY THIS METHOD
        '''
        return self.simulator.cost[self.nodeid][other]

    def get_dist_vector(self):
        '''
        Get the distance vector of this node
        DO NOT MODIFY THIS METHOD
        '''
        return self.dist_table[self.nodeid]

    def get_predecessor(self, other: int) -> int:
        '''
        Get the predecessor of this node in the path to other
        DO NOT MODIFY THIS METHOD
        '''
        return self.predecessors[other]

    def update(self, pkt: Packet):
        '''
        Handle updates when a packet is received. May need to call
        self.simulator.to_link_layer() with new packets based upon what after
        the update. Be careful to construct the source and destination of the
        packet correctly. Read dvsim.py for more details about the potential
        errors.
        '''

        # TODO: implement this method
        pass

    def link_cost_change_handler(self, which_link: int, new_cost: int):
        '''
        Handles the link-change event. The cost of the link between this node
        and which_link has been changed to new_cost. Need to update the
        information that is stored at this node, and notify the neighbours if
        necessary.
        '''

        # TODO: implement this method
        pass

    def print_dist_table(self):
        '''
        Prints the distance table stored at this node. Useful for debugging.
        DO NOT MODIFY THIS METHOD
        '''
        print(" D{}|".format(self.nodeid).rjust(5), end="")
        for i in range(NUM_NODES):
            print("    {}".format(i), end="")
        print("\n----+{}".format("-----"*NUM_NODES))
        for i in range(NUM_NODES):
            print("{:4d}|".format(i), end="")
            for j in range(NUM_NODES):
                print(str(self.dist_table[i][j]).rjust(5), end="")
            print()

