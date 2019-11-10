import constants
from locations import Bus, School, Stop, Student 
import numpy as np
from utils import californiafy, timesecs

#Given an index and a dictionary from geocodes to indices,
#finds the index corresponding with the nearest geocode in
#Euclidean space. (Therefore, if a geocode is in the database,
#its index will be returned, as the distance is 0.) 
def fetch_ind(code_to_find, codes_inds_map):
    if code_to_find in codes_inds_map:
        return codes_inds_map[code_to_find]
    smallest_dist = 1000000
    smallest_dist_ind = -1
    (latitude_to_find, longitude_to_find) = code_to_find.split(";")
    latitude_to_find = float(latitude_to_find)
    longitude_to_find = float(longitude_to_find)
    nearest_code = None
    for code in codes_inds_map:
        (latitude, longitude) = code.split(";")
        latitude = float(latitude)
        longitude = float(longitude)
        dist = ((latitude-latitude_to_find)**2 +
                (longitude - longitude_to_find)**2)**.5
        if dist < smallest_dist:
            smallest_dist = dist
            smallest_dist_ind = codes_inds_map[code]
            nearest_code = code
    if constants.VERBOSE:
        print("Geocode " + code_to_find +
              " not in matrix of known travel times; using " +
              str(nearest_code))
    return smallest_dist_ind
        

#students_file: a format I am using for special ed students
#Columns are latitude, longitude, grade level, human-readable
#description of special ed types (not used), text description.
#all_geocodes: filename for list of all geocodes. gives map from geocode to ind
#geocoded_schools: file name for map from school to geocode
#returns a list of all students, a dict from schools to sets of
#students, and a dict from schools to indices in the travel time matrix.
#bell_sched: file name for which column 3 is cost center and
#column 4 is start time
#sped flags whether this run is for SP students or RG students.
def setup_students(students_filename, all_geocodes,
                   geocoded_schools, sped):
    
    schools = open(geocoded_schools, 'r')
    schools_codes_map = dict()  #maps schools to geocodes
    schools_students_map = dict()  #maps schools to sets of students
    schools_starttimes_map = dict() #maps schools to start times
    schools_endtimes_map = dict() #maps schools to end times
    schools_names_map = dict() #maps schools to their names
    schools_customtimes_map = dict() #maps schools to custom pickup/dropoff intervals
    schools.readline()  #get rid of header
    for cost_center in schools.readlines():
         fields = cost_center.split(",")
         if len(fields) < 6:
             continue
         schools_codes_map[fields[0]] = (fields[4].strip() + ";"
                                         + fields[5].strip())
         schools_students_map[fields[0]] = set()
         schools_names_map[fields[0]] = fields[1]
         schools_starttimes_map[fields[0]] = timesecs(fields[2])
         schools_endtimes_map[fields[0]] = timesecs(fields[3])
         if len(fields) == 10:
             schools_customtimes_map[fields[0]] = [-1, -1, -1, -1]
             for i in range(6, 10):
                 if fields[i].strip() != "":
                     schools_customtimes_map[fields[0]][i - 6] = timesecs(fields[i])
    schools.close()
    
    geocodes = open(all_geocodes, 'r')
    constants.GEOCODES = []
    codes_inds_map = dict()
    ind = 0
    for code in geocodes.readlines():
        constants.GEOCODES.append(code.strip())
        codes_inds_map[code.strip()] = ind
        ind += 1
    geocodes.close()
    
    schools_inds_map = dict()
    for school in schools_codes_map:
        schools_inds_map[school] = fetch_ind(schools_codes_map[school],
                                             codes_inds_map)
    
    students = []
    #Maintain a dictionary of school indices to schools so that
    #school objects can be tested for equality.
    ind_school_dict = dict()
    #Maintain a set of all School objects to return                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           
    all_schools = set()
    student_records = open(students_filename, 'r')
    student_records.readline()  #header
    ind = 0  #keeping track of row to associate with students
    for student_record in student_records.readlines():
        ind += 1
        fields = student_record.strip().split(",")
        school = fields[6].strip()
        stop_ind = fetch_ind(fields[1].strip() + ";" + fields[2].strip(),
                             codes_inds_map)
        school_ind = fetch_ind(schools_codes_map[school],
                               codes_inds_map)
        grade = fields[3].strip()
        stud_sped = (fields[5] == "SP")
        #Not the type of student we are currently routing
        if stud_sped != sped:
            continue
        age_type = 'Other'
        try:
            grade = int(grade)
        except:
            grade = -1
        if int(grade) in constants.GRADES_TYPE_MAP:
            age_type = constants.GRADES_TYPE_MAP[int(grade)]
        if age_type == 'Other':
            print(grade)
        if school_ind not in ind_school_dict:
            starttime = 8*60*60  #default to 8AM start
            endtime = 13*60*60  #default to 3PM finish
            #None of the 19xxxxx schools have times, so use the defaults
            if school in schools_starttimes_map:
                starttime = schools_starttimes_map[school]
                endtime = schools_endtimes_map[school]
                name = schools_names_map[school]
            else:
                if constants.VERBOSE:
                    print("No bell times given for " + school + ", using defaults")
            ind_school_dict[school_ind] = School(school_ind,
                                                 starttime,
                                                 endtime,
                                                 name)
            if school in schools_customtimes_map:
                customtimes = schools_customtimes_map[school]
                if customtimes[0] != -1:
                    ind_school_dict[school_ind].earliest_dropoff = customtimes[0]               
                if customtimes[1] != -1:
                    ind_school_dict[school_ind].latest_dropoff = customtimes[1]               
                if customtimes[2] != -1:
                    ind_school_dict[school_ind].earliest_pickup = customtimes[2]                  
                if customtimes[3] != -1:
                    ind_school_dict[school_ind].latest_pickup = customtimes[3]
            all_schools.add(ind_school_dict[school_ind])
        this_student = Student(stop_ind, ind_school_dict[school_ind],
                               age_type, fields, ind, sped)
        students.append(this_student)
        schools_students_map[school].add(this_student)
        needs = fields[4].split(";")
        #Add special needs
        for need in needs:
            #Splitting an empty string returns one empty string -
            #no needs in this case
            if len(need) == 0:
                continue
            if len(need) == 1:
                #Most types of needs do not require extra info
                assert (need in ["M", "W", "L", "A", "I", "F"]), ("Unknown need type"+str(need))
                this_student.add_need(need)
            else:
                #Custom max travel time does require extra info
                #Translate from minutes to seconds
                assert (need[0] == "T"), ("Unknown need type"+str(need))
                this_student.add_need(need[0], value = int(need[1:])*60/1.5)
    student_records.close()
    return students, schools_students_map, all_schools


