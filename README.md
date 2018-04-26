# Connected Autonomous Vehcile Application Development Platform (CVDeP)
---

This code repository is the sample application developmenet for CAV. 

1. Each vehicle will generate the data (Basic Safety Message(BSM)) at 10 Hz
2. Each vehcile withing its communcation range will receive the data 
3. After receiving the data an applicaiton will process the data and will produce an output

### Related Files:
This repo contains following files:

1. VehcileGeoData.csv : comma separated file which contains the trace of each vehcile locaiton, timestamp, and speed information.
2. Vehicle_1.py : Is the target vehcile where we want to develop an application.
3. Vehicle_others.py : Other vehciles who are broadcasting its own Basic Safety Messages at 10 Hz 

### BSM data format:

we are using a modified BSM message in JSON format in this example:
```
{
  'carid': 2.0, 
  'seq': 166, 
  'timestamp': '1524604110368', 
  'longitude': -82.84551, 
  'latitude': 34.676059, 
  'speed': 20.073232,
  'type': 1,
  'angle': 250
}
```


### User guide:

In this example vehicle 1 is the target applicaiton development vehicle. and it is collecting the data from other vehicles.

### Target Application Development Procedure:
Given the hardware setup, we can develop an application in the target vehcile. For example, in this case it it vehicle_1.py.
Inside this scrip one can write the applicaiton in section tagged with "Application". As an example, collision detection application can be like this: 

```
##############################################
#####		APPLICATIONS		######
##############################################

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
    
    ### define your own application here ###
    
    ########################################

    #######################################
    def run(self):
	while True:
           self.CollisionAvoidance()
           ## put your application function here like collision avoidance
           time.sleep(0.1)
    ######################################
```
