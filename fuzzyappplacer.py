
#!pip install scikit-fuzzy
# Import Libraries
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import matplotlib.pyplot as plt
# %matplotlib inline
from mpl_toolkits.mplot3d import Axes3D  # Required for 3D plotting
import random

class ParrEstimator:
    def __init__(self):
        self.speedup = ctrl.Antecedent(np.arange(0, 10.0, 0.01), 'speedup') # Percent of code that is parallelizable
        self.mag_runtime = ctrl.Antecedent(np.arange(0, 1.0, 0.01), 'mag_runtime') # Normalized magnitude with max runtime of 5 seconds
        self.parr_est_out = ctrl.Consequent(np.arange(0, 1, 0.01), 'parr_est_out') # Impact from 0-1 of code being paralellized
        self.max_mag = 1000.0
        self.generate_mf()
    def generate_mf(self):
        # Generate fuzzy membership functions
        self.speedup['low'] = fuzz.trapmf(self.speedup.universe, [1.0, 1.0, 1.1, 1.2])
        self.speedup['medium'] = fuzz.gaussmf(self.speedup.universe, 1.3, 0.05)
        self.speedup['high'] = fuzz.trapmf(self.speedup.universe, [1.4, 1.7, 10.0, 10.0])
        self.speedup.view()
        self.mag_runtime['low'] = fuzz.trapmf(self.mag_runtime.universe, [0, 0, 0.3, 0.4])
        self.mag_runtime['medium'] = fuzz.gaussmf(self.mag_runtime.universe, 0.5, 0.1)
        self.mag_runtime['high'] = fuzz.trapmf(self.mag_runtime.universe, [0.6, 0.7, 1.0, 1.0])
        self.mag_runtime.view()
        self.parr_est_out['low'] = fuzz.trapmf(self.parr_est_out.universe, [0, 0, 0.3, 0.4])
        self.parr_est_out['medium'] = fuzz.gaussmf(self.parr_est_out.universe, 0.5, 0.1)
        self.parr_est_out['high'] = fuzz.trapmf(self.parr_est_out.universe, [0.6, 0.7, 1.0, 1.0])
        self.parr_est_out.view()
        self.generate_rules()
    def generate_rules(self):
        # Define the Rule Set
        self.rules = []
        self.rules.append(ctrl.Rule(self.speedup['low'] & self.mag_runtime['low'], self.parr_est_out['low']))
        self.rules.append(ctrl.Rule(self.speedup['low'] & self.mag_runtime['medium'], self.parr_est_out['low']))
        self.rules.append(ctrl.Rule(self.speedup['low'] & self.mag_runtime['high'], self.parr_est_out['low']))
        self.rules.append(ctrl.Rule(self.speedup['medium'] & self.mag_runtime['low'], self.parr_est_out['low']))
        self.rules.append(ctrl.Rule(self.speedup['medium'] & self.mag_runtime['medium'], self.parr_est_out['medium']))
        self.rules.append(ctrl.Rule(self.speedup['medium'] & self.mag_runtime['high'], self.parr_est_out['high']))
        self.rules.append(ctrl.Rule(self.speedup['high'] & self.mag_runtime['low'], self.parr_est_out['medium']))
        self.rules.append(ctrl.Rule(self.speedup['high'] & self.mag_runtime['medium'], self.parr_est_out['high']))
        self.rules.append(ctrl.Rule(self.speedup['high'] & self.mag_runtime['high'], self.parr_est_out['high']))
        self.gen_ctrl_sys()
    def gen_ctrl_sys(self):
        # Create the control system
        self.parr_ctrl = ctrl.ControlSystem(self.rules)
        # Create the simulation for the control system
        self.parr_ctrl_sim = ctrl.ControlSystemSimulation(self.parr_ctrl)
    def calculate_parr_out(self,speedup,run_mag):
        self.parr_ctrl_sim.input['speedup'] = speedup
        self.parr_ctrl_sim.input['mag_runtime'] = run_mag/self.max_mag
        # Calculate the location
        self.parr_ctrl_sim.compute()
        return self.parr_ctrl_sim.output['parr_est_out']

