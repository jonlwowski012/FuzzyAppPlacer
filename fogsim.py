"""
# Install Yet Another Fog Simulator
"""

#!cd ~ && git clone https://github.com/acsicuib/YAFS.git
#!cd ~/YAFS && python setup.py install

"""# Imports"""

import yafs
from yafs.topology import Topology
import random

import argparse

from yafs.core import Sim
from yafs.application import Application,Message

from yafs.population import *
from yafs.topology import Topology

from yafs.stats import Stats
from yafs.distribution import deterministicDistribution
from yafs.utils import fractional_selectivity
import time
import sys
import numpy as np
from numpy import random

from yafs.placement import Placement
from yafs.selection import Selection
import networkx as nx
import logging.config
import os

"""# Cloud Placement App"""

class CloudPlacement(Placement):
    """
    This implementation locates the services of the application in the cheapest cloud regardless of where the sources or sinks are located.
    It only runs once, in the initialization. M.O is deploy on node labelled cloud/edge/end_0 then manually change it based on parameters given by FuzzyAppPlacer
    """
    def initial_allocation(self, sim, app_name):#Sim comes from the s.deploy_app and app_name is inherited from the wrong place.
        #We find the ID-nodo/resource
        #print app_name             # is printing App1 b/c "onCloud" is the argument for the __init__. I believe app_name is inherited from initial_allocation() method called in core.py line#1060
        value = {"model": "cloud_0"}
        id_cluster = sim.topology.find_IDs(value)
        app = sim.apps[app_name]#why do we need to call on this
        services = app.services
        for module in services:
            if module in self.scaleServices:
                for rep in range(0, self.scaleServices[module]):
                    idDES = sim.deploy_module(app_name,module,services[module],id_cluster)#thats why e.e
                    
                    
        
    
class EdgePlacement(Placement):
    """
    This implementation locates the services of the application in the cheapest cloud regardless of where the sources or sinks are located.
    It only runs once, in the initialization.
    """
    def initial_allocation(self, sim, app_name):
        value = {"model": "edge-device_0"} # or whatever tag
        id_cluster = sim.topology.find_IDs(value)
        app = sim.apps[app_name]
        services = app.services
        for module in services:
            if module in self.scaleServices:
                for rep in range(0, self.scaleServices[module]):
                    idDES = sim.deploy_module(app_name,module,services[module],id_cluster)
                    
class EndPlacement(Placement):
    """
    This implementation locates the services of the application in the cheapest cloud regardless of where the sources or sinks are located.
    It only runs once, in the initialization.
    """
    #def setDest(self, dest):
    #    self.value={"model": dest}
    
    def initial_allocation(self, sim, app_name):
        #We find the ID-nodo/resource
        #self.value = {"model": "end-device_0"} # or whatever tag

        id_cluster = sim.topology.find_IDs(self.value)
        app = sim.apps[app_name]
        services = app.services

        for module in services:
            if module in self.scaleServices:
                for rep in range(0, self.scaleServices[module]):
                    idDES = sim.deploy_module(app_name,module,services[module],id_cluster)

class FuzzyPlacement(Placement):
    """
    #This Implements FuzzyAppPlacer.py
    
    def initial_allocation(self, sim, app_name):
        fuzzy="cloud"
        
        #CtrlFlow=Copy-Paste of above placements.
        if fuzzy=="cloud":
            value = {"model": "cloud_0"}
            id_cluster = sim.topology.find_IDs(value)
            app = sim.apps[app_name]
            services = app.services
            for module in services:
                if module in self.scaleServices:
                    for rep in range(0, self.scaleServices[module]):
                        idDES = sim.deploy_module(app_name,module,services[module],id_cluster)
        elif fuzzy=="edge":
            value = {"model": "edge-device_0"} # or whatever tag
            id_cluster = sim.topology.find_IDs(value)
            app = sim.apps[app_name]
            services = app.services
            for module in services:
                if module in self.scaleServices:
                    for rep in range(0, self.scaleServices[module]):
                        idDES = sim.deploy_module(app_name,module,services[module],id_cluster)
        elif fuzzy=="end":
            value = {"model": "end-device_0"} # or whatever tag
            id_cluster = sim.topology.find_IDs(value)
            app = sim.apps[app_name]
            services = app.services
            for module in services:
                if module in self.scaleServices:
                    for rep in range(0, self.scaleServices[module]):
                        idDES = sim.deploy_module(app_name,module,services[module],id_cluster)
        else:
            sys.exit("Check Output of FuzzyAppPlacer")
    """

