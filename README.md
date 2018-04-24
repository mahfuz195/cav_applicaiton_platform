# Connected Autonomous Vehcile Application Development Platform
---

This code repository is the sample application developmenet for CAV. 

1. Each vehicle will generate the data (Basic Safety Message(BSM)) at 10 Hz
2. Each vehcile withing its communcation range will receive the data 
3. After receiving the data an applicaiton will process the data and will produce an output

### Related Files:
This repo contains following files:

1. VehcileGeoData.csv : comma separated file which contains the trace of each vehcile locaiton, timestamp, and speed information.
2. Vehicle_1.py : Is the target vehcile where we want to develop an application.
3. Vehicle_2.py : A vehcile who is broadcasting its own Basic Safety Messages at 10 Hz 

### BSM data format:

we are using a modified BSM message in JSON format in this example:
```
{
  'carid': 2.0, 
  'seq': 166, 
  'timestamp': '1524604110368', 
  'longitude': -82.84551, 
  'latitude': 34.676059, 
  'speed': 20.073232
}
```


### User guide:

In this example vehicle 1 is the target applicaiton development vehicle. and it is collecting the data from other vehicles.

