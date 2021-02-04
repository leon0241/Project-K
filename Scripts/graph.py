import csv

array = []

def read_files():
   names = ["Data/formattedLeon.csv", "Data/formattedKristi.csv", "Data/formattedFilterLeon.csv"]

   for i in range(3):
      with open(names[i], "r", encoding="cp437") as file:
         rawContents = csv.reader(file, delimiter=",")
         for row in rawContents:
            array.append(row)
      file.close()

read_files()