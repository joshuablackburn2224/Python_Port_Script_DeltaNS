import re
fname = "C:/Users/joshu/Documents/Delta Internship/Port Script/Special Ports/sample.log"
# 10.38.254.2Stout_MC_10.38.254.2

with open(fname, 'r', encoding =None) as file:
  #substrings to help search for unique identifier for device ID
  substr1 = "Slot-1"
  substr2 = ".1"
  deviceName = ""
  #substrings to help search for unique identifier for vlan names
  substring3 = "configure vlan"
  substring4 = " add ports"
  #driver loop
  for line in file:
  #logic for finding device name
    if substr1 in line:
      index1 = line.find(substr1)
      index2 = line.find(substr2)
      deviceName = line[index1 + len(substr1) + 1: index2]
      print(deviceName)
    #logic for identifying vlan names
    if substring3 in line and substring4 in line:
      vlanNameLineList = line.rsplit(substring3)
      vlanNameLineList.pop(0)
      vlanNameStringFromList = vlanNameLineList[0]
      portNumbersList = re.findall(("\d:\d*-?\d*\d"), vlanNameStringFromList)
      vlanNameOnlyList = vlanNameStringFromList.rsplit(substring4)
      vlanNameFinal = vlanNameOnlyList[0]
      print(vlanNameFinal)
      for i in range (len(portNumbersList)):
        portNumberString = portNumbersList[i]
        print(portNumberString)
  
#    else if()