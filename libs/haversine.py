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
