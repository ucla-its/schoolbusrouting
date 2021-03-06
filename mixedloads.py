import constants
from locations import Student, School

#Perform the mixed-load improvement procedure on a list of routes.
#This function does require it to be a list rather than a
#general Iterable, since it deletes while iterating.
def mixed_loads(route_list):
    #Iterate over all routes and check whether they
    #can be removed.
    i = 0
    for route in route_list:
            route.backup("mixed_loads")
    while i < len(route_list):
        modified_routes = set()
        route_to_delete = route_list[i]
        modified_routes.add(route_to_delete)
        stops = route_to_delete.stops
        succeeded = True
        for stop in stops:
            added = False
            for route_to_add_to in route_list:
                if route_to_add_to == route_to_delete:
                    continue
                if (route_to_add_to.e_no_h and stop.h > 0 and stop.e == 0 or
                    route_to_add_to.h_no_e and stop.e > 0 and stop.h == 0):
                    continue
                if route_to_add_to.insert_mincost(stop):
                    added = True
                    modified_routes.add(route_to_add_to)
                    break
            if not added:
                succeeded = False
                break
        if succeeded:
            del route_list[i]
            for route in modified_routes:
                route.backup("mixed_loads")
        else:
            for route in modified_routes:
                route.restore("mixed_loads")
            i += 1