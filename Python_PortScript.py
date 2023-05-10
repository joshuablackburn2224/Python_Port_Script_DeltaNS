import re
fname = "C:/Users/joshu/Documents/Delta Internship/Port Script/Special Ports/sample.log"
# 10.38.254.2Stout_MC_10.38.254.2

with open(fname, 'r', encoding =None) as file:
  #search for unique identifier for device ID
  substr1 = "Slot-1"
  substr2 = ".1"
  deviceName = ""
  #search for unique identifier for vlan names
  substring3 = "configure vlan"
  substring4 = " add ports"
  vlanName = ""
  for line in file:
    if substr1 in line:
      index1 = line.find(substr1)
      index2 = line.find(substr2)

      deviceName = line[index1 + len(substr1) + 1: index2]
      print(deviceName)
    if substring3 in line and substring4 in line:
      vlanName = line.rsplit(substring3)
      vlanName.pop(0)
      vlanNameStringFromList = vlanName[0]
      portNumbers = re.findall(("\d:\d*-?\d*\d"), vlanNameStringFromList)
      vlanNameList2 = vlanNameStringFromList.rsplit(substring4)
      vlanNameFinal = vlanNameList2[0]
      print(vlanNameFinal)
      print(vlanNameStringFromList)
      print (portNumbers)
  
#    else if()