import sys, ftd2xx as ftd
d = ftd.open(0)   
print(d.getDeviceInfo())