# class LatencyEffects:
#     def __init__(self):
#         self.latency = ctrl.Antecedent(np.arange(0, 1.0, 0.01), 'latency') # Normalized latency with max being 500ms
#         self.latency_tol = ctrl.Antecedent(np.arange(0, 1.0, 0.01), 'latency_tol') # Value from 0-1 for realtime priority
#         self.latency_est_out = ctrl.Consequent(np.arange(0, 1, 0.01), 'latency_est_out') # Impact to tolerance from 0-1
#         self.max_lat = 500.0
#         self.generate_mf()
#     def generate_mf(self):
#         # Generate fuzzy membership functions
#         self.latency['low'] = fuzz.trapmf(self.latency.universe, [0, 0, 0.3, 0.4])
#         self.latency['medium'] = fuzz.gaussmf(self.latency.universe, 0.5, 0.1)
#         self.latency['high'] = fuzz.trapmf(self.latency.universe, [0.6, 0.7, 1.0, 1.0])
#         self.latency.view()
#         self.latency_tol['low'] = fuzz.trapmf(self.latency_tol.universe, [0, 0, 0.3, 0.4])
#         self.latency_tol['medium'] = fuzz.gaussmf(self.latency_tol.universe, 0.5, 0.1)
#         self.latency_tol['high'] = fuzz.trapmf(self.latency_tol.universe, [0.6, 0.7, 1.0, 1.0])
#         self.latency_tol.view()
#         self.latency_est_out['low'] = fuzz.trapmf(self.latency_est_out.universe, [0, 0, 0.3, 0.4])
#         self.latency_est_out['medium'] = fuzz.gaussmf(self.latency_est_out.universe, 0.5, 0.1)
#         self.latency_est_out['high'] = fuzz.trapmf(self.latency_est_out.universe, [0.6, 0.7, 1.0, 1.0])
#         self.latency_est_out.view()
#         self.generate_rules()
#     def generate_rules(self):
#         # Define the Rule Set
#         self.rules = []
#         self.rules.append(ctrl.Rule(self.latency['low'] & self.latency_tol['low'], self.latency_est_out['low']))
#         self.rules.append(ctrl.Rule(self.latency['low'] & self.latency_tol['medium'], self.latency_est_out['low']))
#         self.rules.append(ctrl.Rule(self.latency['low'] & self.latency_tol['high'], self.latency_est_out['low']))
#         self.rules.append(ctrl.Rule(self.latency['medium'] & self.latency_tol['low'], self.latency_est_out['medium']))
#         self.rules.append(ctrl.Rule(self.latency['medium'] & self.latency_tol['medium'], self.latency_est_out['low']))
#         self.rules.append(ctrl.Rule(self.latency['medium'] & self.latency_tol['high'], self.latency_est_out['low']))
#         self.rules.append(ctrl.Rule(self.latency['high'] & self.latency_tol['low'], self.latency_est_out['high']))
#         self.rules.append(ctrl.Rule(self.latency['high'] & self.latency_tol['medium'], self.latency_est_out['high']))
#         self.rules.append(ctrl.Rule(self.latency['high'] & self.latency_tol['high'], self.latency_est_out['low']))
#         self.gen_ctrl_sys()
#     def gen_ctrl_sys(self):
#         # Create the control system
#         self.lat_ctrl = ctrl.ControlSystem(self.rules)
#         # Create the simulation for the control system
#         self.lat_ctrl_sim = ctrl.ControlSystemSimulation(self.lat_ctrl)
#     def calculate_lat_out(self,latency,latency_tol):
#         self.lat_ctrl_sim.input['latency'] = latency/self.max_lat
#         self.lat_ctrl_sim.input['latency_tol'] = latency_tol
#         # Calculate the location
#         self.lat_ctrl_sim.compute()
#         return self.lat_ctrl_sim.output['latency_est_out']

