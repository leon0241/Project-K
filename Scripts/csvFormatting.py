import csv
import csvFunctions

def filestuff():
   # Init 2d arrays
   arrContentsLeon = []
   arrContentsKristi = []
   arrContentsLeon2 = []

   names = ["Data/rawData/messagesLeon.csv", "Data/rawData/messagesKristi.csv"]
   # Repeats 2 times for leon and kristi
   for i in range(2): 
      # Open file [i]
      with open(names[i], "r", encoding="cp437") as file:
         rawContents = csv.reader(file, delimiter=",")
         # If Leon
         if i == 0:
            # Append row into 2d array
            for row in rawContents:
               arrContentsLeon.append(row)
         # If Kristi
         else:
            # Append row into second 2d array
            for row in rawContents:
               arrContentsKristi.append(row)
      file.close()
   
   with open("Data/rawData/filteredLeon.csv", "r", encoding="cp437") as file:
      rawContents = csv.reader(file, delimiter=",")
      for row in rawContents:
         arrContentsLeon2.append(row)
   file.close()

   return arrContentsLeon, arrContentsKristi, arrContentsLeon2

def main():
   rawLeon, rawKristi, rawLeon2 = filestuff()
   formattedLeon = csvFunctions.main_csv_format(rawLeon, "Leon")
   formattedKristi = csvFunctions.main_csv_format(rawKristi, "Kristi")
   formattedLeon2 = csvFunctions.filtered_csv_format(rawLeon2)
   fullData = formattedLeon + formattedLeon2 + formattedKristi
   
   csvFunctions.csv_write("Data/sortedData.csv", fullData)

main()