"""# Minimum path calculators"""

class MinimumPath(Selection):

    def get_path(self, sim, app_name, message, topology_src, alloc_DES, alloc_module, traffic):
        """
        Computes the minimun path among the source elemento of the topology and the localizations of the module
        Return the path and the identifier of the module deployed in the last element of that path
        """
        node_src = topology_src
        DES_dst = alloc_module[app_name][message.dst]

        #print ("GET PATH")
        #print ("\tNode _ src (id_topology): %i" %node_src)
        #print ("\tRequest service: %s " %message.dst)
        #print ("\tProcess serving that service: %s " %DES_dst)

        bestPath = []
        bestDES = []

        for des in DES_dst: ## In this case, there are only one deployment
            dst_node = alloc_DES[des]
            #print ("\t\t Looking the path to id_node: %i" %dst_node)

            path = list(nx.shortest_path(sim.topology.G, source=node_src, target=dst_node))

            bestPath = [path]
            bestDES = [des]

        return bestPath, bestDES


class MinPath_RoundRobin(Selection):

    def __init__(self):
        self.rr = {} #for a each type of service, we have a mod-counter

    def get_path(self, sim, app_name, message, topology_src, alloc_DES, alloc_module, traffic):
        """
        Computes the minimun path among the source elemento of the topology and the localizations of the module
        Return the path and the identifier of the module deployed in the last element of that path
        """
        node_src = topology_src
        DES_dst = alloc_module[app_name][message.dst] #returns an array with all DES process serving


        if message.dst not in self.rr.keys():
            self.rr[message.dst] = 0


        print ("GET PATH")
        print ("\tNode _ src (id_topology): %i" %node_src)
        print ("\tRequest service: %s " %(message.dst))
        print ("\tProcess serving that service: %s (pos ID: %i)" %(DES_dst,self.rr[message.dst]))

        bestPath = []
        bestDES = []

        for ix,des in enumerate(DES_dst):
            if message.name == "M.A":
                if self.rr[message.dst]==ix:
                    dst_node = alloc_DES[des]

                    path = list(nx.shortest_path(sim.topology.G, source=node_src, target=dst_node))

                    bestPath = [path]
                    bestDES = [des]

                    self.rr[message.dst] = (self.rr[message.dst]+ 1) % len(DES_dst)
                    break
            else: #message.name == "M.B"

                dst_node = alloc_DES[des]

                path = list(nx.shortest_path(sim.topology.G, source=node_src, target=dst_node))
                if message.broadcasting:
                    bestPath.append(path)
                    bestDES.append(des)
                else:
                    bestPath = [path]
                    bestDES = [des]

        return bestPath, bestDES

"""# Setup Cloud Topology"""