class ContainerEstimator:
    def __init__(self):
        self.parr_est_block = ParrEstimator()
        self.parr_est = ctrl.Antecedent(np.arange(0, 1.0, 0.01), 'parr_est') # Output from parr_est
        self.lat_est = ctrl.Antecedent(np.arange(0, 1.0, 0.01), 'lat_est') # Normalized latency with max being 500ms
        self.band_ratio = ctrl.Antecedent(np.arange(0, 1, 0.01), 'band_ratio') # Ratio of bandwidth/throughput, higher is better for cloud
        self.others_info = ctrl.Antecedent(np.arange(0, 1, 0.01), 'others_info') # Does the algorithm require info from other nodes
        self.container_loc = ctrl.Consequent(np.arange(0, 1, 0.01), 'container_loc') # Placement of container 0.0 end, 0.5 edge, 1.0 cloud
        self.generate_mf()
    def generate_mf(self):
        # Generate fuzzy membership functions
        self.parr_est['low'] = fuzz.trapmf(self.parr_est.universe, [0, 0, 0.3, 0.4])
        self.parr_est['medium'] = fuzz.gaussmf(self.parr_est.universe, 0.5, 0.1)
        self.parr_est['high'] = fuzz.trapmf(self.parr_est.universe, [0.6, 0.7, 1.0, 1.0])
        self.parr_est.view()
        self.lat_est['low'] = fuzz.trapmf(self.lat_est.universe, [0, 0, 0.3, 0.4])
        self.lat_est['medium'] = fuzz.gaussmf(self.lat_est.universe, 0.5, 0.1)
        self.lat_est['high'] = fuzz.trapmf(self.lat_est.universe, [0.6, 0.7, 1.0, 1.0])
        self.lat_est.view()
        self.band_ratio['low'] = fuzz.trapmf(self.band_ratio.universe, [0, 0, 0.3, 0.4])
        self.band_ratio['medium'] = fuzz.gaussmf(self.band_ratio.universe, 0.5, 0.1)
        self.band_ratio['high'] = fuzz.trapmf(self.band_ratio.universe, [0.6, 0.7, 1.0, 1.0])
        self.band_ratio.view()
        self.others_info['no'] = fuzz.trapmf(self.others_info.universe, [0, 0, 0.500,0.500])
        self.others_info['yes'] = fuzz.trapmf(self.others_info.universe, [0.500, 0.500,1.0,1.0])
        self.others_info.view()
        self.container_loc['end'] = fuzz.trapmf(self.container_loc.universe, [0, 0, 0.3, 0.4])
        self.container_loc['edge'] = fuzz.gaussmf(self.container_loc.universe, 0.5, 0.05)
        self.container_loc['cloud'] = fuzz.trapmf(self.container_loc.universe, [0.6, 0.7, 1.0, 1.0])
        self.container_loc.view()
        self.generate_rules()
    def generate_rules(self):
        # Define the Rule Set
        self.rules = []
        self.rules.append(ctrl.Rule(self.parr_est['low'] & self.lat_est['low'] & self.band_ratio['low'] & self.others_info['no'], self.container_loc['end']))
        self.rules.append(ctrl.Rule(self.parr_est['low'] & self.lat_est['low'] & self.band_ratio['low'] & self.others_info['yes'], self.container_loc['edge']))
        self.rules.append(ctrl.Rule(self.parr_est['low'] & self.lat_est['low'] & self.band_ratio['medium'] & self.others_info['no'], self.container_loc['end']))
        self.rules.append(ctrl.Rule(self.parr_est['low'] & self.lat_est['low'] & self.band_ratio['medium'] & self.others_info['yes'], self.container_loc['edge']))
        self.rules.append(ctrl.Rule(self.parr_est['low'] & self.lat_est['low'] & self.band_ratio['high'] & self.others_info['no'], self.container_loc['end']))
        self.rules.append(ctrl.Rule(self.parr_est['low'] & self.lat_est['low'] & self.band_ratio['high'] & self.others_info['yes'], self.container_loc['edge']))

        self.rules.append(ctrl.Rule(self.parr_est['low'] & self.lat_est['medium'] & self.band_ratio['low'] & self.others_info['no'], self.container_loc['end']))
        self.rules.append(ctrl.Rule(self.parr_est['low'] & self.lat_est['medium'] & self.band_ratio['low'] & self.others_info['yes'], self.container_loc['edge']))
        self.rules.append(ctrl.Rule(self.parr_est['low'] & self.lat_est['medium'] & self.band_ratio['medium'] & self.others_info['no'], self.container_loc['end']))
        self.rules.append(ctrl.Rule(self.parr_est['low'] & self.lat_est['medium'] & self.band_ratio['medium'] & self.others_info['yes'], self.container_loc['edge']))
        self.rules.append(ctrl.Rule(self.parr_est['low'] & self.lat_est['medium'] & self.band_ratio['high'] & self.others_info['no'], self.container_loc['end']))
        self.rules.append(ctrl.Rule(self.parr_est['low'] & self.lat_est['medium'] & self.band_ratio['high'] & self.others_info['yes'], self.container_loc['edge']))

        self.rules.append(ctrl.Rule(self.parr_est['low'] & self.lat_est['high'] & self.band_ratio['low'] & self.others_info['no'], self.container_loc['end']))
        self.rules.append(ctrl.Rule(self.parr_est['low'] & self.lat_est['high'] & self.band_ratio['low'] & self.others_info['yes'], self.container_loc['edge']))
        self.rules.append(ctrl.Rule(self.parr_est['low'] & self.lat_est['high'] & self.band_ratio['medium'] & self.others_info['no'], self.container_loc['end']))
        self.rules.append(ctrl.Rule(self.parr_est['low'] & self.lat_est['high'] & self.band_ratio['medium'] & self.others_info['yes'], self.container_loc['edge']))
        self.rules.append(ctrl.Rule(self.parr_est['low'] & self.lat_est['high'] & self.band_ratio['high'] & self.others_info['no'], self.container_loc['end']))
        self.rules.append(ctrl.Rule(self.parr_est['low'] & self.lat_est['high'] & self.band_ratio['high'] & self.others_info['yes'], self.container_loc['edge']))

        self.rules.append(ctrl.Rule(self.parr_est['medium'] & self.lat_est['low'] & self.band_ratio['low'] & self.others_info['no'], self.container_loc['end']))
        self.rules.append(ctrl.Rule(self.parr_est['medium'] & self.lat_est['low'] & self.band_ratio['low'] & self.others_info['yes'], self.container_loc['edge']))
        self.rules.append(ctrl.Rule(self.parr_est['medium'] & self.lat_est['low'] & self.band_ratio['medium'] & self.others_info['no'], self.container_loc['edge']))
        self.rules.append(ctrl.Rule(self.parr_est['medium'] & self.lat_est['low'] & self.band_ratio['medium'] & self.others_info['yes'], self.container_loc['edge']))
        self.rules.append(ctrl.Rule(self.parr_est['medium'] & self.lat_est['low'] & self.band_ratio['high'] & self.others_info['no'], self.container_loc['edge']))
        self.rules.append(ctrl.Rule(self.parr_est['medium'] & self.lat_est['low'] & self.band_ratio['high'] & self.others_info['yes'], self.container_loc['edge']))

        self.rules.append(ctrl.Rule(self.parr_est['medium'] & self.lat_est['medium'] & self.band_ratio['low'] & self.others_info['no'], self.container_loc['end']))
        self.rules.append(ctrl.Rule(self.parr_est['medium'] & self.lat_est['medium'] & self.band_ratio['low'] & self.others_info['yes'], self.container_loc['edge']))
        self.rules.append(ctrl.Rule(self.parr_est['medium'] & self.lat_est['medium'] & self.band_ratio['medium'] & self.others_info['no'], self.container_loc['edge']))
        self.rules.append(ctrl.Rule(self.parr_est['medium'] & self.lat_est['medium'] & self.band_ratio['medium'] & self.others_info['yes'], self.container_loc['edge']))
        self.rules.append(ctrl.Rule(self.parr_est['medium'] & self.lat_est['medium'] & self.band_ratio['high'] & self.others_info['no'], self.container_loc['edge']))
        self.rules.append(ctrl.Rule(self.parr_est['medium'] & self.lat_est['medium'] & self.band_ratio['high'] & self.others_info['yes'], self.container_loc['edge']))

        self.rules.append(ctrl.Rule(self.parr_est['medium'] & self.lat_est['high'] & self.band_ratio['low'] & self.others_info['no'], self.container_loc['end']))
        self.rules.append(ctrl.Rule(self.parr_est['medium'] & self.lat_est['high'] & self.band_ratio['low'] & self.others_info['yes'], self.container_loc['edge']))
        self.rules.append(ctrl.Rule(self.parr_est['medium'] & self.lat_est['high'] & self.band_ratio['medium'] & self.others_info['no'], self.container_loc['end']))
        self.rules.append(ctrl.Rule(self.parr_est['medium'] & self.lat_est['high'] & self.band_ratio['medium'] & self.others_info['yes'], self.container_loc['edge']))
        self.rules.append(ctrl.Rule(self.parr_est['medium'] & self.lat_est['high'] & self.band_ratio['high'] & self.others_info['no'], self.container_loc['end']))
        self.rules.append(ctrl.Rule(self.parr_est['medium'] & self.lat_est['high'] & self.band_ratio['high'] & self.others_info['yes'], self.container_loc['edge']))

        self.rules.append(ctrl.Rule(self.parr_est['high'] & self.lat_est['low'] & self.band_ratio['low'] & self.others_info['no'], self.container_loc['cloud']))
        self.rules.append(ctrl.Rule(self.parr_est['high'] & self.lat_est['low'] & self.band_ratio['low'] & self.others_info['yes'], self.container_loc['cloud']))
        self.rules.append(ctrl.Rule(self.parr_est['high'] & self.lat_est['low'] & self.band_ratio['medium'] & self.others_info['no'], self.container_loc['cloud']))
        self.rules.append(ctrl.Rule(self.parr_est['high'] & self.lat_est['low'] & self.band_ratio['medium'] & self.others_info['yes'], self.container_loc['cloud']))
        self.rules.append(ctrl.Rule(self.parr_est['high'] & self.lat_est['low'] & self.band_ratio['high'] & self.others_info['no'], self.container_loc['cloud']))
        self.rules.append(ctrl.Rule(self.parr_est['high'] & self.lat_est['low'] & self.band_ratio['high'] & self.others_info['yes'], self.container_loc['cloud']))

        self.rules.append(ctrl.Rule(self.parr_est['high'] & self.lat_est['medium'] & self.band_ratio['low'] & self.others_info['no'], self.container_loc['cloud']))
        self.rules.append(ctrl.Rule(self.parr_est['high'] & self.lat_est['medium'] & self.band_ratio['low'] & self.others_info['yes'], self.container_loc['cloud']))
        self.rules.append(ctrl.Rule(self.parr_est['high'] & self.lat_est['medium'] & self.band_ratio['medium'] & self.others_info['no'], self.container_loc['cloud']))
        self.rules.append(ctrl.Rule(self.parr_est['high'] & self.lat_est['medium'] & self.band_ratio['medium'] & self.others_info['yes'], self.container_loc['cloud']))
        self.rules.append(ctrl.Rule(self.parr_est['high'] & self.lat_est['medium'] & self.band_ratio['high'] & self.others_info['no'], self.container_loc['cloud']))
        self.rules.append(ctrl.Rule(self.parr_est['high'] & self.lat_est['medium'] & self.band_ratio['high'] & self.others_info['yes'], self.container_loc['cloud']))

        self.rules.append(ctrl.Rule(self.parr_est['high'] & self.lat_est['high'] & self.band_ratio['low'] & self.others_info['no'], self.container_loc['end']))
        self.rules.append(ctrl.Rule(self.parr_est['high'] & self.lat_est['high'] & self.band_ratio['low'] & self.others_info['yes'], self.container_loc['edge']))
        self.rules.append(ctrl.Rule(self.parr_est['high'] & self.lat_est['high'] & self.band_ratio['medium'] & self.others_info['no'], self.container_loc['end']))
        self.rules.append(ctrl.Rule(self.parr_est['high'] & self.lat_est['high'] & self.band_ratio['medium'] & self.others_info['yes'], self.container_loc['edge']))
        self.rules.append(ctrl.Rule(self.parr_est['high'] & self.lat_est['high'] & self.band_ratio['high'] & self.others_info['no'], self.container_loc['end']))
        self.rules.append(ctrl.Rule(self.parr_est['high'] & self.lat_est['high'] & self.band_ratio['high'] & self.others_info['yes'], self.container_loc['edge']))

        self.gen_ctrl_sys()
    def gen_ctrl_sys(self):
        # Create the control system
        self.cont_ctrl = ctrl.ControlSystem(self.rules)
        # Create the simulation for the control system
        self.cont_ctrl_sim = ctrl.ControlSystemSimulation(self.cont_ctrl)
    def calculate_parr_out(self,speedup_in_edge,speedup_in,run_mag_in,latency,latency_tol,throughput,bandwidth,others_info):
        lat_est = latency/1000.0
        parr_est = self.parr_est_block.calculate_parr_out(speedup_in,run_mag_in)
        #print "Parr Effects: ", parr_est, speedup_in, run_mag_in
        
        # pass into large main fuzzy block
        self.cont_ctrl_sim.input['parr_est'] = parr_est
        self.cont_ctrl_sim.input['lat_est'] = lat_est
        self.cont_ctrl_sim.input['band_ratio'] = throughput/bandwidth
        self.cont_ctrl_sim.input['others_info'] = others_info
        
        # Calculate the location
        self.cont_ctrl_sim.compute()
        if self.cont_ctrl_sim.output['container_loc'] < 0.66:
          parr_est_edge = self.parr_est_block.calculate_parr_out(speedup_in_edge,run_mag_in)
          #print parr_est_edge
          if parr_est_edge > 0.45:
            return 0.5
          else:
            return 0.2
        return self.cont_ctrl_sim.output['container_loc']

