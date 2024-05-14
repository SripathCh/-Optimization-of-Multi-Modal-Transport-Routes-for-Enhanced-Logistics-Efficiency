# TEAM MEMBER NAMES (GROUP - 9)
# SRIPATH CHERUKURI (G01395231)
# SATHWIK VEMULAPALLY (G01380860)

# importing all the required packages 
import sys
import copy
import pyomo.environ as pyo
from pyomo.environ import *
import json
# importing the transport analytical model
import transportAnalytical

# appending the system path to use dgalPy
sys.path.append("/Users/sripathcherukuri/Desktop/Group9_FinalProjectCode/solution/main.py")
dgal_path = "/Users/sripathcherukuri/Desktop/Group9_FinalProjectCode/lib/dgalPy.py"
spec = importlib.util.spec_from_file_location("dgal", dgal_path)

# loading the input json file from command line
input = json.loads(sys.stdin.read())
# calling the transportAnaltical model
answer = transportAnalytical.shipment_routes(input)
# writing the output to the file given in command line
sys.stdout.write(json.dumps(answer))

