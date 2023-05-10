import re
from pathlib import Path
import csv

#grabs the file name from parent directory of script using path so absolute path is not used. Will probably have to be changed to accept inputs from user, file names will be different in the future.
path = Path(__file__).parent / "10.38.254.41Stout_IC2_10.38.254.41.log"
# 10.38.254.2Stout_MC_10.38.254.2

csvPath = Path(__file__).parent / "output.csv"
outfile = open(csvPath, "w")

writer = csv.writer(outfile)

header = ['device', 'vlan name', 'switch number', 'port numer', 'tag']
writer.writerow(header)

with open(path, 'r', encoding =None) as file:
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
      #split string at configure vlan and convert back from list to string
      vlanNameLineList = line.rsplit(substring3)
      vlanNameLineList.pop(0)
      vlanNameStringFromList = vlanNameLineList[0]
      #create portnumbers list and discover tag with regex
      portNumbersList = re.findall(("\d:\d*-?\d*\d"), vlanNameStringFromList)
      tagFlag = True
      if "untagged" in vlanNameStringFromList:
        tagFlag = False
      tag = ""
      #isolate vlan name, save as vlanNameFinal by converting back from list to string
      vlanNameOnlyList = vlanNameStringFromList.rsplit(substring4)
      vlanNameFinal = vlanNameOnlyList[0]
      #isolate tag, save as tagFinal by converting back from list to String
      #begin iterating through portNumbersList
      for i in range (len(portNumbersList)):
        #create flag, set to False initially, True if range of port Numbers present
        flag = False
        #convert portNumbersList to String for Modifications
        portNumberString = portNumbersList[i]
        if "-" in portNumberString:
          flag = True
        #create list of isolated integers from String
        portNumbersModifiableList = re.findall("\d*",portNumberString)
        #remove all blank spaces from list
        while "" in portNumbersModifiableList:
         portNumbersModifiableList.remove("")
        #isolate switch number
        switchNumber = int(portNumbersModifiableList[0])
        switchNumberString = portNumbersModifiableList[0]
        #logic for printing switch and port numbers when a range is and is not present
        if tagFlag == True:
          tag = "tagged"
        else:
          tag = "untagged"
        if flag != True:
          portNumber = int(portNumbersModifiableList[1])
          portNumberString = portNumbersModifiableList[1]
          print(vlanNameFinal,switchNumber, portNumber, tag)
          writeableSwitchPortNumber = switchNumberString + ":" + portNumberString
          newRow = []
          newRow = [deviceName, vlanNameFinal, writeableSwitchPortNumber, tag]
          writer.writerow(newRow)
        else:
          portNumberStart = int(portNumbersModifiableList[1])
          portNumberEnd = int(portNumbersModifiableList[2])
          for i in range (portNumberStart, portNumberEnd + 1):
            print(vlanNameFinal, switchNumber, i, tag)
            newRow = []
            writeableSwitchPortNumber = switchNumberString + ":" + str(i)
            newRow = [deviceName, vlanNameFinal, writeableSwitchPortNumber, tag]
            writer.writerow(newRow)

outfile.close()
  
#    else if()