cont_est = ContainerEstimator()

#Config 1
speedup = [1.42,1.44,1.55,1.97,1.22,1.89,1.08,1.87,1.01,1.77,1.18,1.15,1.78,1.51, 1.85]
run_mag = [1511.66,2176.61,2554.14,3574.08,4593.05,208.48,3617.33,2654.28,669.15,3744.02,3624.67,2668.70,4828.75,40.23,1807.69,228]
latency = [2460.97,377.78,2424.44,1941.70,2912.20,1295.94,2639.76,3205.62,1805.62,362.26,358.43,2520.15,1012.62,2619.50,836.69,1869]
throughput = [1.66,5.66,4.23,9.19,3.28,7.04,5.48,7.58,4.94,6.36,5.04,3.30,8.55,7.73,2.08, 2.79]
bandwidth = [2.00,6.40,4.33,9.78,3.65,8.57,5.51,8.95,5.97,7.07,5.71,4.11,8.59,8.96,2.43, 6.41]
others_info = [0.00,1.00,0.00,1.00,0.00,1.00,1.00,1.00,0.00,1.00,1.00,1.00,0.00,0.00,1.00, 0.00]


latency_tol = 0
count = 1
for i in range(len(speedup)):
  location = cont_est.calculate_parr_out(1,speedup[i]*500.0,run_mag[i],latency[i],latency_tol,throughput[i],bandwidth[i],others_info[i])
  #print "Output of model: ", location # 0-0.33 place on end device, 0.33-0.66 place on edge, 0.66-1.0 place on cloud
  if location < 0.33:
     print count, "Place App on End Device"
  elif location <0.66:
     print count ,"Place App on Edge"
  else:
     print count, "Place App on Cloud"
  count += 1

