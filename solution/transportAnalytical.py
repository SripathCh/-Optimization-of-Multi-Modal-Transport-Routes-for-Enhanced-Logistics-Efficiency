# TEAM MEMBER NAMES (GROUP - 9)
# SRIPATH CHERUKURI (G01395231)
# SATHWIK VEMULAPALLY (G01380860)

# Importing all the required libraries that will be used in the program:
# itertools: We use itertools to find all the possible combinations of transport available for segments in a given route
# importlib.util: We use this library to set the dgal path to use in this program
 
import itertools
import importlib.util


# Loading the dgal module here

dgal_path = "/Users/sripathcherukuri/Desktop/Group9_FinalProjectCode/lib/dgalPy.py"
spec = importlib.util.spec_from_file_location("dgal", dgal_path)
dgal = importlib.util.module_from_spec(spec)
spec.loader.exec_module(dgal)

#------------------------------------------------------------------------------------------------
# Function to find details of the choosen transport mode. 
# Takes transport mode name and transport modes dictionary as input parameters
# Returns mode details

def find_mode_details(mode_name, transport_modes):
    for mode in transport_modes:
        if mode['mode'] == mode_name:
            return mode
    return None

#------------------------------------------------------------------------------------------------

# Function to calculate the cost for given weight and price per lb in transport mode

def calculate_cost(total_weight, mode_details, fromPlace, toPlace):
    return total_weight * mode_details["pplbFromTo"][fromPlace][toPlace]  

#------------------------------------------------------------------------------------------------
# Function to calculate the carbon emissions for given distance and transport mode
# Returns carbon emissions for distance in miles 
# Conversion: 1km = 0.621371 

def calculate_emissions(distance, mode_details):
    return distance * mode_details['emissions_kg_per_km'] * 0.621371  

#------------------------------------------------------------------------------------------------
# Function to calculate the time taken for travel for certain transport mode
# Returns time taken to cover distance in miles by a transport mode
# Conversion: 1km = 0.621371 

def calculate_time(distance, mode_details):
    return distance / mode_details['speed_km_per_hr'] * 0.621371

#------------------------------------------------------------------------------------------------
# Function to adjust the deadline based on premium flag.
# If premium flag is set to 1 or True it returns 36 hours - Generally one and half day for express shipping
# If premium flag is set to 0 or False we do not change deadline and return the default deadline specified in shipment

def calculate_adjusted_deadline(shipment):
    if shipment.get('premium', 0) == 1:
        return 36
    return shipment['deadline_hours']

#------------------------------------------------------------------------------------------------
# function to caluclate total weight for given qty_units in shipment

def calculate_total_weight(qty_units, weight_per_unit):
    return qty_units * weight_per_unit

#------------------------------------------------------------------------------------------------
# function to check the best combination found is the best one than previous one
# checks with score of previous combination

def checkBestCombination(best_combination, best_overall_score):
    checks = []
    if best_combination:
        # Check if the total cost of the current best combination is less than the best overall score
        better_cost_check = best_combination['total_cost'] < best_overall_score
        checks.append(better_cost_check)

    return checks

#------------------------------------------------------------------------------------------------
# Function to check weight constraint.
# Takes transport mode and shipment as input parameters
# Returns True if if shipment weight is less than or equal to selected transport mode
# False otherwise


def checkWeightConstraint(mode_details, shipment_weight):
    checks = []
    if mode_details:
        # Check if the weight is non-negative
        non_negative_check = shipment_weight >= 0
        checks.append(non_negative_check)
        
        # Check if the weight does not exceed the mode's capacity
        capacity_bound_check = shipment_weight <= mode_details['capacity']
        checks.append(capacity_bound_check)
        
    return dgal.all(checks)

#------------------------------------------------------------------------------------------------
# Function to check time constraint
# Takes total time and , adjusted time as input parameters
# Returns True if satisfies and False otherwise

def checkTimeConstraint(time, adj_deadline):
    return time<=adj_deadline

#------------------------------------------------------------------------------------------------
# function to check and compare the score of every possible combination.
# the best combination updates once everytime a combination with better combination is found
def checkScoreConstraint(current_score, best_score):
    # list to hold check results
    score_checks = []

    # if the current score is better than the best score
    better_score_check = current_score < best_score
    score_checks.append(better_score_check)

    return dgal.all(score_checks)

