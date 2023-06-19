# version 4.0
# github https://github.com/joshuablackburn2224/Python_Port_Script_DeltaNS/settings
# authors Joshua Blackburn , Kevin Shin , Sean Rice
# 1)Make sure python is installed
# 2)Place script in folder with log files which must contain the following:
#   a) sho configuration
#   b) sho fdb
#   c) sho edp ports all
# 3)Drag script to command prompt
# 
# Excel treats port numbers (eg. 1:11) as time by default. To change this:
# Don't double-click the CSV. 
# Launch Excel, go to "tell me what you want" and type import CSV then select do not detect data type

import re
from pathlib import Path
import csv
import sys
import glob

# process each file as a function
# wrap each call in a try/except block so that the script is safely exited on a FileNotFoundError
def process_file(path, tagOption):
  #initial opening of file
  with open(path, 'r', encoding =None) as file:
    #substrings to help search for unique identifier for device ID
    substring1 = "sysName"
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
      stop()

  #close file after retrieving device ID
  file.close()

  #logic for creating and writing to csv file with unique name
  deviceName = deviceName.strip()
  fileName = deviceName + "_SpecialPorts.csv"
  if tagOption == "tagged":
    fileNameSuffix = "_SpecialPorts_untaggedOnly.csv"
  elif tagOption == "untagged":
    fileNameSuffix = "_SpecialPorts_taggedOnly.csv"
  else:
    fileNameSuffix = "_SpecialPorts.csv"

  fileName = deviceName + fileNameSuffix
  
  csvPath = Path(__file__).parent / fileName
  outfile = open(csvPath, "w", newline='')
  writer = csv.writer(outfile)
  
  #updated header with mac column
  header = ['device', 'vlan name', 'MAC', 'port number', 'tag']
  writer.writerow(header)
  
  #added variable called macDictionary that will allow macS to be added to file
  
  macDictionary = macAndPortData(path)
  

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
            macAddress = None
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
            switchNumberString = portNumbersModifiableList[0]
            #logic for setting tagged or untagged in display
            if tagFlag == True:
              tag = "tagged"
            else:
              tag = "untagged"
            
            if tag == tagOption:
              continue
            else:
              pass

  #           print("Value of macDictionary:")
  # print(len(macDictionary) + " items")
  # for key, value in macDictionary.items():
  #   print(key, value)
  # wait = str(input("Press enter to continue..."))

              #logic for writing switch and port numbers when a range is and is not present
            if flag != True:
              portNumberString = portNumbersModifiableList[1]
              writeableSwitchPortNumber = switchNumberString + ":" + portNumberString
              #added logic for retrieving mac address for dictionary and writing to csv
              if writeableSwitchPortNumber in macDictionary:
                if vlanNameFinal in macDictionary[writeableSwitchPortNumber]:
                  macAddress = macDictionary[writeableSwitchPortNumber][vlanNameFinal]
              else:
                macAddress = " "
              newRow = []
              newRow = [deviceName, vlanNameFinal, macAddress, writeableSwitchPortNumber, tag]
              if "Loop" not in vlanNameFinal and "loop" not in vlanNameFinal and "LOOP" not in vlanNameFinal:
                writer.writerow(newRow)
              else: 
                pass
            else:
              portNumberStart = int(portNumbersModifiableList[1])
              portNumberEnd = int(portNumbersModifiableList[2])
              for i in range (portNumberStart, portNumberEnd + 1):
                newRow = []
                #added logic for mac Adress retrieval
                writeableSwitchPortNumber = switchNumberString + ":" + str(i)
                if writeableSwitchPortNumber in macDictionary:
                  if vlanNameFinal in macDictionary[writeableSwitchPortNumber]:
                    macAddress = macDictionary[writeableSwitchPortNumber][vlanNameFinal]
                else: 
                  macAddress = " "
                newRow = [deviceName, vlanNameFinal, macAddress, writeableSwitchPortNumber, tag]
                if "Loop" not in vlanNameFinal and "loop" not in vlanNameFinal and "LOOP" not in vlanNameFinal:
                  writer.writerow(newRow)
                else: 
                 pass
        #logic for writing without a switch number present (no #:## format)
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
              portNumberString = portNumbersModifiableList[0]
              writeablePortNumber = portNumberString
              newRow = []
              #added blank column for mac address since mac retrieval does not function without #:## format
              macAddress = " "
              newRow = [deviceName, vlanNameFinal, macAddress, writeablePortNumber, tag]
              if "Loop" not in vlanNameFinal and "loop" not in vlanNameFinal and "LOOP" not in vlanNameFinal:
                writer.writerow(newRow)
              else: 
                pass
            else:
              portNumberStart = int(portNumbersModifiableList[0])
              portNumberEnd = int(portNumbersModifiableList[1])
              for i in range (portNumberStart, portNumberEnd + 1):
                newRow = []
                writeablePortNumber = str(i)
                macAddress = " "
                newRow = [deviceName, vlanNameFinal, macAddress, writeablePortNumber, tag]
                if "Loop" not in vlanNameFinal and "loop" not in vlanNameFinal and "LOOP" not in vlanNameFinal:
                  writer.writerow(newRow)
                else: 
                  pass
  

  outfile.close()

  print(f"Completed {path}")
    
  #    else if()

