import re
from pathlib import Path
import csv
import sys
import glob

def findPSUs(path):
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

  #close file after retrieving device ID
  file.close()
  #initial opening of file
  with open(path, 'r', encoding =None) as file:
    # substring to search for 
    PSU_600 = "(54V/600W Max)"
    # create writer for CSV file

    csvPath = Path(__file__).parent / "BatteryList.csv"
    outfile = open(csvPath, "a", newline='')
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
    for line in file:    
    #logic for finding device name
        newrow = []
        if PSU_600 in line:
            newrow = [deviceName, line]
            writer.writerow(newrow)
        else: 
            pass
    outfile.close()
    file.close()


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
        findPSUs(logFile)
      except FileNotFoundError:
        print(f"Error: file {logFile} does not exist")
        stop()
    else:

      # run the process function for each file found in the current directory
      for file in fileList:
        print(f"Processing {file}")
        # attempt to process the file, and exit if it does not exist
        try:
            findPSUs(file)
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