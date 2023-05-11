# github https://github.com/joshuablackburn2224/Python_Port_Script_DeltaNS/settings
# authors Joshua Blackburn , Kevin Shin , Sean Rice
import re
from pathlib import Path
import csv
import sys

# logic to get user input
# pulls file name from command line argument, if available
args = len(sys.argv)

if (args >= 2):
  logFile = str(sys.argv[1])
else:
  # ask user for a file name within the same directory as the script
  logFile = str(input("Enter the name of the file in this directory to pass to this script.\n"))

#grabs the file name from parent directory of script using path so absolute path is not used.
path = Path(__file__).parent / logFile
# 10.38.254.2Stout_MC_10.38.254.2

file_exists = Path.is_file(path)

if (file_exists):
  pass
else:
  print(f"Error: File '{path}' not found.")
  exit()

#initial opening of file
with open(path, 'r', encoding =None) as file:
  #substrings to help search for unique identifier for device ID
  substring1 = "sysName"
  deviceName = ""
  substring2 = "Slot-\d"
  substring3 = "\.\d"
  #driver loop
  for line in file:
  #logic for finding device name
    if substring1 in line:
      splitLine = line.rsplit(substring1)
      almostDeviceName = splitLine[1].strip()
      deviceName = almostDeviceName.strip('\"')
  if len(deviceName) > 1:
    pass
  else:
    #substrings to help search for unique identifier for device ID
    substr1 = "Slot-"
    substr2 = "\.\d"
    deviceName = ""
    #driver loop
    for line in file:
    #logic for finding device name
      if substr1 in line:
       index1 = line.find(substr1)
       findEnd = re.search(substr2, line)
       Span1 = findEnd.span()
       index2 = Span1[0]
       deviceName = line[index1 + len(substr1) + 1: index2]
      else:
        print(f"Error: Device ID not found. Please check config log.")
        exit()

#close file after retrieving device ID
file.close()

#logic for creating and writing to csv file with unique name
fileName = deviceName + "_SpecialPorts.csv"
csvPath = Path(__file__).parent / fileName
outfile = open(csvPath, "w")
writer = csv.writer(outfile)
header = ['device', 'vlan name', 'switch:port number', 'tag']
writer.writerow(header)

#open file second time to iterate through and find all vlan names and ports
with open(path, 'r', encoding =None) as file:
  for line in file:
     #substrings to help search for unique identifier for vlan names
    substring3 = "configure vlan "
    substring4 = " add ports"
    #logic for identifying vlan names
    if substring3 in line and substring4 in line:
      #split string at configure vlan and convert back from list to string
      vlanNameLineList = line.rsplit(substring3)
      vlanNameLineList.pop(0)
      vlanNameStringFromList = vlanNameLineList[0]
      #isolate tag, save as tagFinal by converting back from list to String
      tagFlag = True
      if "untagged" in vlanNameStringFromList:
        tagFlag = False
      tag = ""
      #isolate vlan name, save as vlanNameFinal by converting back from list to string
      vlanNameOnlyList = vlanNameStringFromList.rsplit(substring4)
      vlanNameFinal = vlanNameOnlyList[0]
      #begin iterating through portNumbersList
      if ":" in vlanNameStringFromList:
        #create portnumbers list and discover tag with regex
        portNumbersList = re.findall(("\d:\d*-?\d*\d"), vlanNameStringFromList)
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
          #logic for setting tagged or untagged in display
          if tagFlag == True:
            tag = "tagged"
          else:
            tag = "untagged"
            #logic for writing switch and port numbers when a range is and is not present
          if flag != True:
            portNumber = int(portNumbersModifiableList[1])
            portNumberString = portNumbersModifiableList[1]
            writeableSwitchPortNumber = switchNumberString + ":" + portNumberString
            newRow = []
            newRow = [deviceName, vlanNameFinal, writeableSwitchPortNumber, tag]
            writer.writerow(newRow)
          else:
            portNumberStart = int(portNumbersModifiableList[1])
            portNumberEnd = int(portNumbersModifiableList[2])
            for i in range (portNumberStart, portNumberEnd + 1):
              newRow = []
              writeableSwitchPortNumber = switchNumberString + ":" + str(i)
              newRow = [deviceName, vlanNameFinal, writeableSwitchPortNumber, tag]
              writer.writerow(newRow)
      else:
        #create portnumbers list and discover tag with regex
        portNumbersList = re.findall(("\d\d*-?\d*"), vlanNameStringFromList)
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
        #logic for setting tagged or untagged in display
          if tagFlag == True:
            tag = "tagged"
          else:
            tag = "untagged"
          #logic for writing switch and port numbers when a range is and is not present
          if flag != True:
            portNumber = int(portNumbersModifiableList[0])
            portNumberString = portNumbersModifiableList[0]
            writeablePortNumber = portNumberString
            newRow = []
            newRow = [deviceName, vlanNameFinal, writeablePortNumber, tag]
            writer.writerow(newRow)
          else:
            portNumberStart = int(portNumbersModifiableList[0])
            portNumberEnd = int(portNumbersModifiableList[1])
            for i in range (portNumberStart, portNumberEnd + 1):
              newRow = []
              writeablePortNumber = str(i)
              newRow = [deviceName, vlanNameFinal, writeablePortNumber, tag]
              writer.writerow(newRow)

outfile.close()
  
#    else if()