#UPDATE Create additional function to compile mac addresses and port numbers, then use data to add MACs to appropriate rows
def macAndPortData(path):
  with open(path, 'r', encoding =None) as file:
    #define regex patterns
    uplink_pattern = "(00:00:\w+:\w+:\w+:\w+:\w+:\w+)"
    mac_pattern = "(\d{2}:\w+:\w+:\w+:\w+:\w+)"
    port_pattern = "\s+\d:\d+\d*"
    uplinkPort_pattern = "\d:\d+\d?"
    vlanName_pattern = "[a-zA-Z]+_*+[a-zA-Z]+_*+[a-zA-Z]+_*+\d*"
    #create lists to hold all unique port numbers, names and uplink ports
    uplinkPortsUnique = []
    portListUnique = []
    nameListUnique = []
    #Define Outermost Dictionary
    outerPorts_innerNamesAndMacs = {}
    #loop through file
    for line in file:
    #use regex searches to define logic for dictionary creation
      logicalMatch = re.search(mac_pattern, line)
      uplinkMatch = re.search(uplink_pattern, line)
    #if mac address found in line do...
      if logicalMatch != None:
        #if mac address is not an uplink mac do...
        if uplinkMatch == None:
          #create lists containing mac address, port, and vlanName
          macList = re.findall(mac_pattern, line)
          portList = re.findall(port_pattern, line)
          vlanNameList = re.findall(vlanName_pattern, line)
          #convert lists to strings
          mac = macList[0]
          
          # port = portList[0].strip()
          try:
            port = portList[0].strip()
          except Exception as e:
            continue

          # if len(portList) > 0:
          #   print(line)

          vlanName = vlanNameList[0]
          #append port and vlan name to unique list if item not already present
          if vlanName not in nameListUnique:
            nameListUnique.append(vlanName)
          #update outer dictionary if port number is not already present
          if port not in portListUnique:
            portListUnique.append(port)
            outerPorts_innerNamesAndMacs.update({port : {vlanName:mac}})
          #update dictionary related to corresponding port if port already present
          else:
            outerPorts_innerNamesAndMacs[port].update({vlanName:mac})
        #create list of uplink ports using unique 00:00:...mac identifier
        else:
          uplinkPort = re.findall(uplinkPort_pattern, line)
          uplinkPortsUnique.append(uplinkPort[0])
  #removed all entries from outer dictionary that contain uplink ports
  for i in range(len(uplinkPortsUnique)):
    if uplinkPortsUnique[i] in outerPorts_innerNamesAndMacs:
      outerPorts_innerNamesAndMacs.pop(uplinkPortsUnique[i])
  return outerPorts_innerNamesAndMacs


def main():

  userInput = -1
  print("Choose an option by entering its respective number")
  while userInput == -1:
    userInputString = "1. Process untagged vlans only\n2. Process tagged vlans only\n3. Process all vlans\nAlternatively, press Enter to perform option 1 by default.\n"
    try:
      userInput = int(input(userInputString))
    except Exception as e:
      userInput = 1
    if (userInput > 3) or (userInput < 1):
      userInput = -1
  
  # print(userInput)
  
  if userInput == 1:
    userTagOption = "tagged"
    print("Processing only untagged vlans!")
  elif userInput == 2:
    userTagOption = "untagged"
    print("Processing only tagged vlans!")
  else:
    userTagOption = ""
    print("Processing all vlans!")


  # logic to get user input

  # pulls file name from command line argument, if available
  args = len(sys.argv)
  if (args >= 2):
    logFile = str(sys.argv[1])

    # attempt to process the file, and exit if it does not exist
    try:
      macAndPortData(logFile)
      process_file(logFile, userTagOption)
    except FileNotFoundError:
      print(f"Error: file {logFile} does not exist")
      stop()

    # exit once processing is finished
    stop()
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
        macAndPortData(logFile)
        process_file(logFile, userTagOption)
      except FileNotFoundError:
        print(f"Error: file {logFile} does not exist")
        stop()
    else:

      # run the process function for each file found in the current directory
      for file in fileList:
        print(f"Processing {file}")
        # attempt to process the file, and exit if it does not exist
        try:
          macAndPortData(file)
          process_file(file, userTagOption)
        except FileNotFoundError:
          print(f"Error: file {file} does not exist")
          stop()
    # exit once processing has finished
    stop()


def stop():
  wait = str(input("Press Enter to exit...\n"))
  exit()

#main()
# try/except block to catch any errors and report them
if (__name__ == "__main__"):
  try:
    main()
  except Exception as e:
    print("The script has stopped due to the following error:")
    print(e)
  else:
    print("Processing complete.")
    stop()