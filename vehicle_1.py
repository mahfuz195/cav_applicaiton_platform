from socket import *
import threading
import sys
import time
#from haversine import haversine
import json
import pandas as pd
import numpy as np

######### CVDeP Libs ###########
from libs.vehicle import Vehicle
from libs.haversine import haversine_np
from libs.data_io import ReadDataFromFile, LoadPartialData
################################
from kafka import KafkaProducer
producer = KafkaProducer(bootstrap_servers='130.127.198.22:9092')
TOPIC = 'cvbsm'
###########################################################################
filename = 'vehicle_data.csv'
car_id = 1
############################################################################
my_vehicle = Vehicle(car_id)
print ('my vehicle id :' , my_vehicle.id)
############################################################################
#### Data set Loading starts ###############################################
full_data = 0
#############################################
ReadDataFromFile(filename)

def save_data(data):
    with open('delay_result.txt','a+') as f:
        json.dump(data,f)

##### Data set loading ends ################################################
class UpdateState(threading.Thread):
    end_time = 200
    steps = 0.0
    count = 0
    filename = filename

    def __init(self):
        #ReadDataFromFile(self.filename)
        threading.Thread.__init__(self)
    def run(self):
        global my_vehicle
        while(self.steps <= self.end_time):
          #print 'updating state thread'
          pd = LoadPartialData(self.steps, my_vehicle.id)
          
          for index,row in pd.iterrows():
              if(int(row['id'])==my_vehicle.id):
                my_vehicle.set_speed(row['speed'])
                my_vehicle.set_location(row['x'],row['y'])
                #print ('locaiton of car, ', my_vehicle.id , ' is (',my_vehicle.get_location())
                data = "{\"carid\":"+ str(row['id']) +",\"seq\":" + str(self.count) + \
                        ",\"timestamp\":\"" + str(int(time.time()*1000)) + \
                        "\",\"longitude\":"+ str(row['x'])+ \
                        ",\"latitude\":"+ str(row['y'])+ \
                        ",\"speed\":" + str(row['speed']) + \
                        ",\"angle\":" + str(row['angle']) + \
                        ",\"type\":" + str(row['type']) + \
                        "}"
                producer.send(TOPIC,data)
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
	global my_vehicle
        #print ('car ', car_id, ' started broadcasting data!')
        while(self.steps <= self.end_time):
          #print 'start thread'
          pd = LoadPartialData(self.steps,my_vehicle.id)

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
        cs.bind(('192.168.2.1',4499))
        while(True):
            try:
                data, sender_addr= cs.recvfrom(1024)
                #print ('data rx size in bytes:' , sys.getsizeof(data))
                jdata = json.loads(data)
                #jdata = jdata.encode('utf-8')
                #print ('ldata car id = ' , jdata['carid'], ' speed :', jdata['speed'])
                
                #pdf = pd.DataFrame(ldata,index=[0])
                data = self.filter_data(jdata)		
                #print ('size of packet: ' , len(data.encode('utf-8')))
		if(data != None):
                    print ('rx by car:', car_id ,':', data)
                    data['rx_time'] = long(time.time() * 1000.0)
		    maintain_v_dict(data)
		    #print ('v_pack, rx_time, ' , data)
                    #ForwardCollision(data)
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
    vehicle.set_packet(data)

    #print ('v_pack: maintain_dict, ' , vehicle.get_packet())
    v_dict[car_id] = vehicle

##############################################
#####		APPLICATIONS		######
##############################################


### Part 1 : Real time Vehicle probe data
def ForwardCollision(data):
    global my_vehicle
    carid = data['carid']
    lon1 = data['longitude']
    lat1 = data['latitude']

    lon2, lat2 = my_vehicle.get_location()

    dist = haversine_np(lon1, lat1,lon2,lat2, meter = True)
    if(dist<5):
        print ('Collision ahead!')
    else :
        print ('No Collision between car', my_vehicle.id, ' and car ', carid)

        data['app_out'] = long(time.time() * 1000.0)
        
        print ('packet, app out, ' , data)


class CVApplications(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    ############# APPLICAION 1 #############
    def CollisionAvoidance(self):
       global my_vehicle, v_dict

       for carid, car in v_dict.items():
           lon1 , lat1 = car.get_location()
           lon2 , lat2 = my_vehicle.get_location()
	   
           v_packet = car.get_packet()
	   #print ('v_pack:' , v_packet)
           ## check if the packet is already been calculated or not
	   if (('app_out' in v_packet)==False):
               dist = haversine_np(lon1, lat1,lon2,lat2, meter = True)
               if(dist<5):
                   print ('Collision ahead!')
               else :
                   print ('No Collision between car', my_vehicle.id, ' and car ', carid)
               
               v_packet['app_out'] = long(time.time() * 1000.0)
	       
               t1 = long(v_packet['timestamp'])
               t2 = long(v_packet['app_out'])
               
               print ('app output time:' , (t2-t1) , ' ms')
               #print ('calculation delay:' , )
               car.set_packet(v_packet)
               save_data(v_packet)
	       print ('v_pack, app out, ' , v_packet)

    #######################################
    def run(self):
        while True:
           self.CollisionAvoidance()
           time.sleep(0.01)
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