# Config 2
speedup = [1.22, 1.22, 1.29, 1.29, 1.65, 1.65, 1.10, 1.10, 1.59, 1.59, 1.05, 1.05, 1.21, 1.21, 1.52, 1.52, 1.96, 1.96, 1.87, 1.87, 
           1.31, 1.31, 1.43, 1.43, 1.73, 1.73, 1.86, 1.86, 1.64, 1.64, 1.29, 1.29, 1.86, 1.86, 1.25, 1.25, 1.04, 1.04, 1.46, 1.46, 
           1.73, 1.73, 1.94, 1.94, 1.38, 1.38, 1.55, 1.55, 1.41, 1.41]

run_mag = [228.01, 228.01, 339.50, 339.50, 909.2, 909.2, 690.66, 690.66, 4079.19, 4079.19, 108, 108, 4295, 4295, 1411, 1411, 1100, 1100, 929, 929,
           3946, 3946, 4340, 4340, 1987, 1987, 3816, 3816, 818, 818, 4934, 4934, 4778, 4778, 1301, 1301, 3164, 3164, 1387, 1387, 
           715, 715, 2909, 2909, 3514, 3514, 610, 610, 1436, 1436]

latency = [1869.49, 1869.49, 1891.76, 1891.76, 1816.36, 1816.36, 2583.75, 2583.75, 2993.14, 2993.14, 1167, 1167, 1745, 1745, 3140, 3140, 2398, 2398,
           2046, 2046, 1858, 1858, 2743, 2743, 1983, 1983, 1154, 1154, 1442, 1442, 3174, 3174, 1418, 1418, 1649, 1649, 2640, 2640,
           1225, 1225, 2104, 2104, 1692, 1692, 2879, 2879, 2693, 2693, 466, 466]

throughput = [2.79, 2.79, 1.69, 1.69, 4.38, 4.38, 1.72, 1.72, 3.69, 3.69, 3.27, 3.27, 2.24, 2.24, 3.43, 3.43, 4.36, 4.36, 1.87, 1.87, 3.97, 3.97,
              3.46, 3.46, 1.43, 1.43, 1.15, 1.15, 3.62, 3.62, 3.43, 3.43, 3.05, 3.05, 2.58, 2.58, 1.1, 1.1, 1.86, 1.86, 4.62, 4.62,
              1.64, 1.64, 4.43, 4.43, 3.94, 3.94, 3.7, 3.7]