def create_json_topology(resources):
  
  # Init json
  topology_json = {}
  topology_json["entity"] = []
  topology_json["link"] = []

  """
  Input: resources(dict): Defines IPT,RAM,COST,WATT,BW,PR by node number
  Output: 
  Setup device
  So Here I created a for-loop to generate the graph instead of manually each line
  Iterable Hierarchy: [k>m>n,p>q>r]
  
  MaxNumber of Cld-Edge links=nCloud*nEdge
  MaxNumber of Edge-End links=nEnd*nEdge
  I use ID ranges instead of %3 round-robin assignment because otherwise there will be a mismatch between the nodes #s generated by utils.py and the actual node IDs
  Variables:
  nCloud=Number of Cloud Devices
  nEdge=Number of Edge Devices
  nEnd=Number of End Devices
  cloudRange=Range of Cloud node ID numbers
  edgeRange=Range of Edge node ID numbers
  endRange=Range of End node ID numbers
  """
  
  nCloud=resources["COUNT"][0];
  nEdge=resources["COUNT"][1];
  nEnd=resources["COUNT"][2];
  
  #Block Assignment interval definition
  cloudRange=range(0, nCloud)#Range of Cloud Node IDs
  edgeRange=range(nCloud, nEdge+nCloud)#Range of Edge Node IDs
  endRange=range(nEdge+nCloud, nEdge+nCloud+nEnd)#Range of End Node IDs
  
  #Create Dictionary of Resources {"IPT":,"RAM":,"COST":,"WATT":,"BW":,"PR":}?
  #Inputs for FuzzyAppPlacer: percent_parr, run_mag, latency, latency_tol
  
  #Because of how the graph data export works (utils.py L47) I can't use %3 assignments, because if N is the highest ID number, all numbers [0,N] have to be assigned to nodes
  #If we don't want to place the same service on every single cloud device, the key "model" has to be changed for each device (population.py L96 & L105).
  #This obsv. is further justified in practice by examples/Tutorial (main3.py L70-73)
  
  
  #Generate Cloud Nodes
  for k,p in zip(cloudRange,range(0,nCloud)):
    cloud_dev  = {"id": k, "model": "cloud_"+str(p), "mytag": "cloud", "IPT": resources["IPT"][k], "RAM": resources["RAM"][k],"COST": resources["COST"][k],"WATT":resources["WATT"][k]}
    topology_json["entity"].append(cloud_dev)
  #Generate Edge Nodes
  for k,p in zip(edgeRange,range(0,nEdge)):
    edge_dev   = {"id": k, "model": "edge-device_"+str(p), "IPT": resources["IPT"][k], "RAM": resources["RAM"][k],"COST": resources["COST"][k],"WATT":resources["WATT"][k]}
    topology_json["entity"].append(edge_dev)
  
  #Generate End Nodes
  for k,p in zip(endRange,range(0,nEnd)):
    end_dev    = {"id": k, "model": "end-device_"+str(p), "IPT": resources["IPT"][k], "RAM": resources["RAM"][k],"COST": resources["COST"][k], "WATT": resources["WATT"][k]}
    topology_json["entity"].append(end_dev)
  
  #Generate Links (Middle Out, any edge connects to all cloud and end nodes)
  for k in edgeRange:
    
    #Generate Edge to Cloud Links (Should I change this to only 1 master talking to all edges?)
    for m in cloudRange:
      link_to_cloud = {"s": k, "d": m, "BW": resources["BW"][k][m], "PR": resources["PR"][k][m]}
      topology_json["link"].append(link_to_cloud)
    
    #Generate Edge to End Links
    for m in endRange:
      link_to_end = {"s": k, "d": m, "BW": resources["BW"][k][m], "PR": resources["PR"][k][m]}
      topology_json["link"].append(link_to_end)
      
  t = Topology()
  t.load(topology_json)
  return topology_json

"""# Setup Application"""

def create_application(name, instructions_ma, instructions_mb, bytes_a, bytes_b):
    # APLICATION
    a = Application(name=name)

    # (S) --> (ServiceA) --> (A)
    a.set_modules([{"Sensor_"+name:{"Type":Application.TYPE_SOURCE}},
                   {"Service_"+name: {"RAM": 10, "Type": Application.TYPE_MODULE}},
                   {"Actuator_"+name: {"Type": Application.TYPE_SINK}}
                   ])
    """
    Messages among MODULES (AppEdge in iFogSim)
    """
    m_a = Message("M.A_"+name, "Sensor_"+name, "Service_"+name, instructions=instructions_ma, bytes=bytes_a)
    m_b = Message("M.B_"+name, "Service_"+name, "Actuator_"+name, instructions=instructions_mb, bytes=bytes_b)

    """
    Defining which messages will be dynamically generated # the generation is controlled by Population algorithm
    """
    a.add_source_messages(m_a)

    """
    MODULES/SERVICES: Definition of Generators and Consumers (AppEdges and TupleMappings in iFogSim)
    """
    # MODULE SERVICES
    a.add_service_module("Service_"+name, m_a, m_b, fractional_selectivity, threshold=1.0)

    return a

"""# Setup Simulation"""

