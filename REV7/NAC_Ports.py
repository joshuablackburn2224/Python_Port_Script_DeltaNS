import re
from pathlib import Path
import csv
import sys
import glob

def findNACPorts(path):
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
        if len(deviceName) > 2:
            break
    if len(deviceName) < 1:
      print(f"Error: Device ID not found. Please check config log." + path)
  fileNameSuffix = "_NACports.txt"
  fileName = deviceName + fileNameSuffix
  #close file after retrieving device ID
  file.close()
  #initial opening of file txt
  with open(path, 'r', encoding =None) as file:
    # substring to search for 
    portMin = '1'
    portMax = '48'
    slot1 = "1:\d+"
    slot2 = "2:\d+"
    slot3 = "3:\d+"
    slot4 = "4:\d+"
    slot5 = "5:\d+"
    slot6 = "6:\d+"
    slot7 = "7:\d+"
    slots = [slot1,slot2,slot3,slot4,slot5,slot6,slot7]
    # create writer for CSV file

    csvPath = Path(__file__).parent / fileName
    outfile = open(csvPath, "w", newline='')
    writer = csv.writer(outfile)
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
        if len(deviceName) > 2:
            break
    if len(deviceName) < 1:
      print(f"Error: Device ID not found. Please check config log.")
    originalPortNums = []
    for line in file:
        if "Tag:" in line:
          break
        for slotNum in range(len(slots)):
          currentports = re.findall(slots[slotNum], line)
          if len(currentports) > 0:
            for i in range(len(currentports)):
              originalPortNums.append(currentports[i])
    file.close()
    global portRange, writeablePorts, tempSwitchNum
    portRange = []
    writeablePorts = []
    tempSwitchNum = 1
    for i in range(len(originalPortNums)):
      switchPort = originalPortNums[i].rsplit(":")
      thisSwitchNum = switchPort[0]
      if int(thisSwitchNum) == tempSwitchNum:
        portRange.append(int(switchPort[1]))
      else:
        createPortRanges(tempSwitchNum, portRange, writeablePorts)

        tempSwitchNum += 1
        portRange.clear()
        portRange.append(int(switchPort[1]))
    createPortRanges(tempSwitchNum, portRange, writeablePorts)
    print(writeablePorts)
    for i in range(len(writeablePorts)):
      outfile.write(writeablePorts[i])
      if i != len(writeablePorts) - 1:
        outfile.write(",")

    # #logic for finding device name
    #     newrow = []
    #     if PSU_600 in line:
    #         newrow = [deviceName, line]
    #         writer.writerow(newrow)
    #     else: 
    #         pass
    outfile.close()

def createPortRanges(tempSwitchNum, portRange, writeablePorts):
  print("Switch Number {}".format(tempSwitchNum))
  print(portRange)
  thisRange = []
  for p in range(len(portRange)):
    if p + 1 < len(portRange):
      nextPort = portRange[p+1]
      if nextPort == portRange[p] + 1:
        thisRange.append(portRange[p])
      else:
        if len(thisRange) > 0:
          thisRange.append(portRange[p])
          rangeStart = thisRange[0]
          rangeEnd = thisRange[len(thisRange)-1]

          finalRange = "{}:{}-{}".format(tempSwitchNum,rangeStart,rangeEnd)
          writeablePorts.append(finalRange)
          thisRange.clear()
        else:
          thisPort = portRange[p]
          singlePort = "{}:{}".format(tempSwitchNum, thisPort)
          writeablePorts.append(singlePort)
    else:
      if portRange[p] == portRange[p-1] + 1:
        if len(thisRange) > 0:
          thisRange.append(portRange[p])
          rangeStart = thisRange[0]
          rangeEnd = thisRange[len(thisRange)-1]

          finalRange = "{}:{}-{}".format(tempSwitchNum,rangeStart,rangeEnd)
          writeablePorts.append(finalRange)
          thisRange.clear()
      else:
        thisPort = portRange[p]
        singlePort = "{}:{}".format(tempSwitchNum, thisPort)
        writeablePorts.append(singlePort)


def main():
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
        findNACPorts(logFile)
      except FileNotFoundError:
        print(f"Error: file {logFile} does not exist")
        stop()
    else:

      # run the process function for each file found in the current directory
      for file in fileList:
        print(f"Processing {file}")
        # attempt to process the file, and exit if it does not exist
        try:
            findNACPorts(file)
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