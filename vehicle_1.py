from socket import *
import threading
import time
from haversine import haversine
import json
import pandas as pd
import numpy as np

car_id = 0
############################################################################
class Vehicle():
    def __init__(self,_id):
	self.id   = _id
	self.long = 0 
	self.lati = 0
	self.speed= 0
	self.time = 0
    def get_location(self):
	return self.long, self.lati
    def set_location(self, lon, lat):
	self.long = lon
	self.lati = lat
    def set_speed(self, spd):
	self.speed = spd
    def get_speed(self):
	return self.speed
    def set_time(self,time):
	self.time = time
    def get_time():
	return time

my_vehicle = Vehicle(0)
print ('my vehicle id :' , my_vehicle.id)
############################################################################
def haversine_np(lon1, lat1, lon2, lat2, miles= False, meter = False, km = False, feet= False):
    
    lon1, lat1, lon2, lat2 = map(np.radians, [lon1, lat1, lon2, lat2])

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = np.sin(dlat/2.0)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2.0)**2

    c = 2 * np.arcsin(np.sqrt(a))
    
    dist = 6367 * c
	
    if (miles==True):
	dist = 0.621371 * dist
    elif (meter== True):
	dist = dist * 1000.0
    elif (feet== True):
	dist = dist * 3280.84
    return dist
#### Data set Loading starts ###############################################
full_data = 0
def ReadDataFromFile(file_name):
    global full_data
    df = pd.read_csv(file_name)
    full_data = df
    X = np.array(df)
    print (X)
    return X

def LoadPartialData(time):
    global full_data, my_vehicle
    ldata = full_data[full_data['time']>= time]
    ldata = ldata[ldata['id']==car_id]
    pdata = ldata[ldata['time']<(time+0.1)]
    return pdata

ReadDataFromFile('vehicleGeoData.csv')
##### Data set loading ends ################################################
class UpdateState(threading.Thread):
    end_time = 200
    steps = 0.0
    count = 0
    filename = 'vehicleGeoData.csv'

    def __init(self):
	#ReadDataFromFile(self.filename)
	threading.Thread.__init__(self)
    def run(self):
	global my_vehicle
        while(self.steps <= self.end_time):
          #print 'updating state thread'
          pd = LoadPartialData(self.steps)
	  
          for index,row in pd.iterrows():
	      if(int(row['id'])==my_vehicle.id):
		my_vehicle.set_speed(row['speed'])
		my_vehicle.set_location(row['x'],row['y'])
		#print ('locaiton of car, ', my_vehicle.id , ' is (',my_vehicle.get_location())

          time.sleep(0.1)
          self.steps+=0.1
          self.count+=1
#############################################################################
class BroadcastData(threading.Thread):
    end_time = 200
    steps = 0.0
    count = 0
    def __init__(self):
        threading.Thread.__init__(self)

    def run (self):
        #print ('car ', car_id, ' started broadcasting data!')
        while(self.steps <= self.end_time):
          #print 'start thread'
          pd = LoadPartialData(self.steps)

          for index,row in pd.iterrows():
            data = "{\"carid\":"+ str(row['id']) +",\"seq\":" + str(self.count) + ",\"timestamp\":\"" + str(int(time.time()*1000)) + "\",\"longitude\":"+ str(row['x'])+",\"latitude\":"+ str(row['y'])+",\"speed\":" + str(row['speed']) + "}"
            cs = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)
            cs.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
            cs.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
            cs.sendto(data,('',4499))

          time.sleep(0.1)
          self.steps+=0.1
          self.count+=1

#############################################################################
class ReceiveData(threading.Thread):
    dist_threshold = 2000 #ft
    def __init__(self):
        threading.Thread.__init__(self)
    def filter_data(self,data):
	global my_vehicle
	#print ('in filter data:', data)
	
	car2_id = data['carid']
	car2_long = data['longitude']
	car2_lati = data['latitude']

	#print ('car id:' , data['carid']), 
	#print ('logitude: ', data['longitude']),
	#print ('latitude: ', data['latitude']),
	#print ('speed:', data['speed'])
	#car2_location = (data['longitude'], data['latitude'])
	my_lon, my_lat = my_vehicle.get_location()
	#print ('before calculating the ')
	#print ('car 1 location (', my_lon, ',', my_lat , '), car 2 location (', car2_long , ', ' , car2_lati,')')
	dist = haversine_np(my_lon, my_lat, car2_long, car2_lati,feet= True)
	#print ('distance between',my_vehicle.id ,' and car ', car2_id , ' is :', dist , ' feet')
        if (dist <= self.dist_threshold):
            return data

    def run (self):
        cs = socket(AF_INET, SOCK_DGRAM)
        cs.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)
	cs.bind(('',4499))
        while(True):
            try:
                data, sender_addr= cs.recvfrom(1024)
		#print (data)
		jdata = json.loads(data)
		#print ('ldata car id = ' , jdata['carid'], ' speed :', jdata['speed'])
		
		#pdf = pd.DataFrame(ldata,index=[0])
		data = self.filter_data(jdata)		
		if(data != None):
		    print ('rx by car:', car_id ,':', data)
		    maintain_v_dict(data)
	    #except ValueError as err:
		#print ('json parse error!' , err)
	    except Exception as err:
		print (err)
		#cs.close()
		#break
		pass


v_dict = {}
def maintain_v_dict(data):
    car_id = data['carid']
    car_long = data['longitude']
    car_lati = data['latitude']
    car_spd = data['speed']
    car_time= data['timestamp']

    vehicle = Vehicle(car_id)
    vehicle.set_location(car_long,car_lati)
    vehicle.set_speed(car_spd)
    vehicle.set_time(car_time)

    v_dict[car_id] = vehicle

##############################################
#####		APPLICATIONS		######
##############################################

### Part 1 : Real time Vehicle probe data

class CVApplications(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    ############# APPLICAION 1 #############
    def CollisionAvoidance(self):
       global my_vehicle, v_dict

       for carid, car in v_dict.items():
           lon1 , lat1 = car.get_location()
           lon2 , lat2 = my_vehicle.get_location()

           dist = haversine_np(lon1, lat1,lon2,lat2, meter = True)
           if(dist<5):
               print ('Collision ahead!')
           else :
               print ('No Collision between car', my_vehicle.id, ' and car ', carid)



    #######################################
    def run(self):
	while True:
           self.CollisionAvoidance()
           time.sleep(0.1)
    ######################################


##############################################
#####			MAIN 		######
##############################################

def main():

    st = UpdateState()
    st.start()
    
    rx = ReceiveData()
    rx.start()


    app = CVApplications()
    app.start()

#    tx = BroadcastData()
#    tx.start()
##############################################
if __name__ == '__main__':
    main()

''' 
cs = socket(AF_INET, SOCK_DGRAM)
try:
    cs.bind(('127.0.0.255', 4499))
except:
    print 'failed to bind'
    cs.close()
    raise
    cs.blocking(0)
while (True):
    data = cs.recvfrom(1024) # <-- waiting forever
    print data
'''