#@profile
#Jonathan's but standardizing the appname, and adding app w/ other's info
def setup_sim(simulated_time,userplace,others_info,seed):
    random.seed(RANDOM_SEED)
    #np.random.seed(RANDOM_SEED)
    """
    AVAILABLE RESOURCES (resources(dict))
    
    Keys:
    BW(int): [0,inf]         || Symmetric Bandwidth matrix (link data)
    PR(int): [0,inf]         || Symmetric Propagation Rate matrix (link data) NOTE: This is the base time delay between links. The formula in the readthedocs.io was wrong.
    IPT(int): [0,inf]        || Instructions Per unit Time 1d array (node data)
    RAM(int): [0,inf]        || Memory 1d array (node data)
    COST(int): [-inf,inf]    || Cost per unit time (node data) #not considered
    WATT(int): [0,inf]       || Power per unit time (node data) #not considered
    =================================================================
    WORK LOAD
    =================================================================
    INTEGRATION OF FUZZY APP PLACER
    
    Ideally I want to be able to define these variables given resources(dict)
    
    Inputs:
    speedup(float): [0,1]    || Factor benefit from cloud placement.
    run_mag(int): [0,inf]    || Algorithm Runtime
    latency(float): [0,inf]  || Expected Latency (minimum of path)
    throughput(int): [0,inf] || Expected Throughput (minimum of path) (mbps)
    bandwidth(int): [0,inf]  || Bandwidth of network (mbps)
    others_info(bool): [0,1] || Answer to "Does Service require data from multiple end devices?"
    
    Outputs:
    decision(str): [cloud/edge/end]
    """
    np.random.seed(seed) #Reproducibility
    
    work={"COUNT":1,"BYTES":[],"INST":[]}
    
    #From App Placer
    #Config 1-2
    
    #Config 2
    
    #Config 3
    #cloud_speedup=500+np.random.rand()*500 #cs~Uniform(1,10)
    #edge_speedup=10#+np.random.rand()*2    #es~Uniform(1,3)
    #latency=0.3+3*np.random.rand()  #lat~Uniform(0,1)
    #bandwidth=2+8*np.random.rand() #bw~Uniform(2,10)
    #throughput=bandwidth/work["COUNT"]*(0.8+0.2*np.random.rand())
    #run_mag=5*np.random.rand() #mag~Unform(0,1)
    
    #Config 4-5 (Results from "Towards the Optimal Placement...")
    cloud_speedup=1+9*np.random.rand() #cs~Uniform(1,10)
    edge_speedup=1+np.random.rand()*2    #es~Uniform(1,3)
    latency=np.random.rand()    #lat~Uniform(0,1)
    bandwidth=2+8*np.random.rand() #bw~Uniform(2,10)
    run_mag=10*np.random.rand() #run_mag~Uniform(0,10)
    throughput=bandwidth/work["COUNT"]*np.random.rand()
    
    #Aliases
    lat=latency
    bw=bandwidth
    tp=throughput
    
    resources={"COUNT": [1,1,2],"IPT":[100e6*cloud_speedup,100e6*edge_speedup,100e6,100e6],"RAM":[40e6,40e3,4e3,4e3],"COST":[3,3,3,3],"WATT":[2,4,4,4],"BW":[[0,10*tp,0,0],[10*tp,0,tp,tp],[0,tp,0,0],[0,tp,0,0]],"PR":[[0,lat,0,0],[lat,0,lat/10,lat/10],[0,lat/10,0,0],[0,lat/10,0,0]]}
    
    work["INST"]=[resources["IPT"][2]*run_mag]*work["COUNT"]
    msgSize=tp*lat*bw/(bw-tp)*1e6
    #msgSize=1000
    work["BYTES"]=[msgSize]*work["COUNT"]
     
    
    placements=[]
    pops=[]
    apps=[]
    
    #Generating Two Initial Placement policies for each app.
    for k in range(0,work["COUNT"]):
      #place=raw_input("Should App"+str(k)+" go on Cloud(c), Edge(e), or End Device(d)?\t")
      #n=int(raw_input("How many services should App"+str(k)+" have?\t"))
      place=userplace[k]
      assert place.lower()=="c" or place.lower()=="e" or place.lower()=="d0" or place.lower()=="d1"  
      #assert n>0
      if place.lower()=="c":
        placements.append(CloudPlacement("onCloud"+str(k)))
        placements[-1].scaleService({"Service_"+"App"+str(k): 1})
      if place.lower()=="e":
        placements.append(EdgePlacement("onEdge"+str(k)))
        placements[-1].scaleService({"Service_"+"App"+str(k): 1})
      if place.lower()=="d0":
        placements.append(EndPlacement("onEnd"+str(k)))
        #placements[-1].setValue="end-device_"+str(m)
        placements[-1].value={"model": "end-device_0"}
        placements[-1].scaleService({"Service_"+"App"+str(k): 1})
      if place.lower()=="d1":
        placements.append(EndPlacement("onEnd"+str(k)))
        #placements[-1].setValue="end-device_"+str(m)
        placements[-1].value={"model": "end-device_1"}
        placements[-1].scaleService({"Service_"+"App"+str(k): 1})
    """
    TOPOLOGY from a json
    """
    t = Topology()
    t_json = create_json_topology(resources)
    t.load(t_json)
    t.write("network.gexf")
    stop_time = simulated_time
    s = Sim(t, default_results_path="Results")
    
    dDistribution = deterministicDistribution(name="Deterministic",time=100)
    selectorPath = MinimumPath()

    #Final Deploy
    for k in range(len(placements)):
      #n=int(raw_input("Does this app"+str(k)+" use sensors from end-device_0 (0), end-device_1 (1), or both (2)?\t"))
      #CtrlFlow for if app is on UAV (0), UGV (1), or UAV Data-->UGV Action (2)
      #assert others_info in range(2)
      if others_info[k]==0:
        app = create_application("App"+str(k), work["INST"][k],work["INST"][k], work["BYTES"][k],work["BYTES"][k])
        pop = Statical("Statical"+str(k))
        pop.set_sink_control({"id": 0, "model": "end-device_"+str(k),"number":1, "module": app.get_sink_modules()}) #sskc["number"]=# of actuators
        pop.set_src_control({"id": 0, "model": "end-device_"+str(k), "number":1, "message": app.get_message("M.A_App"+str(k)), "distribution": dDistribution}) #sscc["number"]=# of sensors
      #elif n==1:
        #app = create_application("App"+str(k), work["INST"][k],work["INST"][k], work["BYTES"][k],work["BYTES"][k])
        #pop = Statical("Statical0"+str(k))
        #pop.set_sink_control({"id": 0, "model": "end-device"+str(k),"number":1, "module": app.get_sink_modules()}) #sskc["number"]=# of actuators
        #pop.set_src_control({"id": 0, "model": "end-device"+str(k), "number":1, "message": app.get_message("M.A_App"+str(k)), "distribution": dDistribution}) #sscc["number"]=# of sensors
        #others_info=0
      else:
        app = create_application("App"+str(k), work["INST"][k],work["INST"][k], work["BYTES"][k],work["BYTES"][k])
        pop = Statical("Statical0"+str(k))
        pop.set_sink_control({"id": 0, "model": "end-device_0","number":1, "module": app.get_sink_modules()}) #sskc["number"]=# of actuators
        pop.set_src_control({"id": 0, "model": "end-device_1", "number":1, "message": app.get_message("M.A_App"+str(k)), "distribution": dDistribution}) #sscc["number"]=# of sensors
      
      s.deploy_app(app, placements[k], pop, selectorPath)
    """
    SIMULATION ENGINE
    """
    s.run(stop_time,show_progress_monitor=False)
    #s.draw_allocated_topology() # for debugging
    if userplace==['c']:
    #Print inputs for app placer
    #print "="*40
      print "Inputs for fuzzy app placer:"
      print "-"*40
      print "cloud speedup =",cloud_speedup
      print "edge speedup =",edge_speedup
      print "run_mag =",run_mag*1000
      print "latency =",latency*1000
      print "throughput =",throughput
      print "bandwidth =",bandwidth
      print "others_info =",others_info

      #print "="*40

