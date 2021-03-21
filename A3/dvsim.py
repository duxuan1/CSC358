import random, copy, sys
from math import inf
from typing import List

from dvnode import *

# the number of nodes in the network
# modify it when you test different graph sizes
NUM_NODES = 3

# event types
EVT_FROM_LINK_LAYER = 0
EVT_LINK_CHANGE = 1

class Packet:
    '''
    A packet is a message that is sent between neighbouring nodes, to tell the
    neighbour about their latest distance vector.
    '''

    def __init__(self, src, dest, dist_vector):

        self.src = src      # the sender of the packet
        self.dest = dest    # the receiver of the packet

        # self.dist_vector is a list of int
        self.dist_vector = copy.deepcopy(dist_vector)
        assert len(self.dist_vector) == NUM_NODES

    def copy(self):
        '''
        return a copy of the packet
        '''
        pkt = Packet(self.src, self.dest, self.dist_vector)
        return pkt

    def get_src(self) -> int:

        return self.src

    def get_dest(self) -> int:

        return self.dest

    def get_dist_vector(self) -> List[int]:

        return self.dist_vector

    def __str__(self):

        return "src: {}, dest: {}, dist_vector: {}".format(\
                self.src, self.dest, self.dist_vector)

class Event:
    '''
    Two types of events: 
    - EVT_FROM_LINK_LAYER: a node receives a message from the link layer
    - EVT_LINK_CHANGE: a node's link's cost is changed
    '''
    def __init__(self, time: float, typ: int, node: int, pkt: Packet=None):

        self.time = time    # time of the event
        self.type = typ     # EVT_FROM_LINK_LAYER or EVT_LINK_CHANGE
        self.node = node    # the node receiving the message (EVT_FROM_LINK_LAYER)
                            # node is irrelevant for EVT_LINK_CHANGE
        if pkt:             # pkt is None for EVT_LINK_CHANGE
            self.packet = pkt.copy()

    def get_time(self) -> float:

        return self.time

    def get_type(self) -> int:

        return self.type

    def get_node(self) -> int:

        return self.node

    def get_packet(self) -> Packet:

        return self.packet

    def __str__(self):

        return "time: {}, type: {}, node: {}, packet: {}".format(\
                self.time, self.type, self.node, self.packet)

class EventList:
    '''
    The list of events in the simulation
    '''
    def __init__(self):

        # data is a list of Event
        self.data = list()

    def add(self, evt: Event):
        '''
        add a new event to the event list
        '''
        self.data.append(evt)
        return

    def remove_next(self) -> Event:
        '''
        remove and return the event with the smallest time value, 
        i.e., the next event to take place
        '''
        if len(self.data) == 0:
            return None
        smallest_time = inf
        smallest_index = None
        for i in range(len(self.data)):
            if self.data[i].get_time() < smallest_time:
                smallest_time = self.data[i].get_time()
                smallest_index = i
        return self.data.pop(smallest_index)

    def get_last_packet_time(self, from_node: int, to_node: int) -> float:
        '''
        return the time of the last message from from_node to to_node
        return 0 if such message does not exist in the event list
        '''
        rv = 0.0
        for evt in self.data:
            if evt.get_type() == EVT_FROM_LINK_LAYER and \
                    evt.get_node() == to_node and \
                    evt.get_packet().get_src() == from_node:
                rv = max(rv, evt.get_time())
        return rv

