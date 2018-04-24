from socket import *
import threading
import time
import pandas as pd
import numpy as np

car_id = 2
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
class BroadcastData(threading.Thread):
    end_time = 200
    steps = 0.0
    count = 0 
    def __init__(self):
        threading.Thread.__init__(self)
    
    def run (self):
	print ('car ', car_id, ' started broadcasting data!')
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
    ReadDataFromFile('vehicleGeoData.csv')
#    rx = ReceiveData()
#    rx.start()


    tx = BroadcastData()
    tx.start()

if __name__ == '__main__':
    main()

