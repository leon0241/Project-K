import csv

def filestuff():
   # Init 2d arrays
   arrContentsLeon = []
   arrContentsKristi = []
   arrContentsLeon2 = []

   names = ["Data/messagesLeon.csv", "Data/messagesKristi.csv"]
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
   
   with open("DAta/filteredLeon.csv", "r", encoding="cp437") as file:
      rawContents = csv.reader(file, delimiter=",")
      for row in rawContents:
         arrContentsLeon2.append(row)
   file.close()
   print(arrContentsLeon[1])
   print(arrContentsLeon2[1])
   print(arrContentsKristi[1])

filestuff()

# open("Data/filteredLeon.csv", "r", encoding="utf-8") as fileLeon2, \
#       open("Data/messagesKristi.csv", "r", encoding="utf-8") as fileKristi:
#       contentsLeon1 = fileLeon1.read()
#       contentsLeon2 = fileLeon2.read()
#       contentsKristi = fileKristi.read()
#    fileLeon1.close()
#    fileLeon2.close()
#    fileKristi.close()