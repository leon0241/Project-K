# Converts copy-pasted discord into csv format

import csv

def filestuff():
   file = open("data/rawData/unfilteredtext.txt", "r", encoding = 'utf-8')
   contents = file.read()
   file.close()
   contents = contents.split("\n") # Split new line
   return contents

def arraystuff():
   formattedContents = [[0, 0, 0]] # 2d array
   date = ""
   state = True # State determines if Leon or Kristi (Leon is true)

   for i in range(len(contents)):
      array = [0] * 3 # Empty array
      string = contents[i] # Message contents
      header = False

      # If the string is message header leon
      if string.rfind("leon02four") == 0:
         state = True
         header = True
         date = string[-10:]
      # If the string is message header kristi
      elif string.rfind("みどり") == 0:
         state = False
         header = True
      # Write if string is not header and is leon
      if state == True and header == False:
         array[0] = "Leon" # Write name
         array[1] = date # Write date
         array[2] = string # Write message
         formattedContents.append(array) # Append the array to the 2d array
   return formattedContents

def csvstuff():
   csvfile = open("data/filteredLeon.csv", 'w', encoding = 'utf-8', newline='')
   with csvfile:
      writer = csv.writer(csvfile)
      
      writer.writerows(formatted)
   csvfile.close()

contents = filestuff()
formatted = arraystuff()
csvstuff()
print(formatted)