#------------------------------------------------------------------------------------------------
# Function to find and calcuate the metrics for all 
# possible transport combinations for a given route.
#------------------------------------------------------------------------------------------------
def shipment_routes(input):
    
    # loading all the inputs from the JSON files
    # shipments, transport modes, network
    # weight factors set for premium flag.
    
    shipments = input["shipments"]
    network = input["network"]
    transport_modes = input["transportation_modes"]
    # initializing the output dictionary
    results = {"shipments": {}}

    # for each shipment in shipments
    for shipment in shipments:
        # checking for adjusted deadline, adjusts if premium is present
        adjusted_deadline = calculate_adjusted_deadline(shipment)
        # best overall route set to None initially
        best_overall_route = None
        # best overall score set to max float value and we update it when we find smaller score
        best_overall_score = float('inf')
        total_weight = calculate_total_weight(shipment['qty_units'], shipment['weight_per_unit'])

        # for each route in network
        for route in network:
            # check if the origin and destination match with shipment
            if route['origin'] == shipment['origin'] and route['destination'] == shipment['destination']:
                # if yes then for each route present in shipment we find combinations of transports possible
                for route_option in route['routes']:
                    combinations = list(itertools.product(*(segment['available_modes'] for segment in route_option['segments'])))
                    # best transport combination set to None initially
                    best_combination = None
                    # best score for each combination set to max float value and will update it when we find better combo with min score
                    best_score = float('inf')
                    # for each transport combo in combinations
                    for combo in combinations:
                        # initializing cost, time and car emissions variables for each combo
                        combo_total_cost = 0
                        combo_total_time = 0
                        combo_total_emissions = 0
                        route_details = []
                        valid_route = True
                        # previous mode to keep track of previous mode to find if  there is a transport mode change
                        previous_mode = None
                        
                        # for each segment in a route and combo we calcluate the metrics
                        for segment, mode in zip(route_option['segments'], combo):
                            # getting mode details
                            mode_details = find_mode_details(mode, transport_modes)
                            weightConstraint = checkWeightConstraint(mode_details, total_weight)
                            # if we find mode details and weight costraints returns True
                            if mode_details and weightConstraint:
                                # finding individual cost, time and emissions for that transport
                                individual_cost = calculate_cost(total_weight, mode_details, segment['from'], segment['to'])
                                individual_time = calculate_time(segment['distance_miles'], mode_details)
                                individual_emissions = calculate_emissions(segment['distance_miles'], mode_details)
                                # if we find previous mode 
                                if previous_mode and previous_mode != mode:
                                    # we get the change over cost
                                    changeover_cost = mode_details["changeover_cost"].get(previous_mode, 0)
                                    # adding it to cost
                                    individual_cost += changeover_cost
                                
                                # adding it to total combo cost, time and carbon emissions
                                combo_total_cost += individual_cost
                                combo_total_time += individual_time
                                combo_total_emissions += individual_emissions
                                # updating previous mode to current mode
                                previous_mode = mode
                                # appending segment details to route details 
                                route_details.append({
                                    "from": segment["from"],
                                    "to": segment["to"],
                                    "mode": mode,
                                    "distance": segment['distance_miles'],
                                    "cost": individual_cost,
                                    "time": individual_time,
                                    "emissions": individual_emissions
                                })
                            # if the weight constraint fails or mode details are not found else executes
                            else:
                                # setting route flag to False indicating the transport mode is not viable and proceeds with next combo
                                valid_route = False
                                break
                        # If we have found a combo and if it meets the time constraint then we update the score
                        timeConstraint = checkTimeConstraint(combo_total_time, adjusted_deadline)
                        constraints = weightConstraint and timeConstraint        
                        if valid_route and timeConstraint:
                            # if we found a transport combo and time constrain is True
                            # if premium flag is there we use weight factors accordingly
                            score = (combo_total_cost * 0.0 + combo_total_time * 1.0 + combo_total_emissions * 0.0) if shipment["premium"] else (combo_total_cost * 0.3 + combo_total_time * 0.3 + combo_total_emissions * 0.3)
                            # update the score everytime we find a better score
                            if checkScoreConstraint(score,best_score):
                                best_score = score
                                # add metrics for the shipment when we find the best transport combo
                                best_combination = {
                                    "quantity": shipment["qty_units"],
                                    "route_id": route_option['route_id'],
                                    "total_cost": combo_total_cost,
                                    "total_time": combo_total_time,
                                    "total_emissions": combo_total_emissions,
                                    "constraints": constraints,
                                    "weight_constraints": weightConstraint,
                                    "timeConstraint": timeConstraint,
                                    "route_details": route_details
                                }
                # if we found best mode combo
                if checkBestCombination(best_combination, best_overall_score):
                    # checking if we have previous overall best score
                    best_overall_score = best_combination['total_cost']
                    best_overall_route = best_combination
        # we update the results to have details of more cost effective route
        if best_overall_route:
             results["shipments"][shipment['id']]=best_overall_route
    # return results
    return results

#------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------
# End of shipment routes function
