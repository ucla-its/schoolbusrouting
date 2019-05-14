import pandas as pd
import sys 
from routing import start_routing
import constants
from setup import setup_data
from output import print_routes

def main():
   
    prefix = '/Users/cuhauwhung/Google Drive (cuhauwhung@g.ucla.edu)/Masters/Research/school_bus_project/Willy_Data/'
    
    # Store this information in a global variable
    single_school_clusters = setup_data(prefix+'stop_geocodes_fixed.csv', 
                                        prefix+'zipData.csv', 
                                        prefix+'school_geocodes_fixed.csv', 
                                        prefix+'totalPhoneBook.csv',
                                        prefix+'bell_times.csv')

    # Perform routing 
    start_routing(single_school_clusters)

    # Print routes 
    print_routes(single_school_clusters)
    return 
    
main()