bandwidth =[6.41, 6.41, 3.53, 3.53, 9.03, 9.03, 3.98, 3.98, 9.13, 9.13, 7.77, 7.77, 5.36, 5.36, 8.12, 8.12, 10, 10, 4.23, 4.23, 8.15, 8.15,
            7.88, 7.88, 3.0, 3.0, 2.59, 2.59, 7.30, 7.30, 8.16, 8.16, 6.44, 6.44, 5.29, 5.29, 2.74, 2.74, 3.85, 3.85,
            9.62, 9.62, 3.54, 3.54, 9.55, 9.55, 8.56, 8.56, 8.31, 8.31]

others_info=[0.0, 0.0, 1.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0, 1.0, 0.0, 0.0, 1.0, 1.0, 1.0, 0.0,
             1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 0.0,
             1.0, 1.0]

latency_tol = 0
count = 16
for i in range(len(speedup)):
  location = cont_est.calculate_parr_out(1,speedup[i]*500.0,run_mag[i],latency[i],latency_tol,throughput[i],bandwidth[i],others_info[i])
  #print "Output of model: ", location # 0-0.33 place on end device, 0.33-0.66 place on edge, 0.66-1.0 place on cloud
  if location < 0.33:
     print count, "Place App on End Device"
  elif location <0.66:
     print count ,"Place App on Edge"
  else:
     print count, "Place App on Cloud"
  if i%2 == 1:
    count += 1

# Config 3
speedup = [1.22, 1.22, 1.29, 1.29, 1.65, 1.65, 1.10, 1.10, 1.59, 1.59, 1.05, 1.05, 1.21, 1.21, 1.52, 1.52, 1.96, 1.96, 1.87, 1.87, 
           1.31, 1.31, 1.43, 1.43, 1.73, 1.73, 1.86, 1.86, 1.64, 1.64, 1.29, 1.29, 1.86, 1.86, 1.25, 1.25, 1.04, 1.04, 1.46, 1.46, 
           1.73, 1.73, 1.94, 1.94, 1.38, 1.38, 1.55, 1.55, 1.41, 1.41]

run_mag = [228.01, 228.01, 339.50, 339.50, 909.2, 909.2, 690.66, 690.66, 4079.19, 4079.19, 108, 108, 4295, 4295, 1411, 1411, 1100, 1100, 929, 929,
           3946, 3946, 4340, 4340, 1987, 1987, 3816, 3816, 818, 818, 4934, 4934, 4778, 4778, 1301, 1301, 3164, 3164, 1387, 1387, 
           715, 715, 2909, 2909, 3514, 3514, 610, 610, 1436, 1436]

latency = [1869.49, 1869.49, 1891.76, 1891.76, 1816.36, 1816.36, 2583.75, 2583.75, 2993.14, 2993.14, 1167, 1167, 1745, 1745, 3140, 3140, 2398, 2398,
           2046, 2046, 1858, 1858, 2743, 2743, 1983, 1983, 1154, 1154, 1442, 1442, 3174, 3174, 1418, 1418, 1649, 1649, 2640, 2640,
           1225, 1225, 2104, 2104, 1692, 1692, 2879, 2879, 2693, 2693, 466, 466]

throughput = [2.79, 2.79, 1.69, 1.69, 4.38, 4.38, 1.72, 1.72, 3.69, 3.69, 3.27, 3.27, 2.24, 2.24, 3.43, 3.43, 4.36, 4.36, 1.87, 1.87, 3.97, 3.97,
              3.46, 3.46, 1.43, 1.43, 1.15, 1.15, 3.62, 3.62, 3.43, 3.43, 3.05, 3.05, 2.58, 2.58, 1.1, 1.1, 1.86, 1.86, 4.62, 4.62,
              1.64, 1.64, 4.43, 4.43, 3.94, 3.94, 3.7, 3.7]

bandwidth =[6.41, 6.41, 3.53, 3.53, 9.03, 9.03, 3.98, 3.98, 9.13, 9.13, 7.77, 7.77, 5.36, 5.36, 8.12, 8.12, 10, 10, 4.23, 4.23, 8.15, 8.15,
            7.88, 7.88, 3.0, 3.0, 2.59, 2.59, 7.30, 7.30, 8.16, 8.16, 6.44, 6.44, 5.29, 5.29, 2.74, 2.74, 3.85, 3.85,
            9.62, 9.62, 3.54, 3.54, 9.55, 9.55, 8.56, 8.56, 8.31, 8.31]

others_info=[0.0, 0.0, 1.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0, 1.0, 0.0, 0.0, 1.0, 1.0, 1.0, 0.0,
             1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 0.0,
             1.0, 1.0]

latency_tol = 0
count = 16
for i in range(len(speedup)):
  location = cont_est.calculate_parr_out(10,speedup[i]*500.0,run_mag[i],latency[i],latency_tol,throughput[i],bandwidth[i],others_info[i])
  #print "Output of model: ", location # 0-0.33 place on end device, 0.33-0.66 place on edge, 0.66-1.0 place on cloud
  if location < 0.33:
     print count, "Place App on End Device"
  elif location <0.66:
     print count ,"Place App on Edge"
  else:
     print count, "Place App on Cloud"
  if i%2 == 1:
    count += 1

