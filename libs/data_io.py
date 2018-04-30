import json
import pandas as pd
import numpy as np

def ReadDataFromFile(file_name):
    global full_data
    df = pd.read_csv(file_name)
    full_data = df
    X = np.array(df)
    print (X)
    return X

def LoadPartialData(time, car_id = 1):
    global full_data, my_vehicle
    ldata = full_data[full_data['time']>= time]
    ldata = ldata[ldata['id']== car_id]

def LoadPartialData(time):
    global full_data, my_vehicle
    ldata = full_data[full_data['time']>= time]
    ldata = ldata[ldata['id']==car_id]
    pdata = ldata[ldata['time']<(time+0.1)]
    return pdata
