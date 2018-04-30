class Vehicle():
    def __init__(self,_id):
	self.id   = _id
	self.long = 0 
	self.lati = 0
	self.speed= 0
	self.time = 0
	self.packet = 0
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
    def get_time(self):
	return self.time
    def set_packet(self,pk):
	self.packet = pk
    def get_packet(self):
	return self.packet