#Config 4
speedup = [3.26, 4.37, 2.04, 8.51, 9.90, 8.05, 2.02, 1.16, 3.71, 5.45, 7.08, 8.41, 8.62, 4.78, 1.84,
           9.86, 1.79, 4.29, 9.32, 3.71]
edge_speedup = [1.09, 2.90, 2.22, 1.21, 2.10, 2.27, 2.95, 2.78, 1.49, 1.46, 1.09, 1.05, 2.12, 1.73,
                2.94, 1.67, 1.46, 1.90, 1.32, 1.37]
run_mag = [116.42, 156.02, 327.14, 359.31, 444.47, 313.08, 707.61, 792.03, 683.28, 377, 284, 98,
           585, 8.61, 531, 354, 565, 571, 573, 566]
latency = [676.82, 731.99, 133.39, 744.64, 281.45, 249.04, 728.73, 284.86, 926.34, 255, 343, 210,
          454, 184, 483, 673, 411, 496, 866, 323]
throughput = [1.42, 1.06, 3.37, 2.98, 1.24, 7.56, 3.85, 1.43, 5.18, 5.15, 6.79, 4.31, 2.58, 5.96,
             1.13, 2.90, 2.45, 0.75, 0.75, 2.92]
bandwidth = [2.35, 6.79, 3.92, 4.88, 2.62, 8.06, 4.81, 4.39, 9.13, 5.17, 7.15, 6.95, 4.82, 6.15,
             3.94, 3.57, 4.49, 2.60, 2.67, 7.33]
others_info = [0, 1, 1, 0, 0, 0, 1, 0, 1, 1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0]

latency_tol = 0
count = 1
for i in range(len(speedup)):
  location = cont_est.calculate_parr_out(edge_speedup[i],speedup[i],run_mag[i],latency[i],latency_tol,throughput[i],bandwidth[i],others_info[i])
  #print "Output of model: ", location # 0-0.33 place on end device, 0.33-0.66 place on edge, 0.66-1.0 place on cloud
  if location < 0.33:
     print count, "Place App on End Device"
  elif location <0.66:
     print count ,"Place App on Edge"
  else:
     print count, "Place App on Cloud"
  count += 1

#Config 4
speedup = [3.26, 4.37, 2.04, 8.51, 9.90, 8.05, 2.02, 1.16, 3.71, 5.45, 7.08, 8.41, 8.62, 4.78, 1.84,
           9.86, 1.79, 4.29, 9.32, 3.71]
edge_speedup = [1.09, 2.90, 2.22, 1.21, 2.10, 2.27, 2.95, 2.78, 1.49, 1.46, 1.09, 1.05, 2.12, 1.73,
                2.94, 1.67, 1.46, 1.90, 1.32, 1.37]
run_mag = [116.42, 156.02, 327.14, 359.31, 444.47, 313.08, 707.61, 792.03, 683.28, 377, 284, 98,
           585, 8.61, 531, 354, 565, 571, 573, 566]
latency = [676.82, 731.99, 133.39, 744.64, 281.45, 249.04, 728.73, 284.86, 926.34, 255, 343, 210,
          454, 184, 483, 673, 411, 496, 866, 323]
throughput = [1.42, 1.06, 3.37, 2.98, 1.24, 7.56, 3.85, 1.43, 5.18, 5.15, 6.79, 4.31, 2.58, 5.96,
             1.13, 2.90, 2.45, 0.75, 0.75, 2.92]
bandwidth = [2.35, 6.79, 3.92, 4.88, 2.62, 8.06, 4.81, 4.39, 9.13, 5.17, 7.15, 6.95, 4.82, 6.15,
             3.94, 3.57, 4.49, 2.60, 2.67, 7.33]
others_info = [0, 1, 1, 0, 0, 0, 1, 0, 1, 1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0]



speedup = [8.42,1.30,5.99,4.41,2.97,2.39,5.91,3.33,3.67,9.35,2.67,1.96,6.78,2.82,6.12,3.80,9.27,1.43,5.51,
           5.70,4.20,3.48,3.31,1.41,6.58,2.82,6.91,6.83,5.50,2.38,2.81,8.97,6.46,7.47,3.06,2.93]
edge_speedup = [1.36,1.98,1.79,2.13,1.06,1.27,2.72,1.09,2.62,2.74,1.77,2.37,2.08,2.57,1.13,2.64,
                2.28,2.36,1.94,2.40,1.68,2.28,2.37,1.74,2.02,1.41,2.91,2.01,1.51,1.32,1.66,2.58,2.32,2.21,1.38,2.82]
run_mag = [9649.26,6314.15,1530.39,4570.20,3033.76,1944.50,599.98,6107.77,5613.49,3168.33,9165.58,
           4126.15,4929.89,2488.60,6796.92,1103.13,873.20,9652.97,8202.78,9080.72,8374.65,4781.14,
           8273.67,9901.10,2735.07,2274.27,2407.45,6999.91,5641.85,1860.78,3330.79,3.54,5359.19,
           4507.66,5329.83,7068.79]
latency = [877.33,846.09,48.13,595.59,287.13,362.69,685.89,582.03,350.25,584.63,831.90,534.96,
           511.90,860.54,888.11,334.75,753.71,798.70,500.78,269.87,933.11,623.90,663.64,242.32,
           298.24,152.64,970.88,528.34,258.10,985.49,296.50,424.73,307.24,689.86,886.36,817.24]
