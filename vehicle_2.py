from socket import *
import threading
import time
import pandas as pd
import numpy as np

##########################
from kafka import KafkaProducer
producer = KafkaProducer(bootstrap_servers='130.127.198.22:9092')
TOPIC = 'cvbsm'

###########################################################################
filename = 'vehicle_data.csv'
car_id = 1

###########################################################################
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

my_vehicle = Vehicle(car_id)
print ('my vehicle id :' , my_vehicle.id)
############################################################################


#### Data set Loading starts ###############################################
full_data = 0
def ReadDataFromFile(file_name):
    global full_data
    df = pd.read_csv(file_name)
    full_data = df
    X = np.array(df)
    return X
def LoadPartialData(time):
    global full_data
    ldata = full_data[full_data['time']>= time]
    ldata = ldata[ldata['id']==car_id]
    pdata = ldata[ldata['time']<(time+0.1)]
    return pdata

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
          pd = LoadPartialData(self.steps)

          for index,row in pd.iterrows():
              if(int(row['id'])==my_vehicle.id):
                my_vehicle.set_speed(row['speed'])
                my_vehicle.set_location(row['x'],row['y'])
                print ('locaiton of car, ', my_vehicle.id , ' is (',my_vehicle.get_location())
                data = "{\"carid\":"+ str(row['id']) +",\"seq\":" + str(self.count) + ",\"timestamp\":\"" + str(int(time.time()*1000)) + "\",\"longitude\":"+ str(row['x'])+",\"latitude\":"+ str(row['y'])+",\"speed\":" + str(row['speed']) + "}"
                producer.send(TOPIC,data)
          time.sleep(0.1)
          self.steps+=0.1
          self.count+=1


##### Data set loading ends ################################################
class BroadcastData(threading.Thread):
    end_time = 200
    steps = 0.0
    count = 0 
    def __init__(self):
        threading.Thread.__init__(self)
    
    def run (self):
	global producer, TOPIC
        
	print ('car ', car_id, ' started broadcasting data!')
        while(self.steps <= self.end_time):
          #print 'start thread'
          pd = LoadPartialData(self.steps)

	  for index,row in pd.iterrows():
            data = "{\"carid\":"+ str(row['id']) +",\"seq\":" + str(self.count) + ",\"timestamp\":\"" + str(int(time.time()*1000)) + "\",\"longitude\":"+ str(row['x'])+",\"latitude\":"+ str(row['y'])+",\"speed\":" + str(row['speed']) + "}"

            #print (data)
	    #producer.send(TOPIC,data)
            cs = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)
            cs.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
            cs.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
            cs.sendto(data,('',4499))
                      
          time.sleep(0.1)
	  self.steps+=0.1
          self.count+=1

class ReceiveData(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
    def run (self):
        cs = socket(AF_INET, SOCK_DGRAM)
        cs.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)
	cs.bind(('',4499))
        while(True):
            try:
                data = cs.recvfrom(1024)
		print ('rx:', data)
	    except:
		cs.close()
		break
#### Read write from vehcile ends ############################################

def main():
    ReadDataFromFile(filename)
#    rx = ReceiveData()
#    rx.start()
    
    st = UpdateState()
    st.start()

    tx = BroadcastData()
    tx.start()

if __name__ == '__main__':
    main()