class Simulator:
    '''
    The simulator class
    '''
    def __init__(self, link_changes: int, seed: int):
        '''
        link_changes (1 or 0): whether to include link-change event in the sim
        seed: seed for random number generator
        '''
        self.total_msgs = 0
        self.link_changes = link_changes
        self.event_list = EventList()
        random.seed(seed)
        self.clocktime = 0.0

        # uncomment one of the following two lines to generate the graph,
        # manually or randomly
        # this method will populate self.cost
        self.generate_topology()
        #self.generate_random_topology()

        # creating the nodes of in the graph
        # calling the __init__ method of the Node class
        self.nodes = [Node(x, self) for x in range(NUM_NODES)]

        if link_changes:
            # modify the code the below to add more link-change events
            self.event_list.add(Event(10000.0, EVT_LINK_CHANGE, 0))

    def generate_topology(self):
        '''
        This method manually defines a specific input graph.
        Modify this method to test different graphs
        Make sure the size of this graph matches NUM_NODES
        '''
        self.cost = [
                      [0,   4,   50], 
                      [4,   0,   1], 
                      [50,  1,   0]
                    ]
        return

    def generate_random_topology(self):
        '''
        This method generates a random topology with NUM_NODES nodes
        '''
        choices = [1, 2, 3, 5, 7, 10, 15, 20, inf, inf]
        self.cost = [[0 for _ in range(NUM_NODES)] for _ in range(NUM_NODES)]
        for i in range(NUM_NODES):
            for j in range(i+1, NUM_NODES):
                self.cost[i][j] = self.cost[j][i] = random.choice(choices)
        return

    def generate_link_change(self):
        '''
        This method defines the link-change events that are added in __init__
        The method is called when processing a link-change event in the event list.
        You may modify this method to test different link-change events.
        '''
        nodea = 0
        nodeb = 1
        new_cost = 2
        if self.clocktime > 10001.0:
            new_cost = 8   # use different new_cost depending on its time

        self.cost[nodea][nodeb] = new_cost
        self.cost[nodeb][nodea] = new_cost
        self.nodes[nodea].link_cost_change_handler(nodeb, new_cost)
        self.nodes[nodeb].link_cost_change_handler(nodea, new_cost)
        return

    def run(self):
        '''
        Run the simulation
        '''
        next = None
        while True:
            next = self.event_list.remove_next()
            if next is None:
                break

            print("\nmain(): event received. t={}, node={}".format(\
                    next.get_time(), next.get_node()))
            if next.get_type() == EVT_FROM_LINK_LAYER:
                p = next.get_packet()
                print("\tsrc={}, dest={}, contents={}".format(\
                        p.get_src(), p.get_dest(), p.get_dist_vector()))
            elif next.get_type() == EVT_LINK_CHANGE:
                print("\tLink cost change.")
            else:
                raise RuntimeError("Panic: invalid type of event")

            self.clocktime = next.get_time()

            if next.get_type() == EVT_FROM_LINK_LAYER:
                p = next.get_packet()
                if next.get_node() < 0 or next.get_node() >= NUM_NODES:
                    raise RuntimeError("Panic: Unknown event node")
                # the node receiving the packet calls its update() method
                self.nodes[next.get_node()].update(p)
            elif next.get_type() == EVT_LINK_CHANGE:
                # link-change event occurs
                self.generate_link_change()
            else:
                raise RuntimeError("Panic: Unknown event type")

        print("\nSimulator terminated at t={}, no packets in medium.".format(\
                self.clocktime))
        print("Total number of messages:", self.total_msgs)
        print("\nFinal distance tables:")
        for node in self.nodes:
            print()
            node.print_dist_table()
        
        print("\nShortest paths:")
        for i in range(NUM_NODES):
            for j in range(i+1, NUM_NODES):
                self.print_shortest_path(i, j)
        return

    def to_link_layer(self, pkt: Packet):
        '''
        send a Packet pkt to the link layer
        '''
        current_packet = None
        arrival_time = None

        if pkt.get_src() < 0 or pkt.get_src() >= NUM_NODES:
            raise RuntimeError("to_link_layer(): Illegal src id")

        if pkt.get_dest() < 0 or pkt.get_dest() >= NUM_NODES:
            raise RuntimeError("to_link_layer(): Illegal dest id")

        if pkt.get_src() == pkt.get_dest():
            raise RuntimeError("to_link_layer(): src same as dest")

        if self.cost[pkt.get_src()][pkt.get_dest()] == inf:
            raise RuntimeError("to_link_layer(): src and dest not connected")

        print("to_link_layer(): src={}, dest={}, distance: {}".format(\
                pkt.get_src(), pkt.get_dest(), pkt.get_dist_vector()))

        # Schedule the arrival time of this packet
        arrival_time = self.event_list.get_last_packet_time(\
                pkt.get_src(), pkt.get_dest())
        if arrival_time == 0.0:
            arrival_time = self.clocktime
        arrival_time += (1.0 + random.random() * 9.0)

        print("to_link_layer(): scheduled arrival_time: {}".format(arrival_time))
        current_packet = pkt.copy()
        self.event_list.add(Event(arrival_time, EVT_FROM_LINK_LAYER, \
                current_packet.get_dest(), current_packet))

        self.total_msgs += 1
        return

    def print_shortest_path(self, from_node, to_node):
        '''
        print the shortest path from from_node to to_node
        '''
        path = [from_node]
        curr = from_node
        if self.nodes[from_node].get_dist_vector()[to_node] == inf:
            print("Path does not exist from Node {} to {}".format(\
                    from_node, to_node))
            return
        while curr != to_node:
            curr = self.nodes[curr].get_predecessor(to_node)
            path.append(curr)
        print("Path from Node {} to {}: {}".format(from_node, to_node,\
                " -> ".join([str(x) for x in path])))
        return

if __name__ == "__main__":

    if len(sys.argv) != 3:
        print("Usage: python3 dvsim.py HasLinkChange Seed")
        exit(0)

    has_link_change = int(sys.argv[1])
    seed = int(sys.argv[2])

    sim = Simulator(has_link_change, seed)
    sim.run()