throughput = [1.42,1.06,3.37,2.98,1.24,7.56,3.85,1.43,5.18,5.15,6.79,4.31,2.58,5.96,1.13,2.90,
              2.45,0.75,0.75,2.92,0.02,1.54,3.10,1.74,0.55,1.87,1.80,0.86,2.11,1.37,2.83,2.91,
              1.48,3.74,5.14,3.42,2.45,3.73,1.03,5.07,0.55,7.89,2.93,0.92,3.78,5.34,2.42,6.55,
              0.04,2.47,1.99,4.99,6.40,2.11,6.74,1.09]
bandwidth = [2.35,6.79,3.92,4.88,2.62,8.06,4.81,4.39,9.13,5.17,7.15,6.95,4.82,6.15,3.94,3.57,
             4.49,2.60,2.67,7.33,6.00,5.29,6.21,5.60,3.38,7.43,4.65,2.90,8.32,9.24,3.59,4.95,
             6.88,4.62,9.44,3.55,3.11,8.40,3.19,7.40,9.31,8.22,8.22,7.03,7.23,8.04,2.78,9.17,
             2.78,9.24,2.75,5.83,9.70,5.39,7.75,9.23]
others_info = [0,0,0,1,0,0,1,1,0,1,0,0,1,0,1,1,0,1,0,0,1,1,1,1,0,1,1,1,0,1,0,1,0,0,1,0]


latency_tol = 0
count = 1
for i in range(len(speedup)):
  location = cont_est.calculate_parr_out(edge_speedup[i],speedup[i],run_mag[i]*10,latency[i],latency_tol,throughput[i],bandwidth[i],others_info[i])
  #print "Output of model: ", location # 0-0.33 place on end device, 0.33-0.66 place on edge, 0.66-1.0 place on cloud
  if location < 0.33:
     print count, "Place App on End Device"
  elif location <0.66:
     print count ,"Place App on Edge"
  else:
     print count, "Place App on Cloud"
  count += 1

from google.colab import drive
drive.mount('/content/gdrive')
for i in range(100):
  speedup = random.uniform(0,2) # percent of code that can parralized 
  run_mag = random.uniform(0,5000) # runtime of algorithm in ms
  latency = random.uniform(0,500) # latency of network in ms
  latency_tol = random.uniform(0,1) # how tolerant to latency is algorithm (0-1)
  throughput = random.uniform(0,1000) # throughput in mbps
  bandwidth = random.uniform(0,1000) # bandwidth in mbps
  others_info = random.choice([0,1]) # requires info from other nodes ()0 or 1)
  print "Percent Parr: ", speedup
  print "Runtime Mag: ", run_mag, "ms"
  print "Latency: ", latency, "ms"
  print "Latency Tol: ", latency_tol
  print "Throughput: ", throughput, "mbps"
  print "Bandwidth: ", bandwidth, "mbps"
  print "Req Others Info: ", others_info
  expert_out = raw_input("Should App go on Cloud(c), Edge(e), or End Device(d)")
  location = cont_est.calculate_parr_out(speedup,run_mag,latency,latency_tol,throughput,bandwidth,others_info)
  print "Output of model: ", location # 0-0.33 place on end device, 0.33-0.66 place on edge, 0.66-1.0 place on cloud
  if location < 0.33:
    location_out = 'd'
  elif location <0.66:
    location_out = 'e'
  else:
    location_out = 'c'
  if location_out == expert_out:
    print "Fuzzy App Placer was Correct"
    with open('/content/gdrive/My Drive/fuzzy_app_placer_results.txt', 'a') as f:
      f.write("Percent Parr: "+ str(speedup) + "\n")
      f.write("Runtime Mag: "+ str(run_mag) + "ms\n")
      f.write("Latency: "+ str(latency) + "ms\n")
      f.write("Latency Tol: "+ str(latency_tol) + "\n")
      f.write("Throughput: "+ str(throughput) + "mbps\n")
      f.write("Bandwidth: "+ str(bandwidth)+ "mbps\n")
      f.write("Req Others Info: "+ str(others_info) + "\n")
      f.write("Expert: "+ str(expert_out) + "\n")
      f.write("Fuzzy App Placer: "+ str(location_out) + "\n")
      f.write("Correct")
      f.write("____________________________________________________" + "\n")
  else:
    print "Fuzzy App Placer was Wrong Expert: ", expert_out, " Fuzzy App Placer: ", location_out
    with open('/content/gdrive/My Drive/fuzzy_app_placer_results.txt', 'a') as f:
      f.write("Percent Parr: "+ str(speedup) + "\n")
      f.write("Runtime Mag: "+ str(run_mag) + "ms\n")
      f.write("Latency: "+ str(latency) + "ms\n")
      f.write("Latency Tol: "+ str(latency_tol) + "\n")
      f.write("Throughput: "+ str(throughput) + "mbps\n")
      f.write("Bandwidth: "+ str(bandwidth)+ "mbps\n")
      f.write("Req Others Info: "+ str(others_info) + "\n")
      f.write("Expert: "+ str(expert_out) + "\n")
      f.write("Fuzzy App Placer: "+ str(location_out) + "\n")
      f.write("Wrong")
      f.write("____________________________________________________" + "\n")
  print "__________________________________________________________"

