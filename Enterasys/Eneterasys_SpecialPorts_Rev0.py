# version 3.0
# github https://github.com/joshuablackburn2224/Python_Port_Script_DeltaNS/settings
# authors Joshua Blackburn , Kevin Shin , Sean Rice
import re
from pathlib import Path
import csv
import sys
import glob

# process each file as a function
# wrap each call in a try/except block so that the script is safely exited on a FileNotFoundError
def process_file(path):
  print(f"Processing {path}")
  #initial opening of file
  with open(path, 'r', encoding =None) as file:
    #substrings to help search for unique identifier for device ID
    substring1 = "system name"
    deviceName = ""
    substring2 = "Slot-"
    substring3 = "\.\d"
    #driver loop
    for line in file:
    #logic for finding device name
      if substring1 in line:
        splitLine = line.rsplit(substring1)
        almostDeviceName = splitLine[1].strip()
        deviceName = almostDeviceName.strip('\"')
    # Might not be relevant for Enterasys
      elif substring2 in line:
        index1 = line.find(substring2)
        findEnd = re.search(substring3, line)
        Span1 = findEnd.span()
        index2 = Span1[0]
        deviceName = line[index1 + len(substring2) + 1: index2]
    if len(deviceName) > 1:
      pass
    else:
      print(f"Error: Device ID not found. Please check config log.")
      exit()

  #close file after retrieving device ID
  # file.close()

  #logic for creating and writing to csv file with unique name
  fileName = deviceName + "_SpecialPorts.csv"
  csvPath = Path(__file__).parent / fileName
  outfile = open(csvPath, "w", newline='')
  writer = csv.writer(outfile)
  header = ['device', 'vlan name', 'vlan number', 'direction', 'port number', 'tag']
  writer.writerow(header)
  

  #TODO: Need to add logic for creating dictionary of Key:Value = Number:Name
  # create empty dictionary to store vlan number and name
  vlans = {}

  # open file SECOND time for populating dictionary of vlan number:name
  with open(path, 'r', encoding =None) as file:
    substring11 = "set vlan name"

    for line in file:

      if (substring11 in line):

        mappableVlanList = line.rsplit(" ")
        for i in range(3):
          mappableVlanList.pop(0)
        
        mappableVlanList[1] = mappableVlanList[1].replace("\n", "")
        mappableVlanList[1] = mappableVlanList[1].replace("\"", "")


        vlans.update({mappableVlanList[0]: mappableVlanList[1]})

  """
  # print entire dictionary
  for key, value in vlans.items():
    print(key, value)

  print()
  search with key
  print(vlans['610'])

  # find key by value
  for key, value in vlans.items():
    if value == 'HS':
      print(key)
  """

  #open file THIRD time to iterate through and find all vlan names and ports
  with open(path, 'r', encoding =None) as file:
    for line in file:
      #substrings to help search for unique identifier for vlan names
      substring4 = "set vlan"
      substring5 = "egress"
      substring6 = "ingress"
      #logic for identifying vlan names
      if substring4 in line and (substring5 in line or substring6 in line):

        # if string 'egress' exists in the line, save that as a variable.
        # if string 'ingress' exists instead, do the same.
        # the else statement should hopefully never run
        if substring5 in line:
          direction = substring5
        elif substring6 in line:
          direction = substring6
        else:
          print("Error: could not set egress/ingress variable")
          direction = 'unknown'
        
        #split string at set vlan and convert back from list to string
        vlanNumberLineList = line.rsplit(direction)
        vlanNumberLineList.pop(0)
        vlanNumberStringFromList = vlanNumberLineList[0]
        #isolate tag, save as tagFinal by converting back from list to String
        tagFlag = True
        if "untagged" in vlanNumberStringFromList:
          tagFlag = False
        tag = ""
        #isolate vlan number, save as vlanNumberFinal by converting back from list to string
        vlanNumberOnlyList = vlanNumberStringFromList.rsplit()
        vlanNumberFinal = vlanNumberOnlyList[0]
        #begin iterating through portNumbersList
        #if ":" in vlanNumberStringFromList:
          #create portnumbers list and isolate all port numbers
        portNumberListStart = vlanNumberStringFromList.split()
        portNumberListStart.pop(len(portNumberListStart) - 1)
        portNumberListStart.pop(0)
        portNumberOnlyString = portNumberListStart[0]
        # create list of individual port ranges by splitting at ;
        portNumbersList = portNumberOnlyString.split(";")
        for i in range (len(portNumbersList)):
            #create flag, set to False initially, True if range of port Numbers present
            flag = False
            #convert portNumbersList to String for Modifications
            portNumberString = portNumbersList[i]
            if "-" in portNumberString:
              flag = True
            #create list of isolated integers from String
            portNumbersModifiableList = portNumberString.split(".")
            portNumberNoRangeFinal = portNumberString
            isolatedPortNumberRange = portNumbersModifiableList[2]
            #logic for setting tagged or untagged in display
            if tagFlag == True:
              tag = "tagged"
            else:
              tag = "untagged"
              #logic for writing switch and port numbers when a range is and is not present
            if flag != True:
              writeableSwitchPortNumber =  portNumberNoRangeFinal
              newRow = []
              newRow = [deviceName, vlans[vlanNumberFinal], vlanNumberFinal, direction, writeableSwitchPortNumber, tag]
              if "Loop" not in vlanNumberFinal and "loop" not in vlanNumberFinal:
                writer.writerow(newRow)
              else: 
                pass
            else:
              isolatedPortNumbers = isolatedPortNumberRange.split("-")
              portNumberStart = int(isolatedPortNumbers[0])
              portNumberEnd = int(isolatedPortNumbers[1])
              for i in range (portNumberStart, portNumberEnd + 1):
                newRow = []
                writeableSwitchPortNumber = portNumbersModifiableList[0] + "." + portNumbersModifiableList[1] + "." + str(i)
                newRow = [deviceName, vlans[vlanNumberFinal], vlanNumberFinal, direction, writeableSwitchPortNumber, tag]
                if "Loop" not in vlanNumberFinal and "loop" not in vlanNumberFinal:
                  writer.writerow(newRow)
                else: 
                 pass


  outfile.close()

  print(f"Completed {path}")
    
  #    else if()

# logic to get user input

# pulls file name from command line argument, if available
args = len(sys.argv)
if (args >= 2):
  logFile = str(sys.argv[1])

  # attempt to process the file, and exit if it does not exist
  try:
    process_file(logFile)
  except FileNotFoundError:
    print(f"Error: file {logFile} does not exist")
    exit()

  # exit once processing is finished
  exit()
else:

  # grab the full path of all files in the current directory ending in .log
  # these are stored in a list
  parent = Path(__file__).parent
  fileList = glob.glob(f"{parent}/*.log")
  numFiles = len(fileList)

  # if files cannot be fetched automatically, ask user for a file name within the same directory as the script
  if numFiles < 1:
    logFile = str(input("Couldn't fetch log files automatically.\nEnter the name of the file in this directory to pass to this script.\n"))

    # attempt to process the file, and exit if it does not exist
    try:
      process_file(logFile)
    except FileNotFoundError:
      print(f"Error: file {logFile} does not exist")
      exit()
  else:

    # run the process function for each file found in the current directory
    for file in fileList:

      # attempt to process the file, and exit if it does not exist
      try:
        process_file(file)
      except FileNotFoundError:
        print(f"Error: file {file} does not exist")
        exit()
  # exit once processing has finished
  exit()

