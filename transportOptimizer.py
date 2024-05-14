# TEAM MEMBER NAMES (GROUP - 9)
# SRIPATH CHERUKURI (G01395231)
# SATHWIK VEMULAPALLY (G01380860)

# importing neccessary libraries
import sys
import json
import copy
import pyomo

# appending the lib folder to system ath for use of dgal
sys.path.append("./lib")

import dgalPy as dgal
import transportAnalytical

dgal.startDebug()

f = open("input_output/transport_input_var.json","r")
varInput = json.loads(f.read())

# defining constraints for optimization
def constraints(o):
    #reading from output o
    shipments = o["shipments"]
    # reading quantities of shipments
    qty1 = shipments["shipment1"]["quantity"]
    qty2 = shipments["shipment2"]["quantity"]
    qty3 = shipments["shipment3"]["quantity"]
    qty4 = shipments["shipment4"]["quantity"]
    qty5 = shipments["shipment5"]["quantity"]

    # Setting lower bounds 
    additional = [qty1 >= 1000, qty2 >= 1000, qty3 >= 1000, qty4 >= 1000, qty5 >= 1000]   
    # returning all constraints
    return (dgal.all([ shipments["shipment1"]["constraints"], shipments["shipment2"]["constraints"], shipments["shipment3"]["constraints"], shipments["shipment4"]["constraints"], shipments["shipment5"]["constraints"], additional]))

# using dgal.min function to optimize cost, time and emissions
optAnswer = dgal.min({
    "model": transportAnalytical.shipment_routes,
    "input": varInput,
    "obj": lambda o: sum(shipment["total_cost"] + 
                         shipment["total_time"] + 
                         shipment["total_emissions"] 
                         for shipment in o["shipments"].values()),
    "constraints": constraints,
    "options": {"problemType": "mip", "solver": "glpk", "debug": True}
})

optOutput = transportAnalytical.shipment_routes(optAnswer["solution"])

output = {
#    "input":input,
#    "varInput":varInput,
    "optAnswer": optAnswer,
    "optOutput": optOutput
}

# opening file handle to write optimal solution to file

f = open("answers/transportOutOpt.json","w")


# writing optimal solution to file
f.write(json.dumps(output))