"""# Main Function"""

RANDOM_SEED = 10
#following the same iterator convention: (k>m>n,p>q>r)
devs=["c","e","d0"]
seed=95

for k0 in range(len(devs)):
  #for m0 in range(len(devs)):
  print "="*40
  print "="*40
  start_time = time.time()
  setup_sim(simulated_time=1000, userplace=[devs[k0]], others_info=[0], seed=seed)
  print("\n--- %s seconds ---" % (time.time() - start_time))

  ### Finally, you can analyse the results:
  print "-" * 40
  print "Results: for",[devs[k0]]#,devs[m0]]
  print "-" * 40
  m = Stats(defaultPath="Results") #Same name of the results
  time_loops = [["M.A_App0", "M.B_App0","M.A_App1","M.B_App1"]]
  m.showResults2(1000, time_loops=time_loops)
#print "\t- Network saturation -"
#print "\t\tAverage waiting messages :", m.average_messages_not_transmitted()
#print "\t\tPeak of waiting messages : ", m.peak_messages_not_transmitted()
#print "\t\tTOTAL messages not transmitted: ", m.messages_not_transmitted()

RANDOM_SEED = 10

start_time = time.time()
setup_sim(simulated_time=1000, userplace=["c","e"])

print("\n--- %s seconds ---" % (time.time() - start_time))

### Finally, you can analyse the results:
print "-" * 20
print "Results:"
print "-" * 20
m = Stats(defaultPath="Results") #Same name of the results
time_loops = [["M.A_App0", "M.B_App0","M.A_App1","M.B_App1"]]
m.showResults2(1000, time_loops=time_loops)
print "\t- Network saturation -"
print "\t\tAverage waiting messages :", m.average_messages_not_transmitted()
print "\t\tPeak of waiting messages : ", m.peak_messages_not_transmitted()
print "\t\tTOTAL messages not transmitted: ", m.messages_not_transmitted()