def setup_map_data(mapdata_filename):
    constants.TRAVEL_TIMES = np.load(constants.FILENAMES[3])*constants.TT_MULT



#bus_capacities is an input csv file where the first
#column is bus ID and the second is capacity.
def setup_buses(bus_filename, sped):
    buses = []
    bus_file = open(bus_filename, 'r')
    bus_file.readline()  #header
    for bus_info in bus_file.readlines():
        fields = bus_info.split(",")
        cap = int(fields[1])
        lift = (fields[2] == 'Y')
        #Don't include wheelchair buses when routing non-special-ed
        if lift and not sped:
            continue
        #By default, assume no wheelchair capacity.
        min_wheel = 0
        max_wheel = 0
        if len(fields) == 5 and len(fields[3]) > 0 and len(fields[4]) > 0:
            min_wheel = int(fields[3])
            max_wheel = int(fields[4])
        bus = Bus(cap, min_wheel, max_wheel, lift)
        buses.append(bus)
    bus_file.close()
    buses = sorted(buses, key = lambda x:x.capacity)
    return buses

#Sets up the stops based on the output of setup_students
#Populates unrouted_stops in the Schools
#Note: students with different cost centers may go to the same
#physical location. The loop variable "cost_cent" represents the cost
#center number, whereas student.school is the school object in memory.
#As a result, this function is the one that will associate different
#cost centers at the same location together.
def setup_stops(schools_students_map):
    stops = set()
    ttind_stop_map = dict()
    for cost_cent in schools_students_map:
        for student in schools_students_map[cost_cent]:
            dict_key = student.tt_ind
            if student.school not in ttind_stop_map:
                ttind_stop_map[student.school] = dict()
            if dict_key not in ttind_stop_map[student.school]:
                new_stop = Stop(student.school)
                ttind_stop_map[student.school][dict_key] = new_stop
                stops.add(ttind_stop_map[student.school][dict_key])
                student.school.unrouted_stops.add(new_stop)
            ttind_stop_map[student.school][dict_key].add_student(student)
    return stops
                
#Sets up the map from unmodified capacities to modified capacities.
def setup_mod_caps(mod_caps_filename):
    constants.CAPACITY_MODIFIED_MAP = dict()
    modcaps_file = open(mod_caps_filename, 'r')
    modcaps_file.readline() #header
    for modcap in modcaps_file.readlines():
        fields = modcap.split(",")
        orig_cap = int(fields[0])
        resulting_caps = [int(fields[1]), int(fields[2]), int(fields[3])]
        constants.CAPACITY_MODIFIED_MAP[orig_cap] = resulting_caps
    #If we ever want to not worry about capacity, use virtual
    #buses of capacity 10000.
    constants.CAPACITY_MODIFIED_MAP[10000] = [10000, 10000, 10000]
    modcaps_file.close()
    
def setup_parameters(parameters_filename, sped):
    parameters_file = open(parameters_filename, 'r')
    parameters_file.readline() #header
    fields = parameters_file.readline().split(",")
    if sped:
        fields = parameters_file.readline().split(",")
    constants.MAX_TIME = 60*float(fields[1])/float(fields[2])
    constants.MSTT_WEIGHT = float(fields[3])
    constants.MINUTES_PER_SEGMENT = float(fields[4])/2
    constants.SLACK = float(fields[5])
    constants.MAX_SCHOOL_DIST = float(fields[6])*60
    parameters_file.close()
    
def setup_school_pairs(forbidden_pairs_filename, allowed_pairs_filename):
    constants.ALLOWED_SCHOOL_PAIRS = set()
    constants.FORBIDDEN_SCHOOL_PAIRS = set()
    if forbidden_pairs_filename != "":
        forbidden_file = open(forbidden_pairs_filename, 'r')
        for forbidden_pair in forbidden_file.readlines():
            fields = forbidden_pair.split(",")
            if len(fields) < 2:
                continue
            constants.FORBIDDEN_SCHOOL_PAIRS.add((fields[0], fields[1]))
            constants.FORBIDDEN_SCHOOL_PAIRS.add((fields[1], fields[0]))
        forbidden_file.close()
    if allowed_pairs_filename != "":
        allowed_file = open(allowed_pairs_filename, 'r')
        for allowed_pair in allowed_file.readlines():
            fields = allowed_pair.split(",")
            if len(fields) < 2:
                continue
            constants.ALLOWED_SCHOOL_PAIRS.add((fields[0], fields[1]))
            constants.ALLOWED_SCHOOL_PAIRS.add((fields[1], fields[0]))
        allowed_file.close()