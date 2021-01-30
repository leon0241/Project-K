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

   return arrContentsLeon, arrContentsKristi, arrContentsLeon2

def main_csv_format(mainArray, name):
   # 744703296903708682,2020-08-16 23:45:01.900000+00:00,ye,
   formattedArray = []
   for i in range(len(mainArray)):
      newArray = [""] * 5
      # id, datetime, message, attachment -> name, date, time, message, attachment
      _, time, contents, attach = mainArray[i]
      newArray[0] = name
      
      # 2021-01-26 02:39:35.646000+00:00
      newArray[1] = time[:10]
      newArray[2] = time[11:19]

      newArray[3] = contents
      newArray[4] = attach
      formattedArray.append(newArray)
   return formattedArray

def filtered_csv_format(mainArray):
   # Leon,08/07/2020,wait wha
   formattedArray = []
   i = 0
   while len(mainArray) > i:
      newArray = [""] * 5

      name, date, message = mainArray[i]
      newArray[0] = name
      # Replace date format from DD/MM/YYYY to DD-MM-YYYY
      newArray[1] = date.replace("/", "-")
      
      # If starts with a link
      if message.startswith("https://") == True:
         # Sets new array as the message
         newArray[3] = message

         # If the 4th value down from the message is picture, it is a preview link
         if mainArray[i + 4][2] == "":
            for j in range(4):
               # Remove values describing the link
               mainArray.pop(i + 1)
      
      # If message is blank means its a picture
      elif message == "":
         newArray[4] = "https://media.discordapp.net/attachments/568593849195429898/805125659500216421/KokoronYay.png"
      # Else just a regular message
      else:
         newArray[3] = message
      formattedArray.append(newArray)
      i += 1
   return formattedArray

def csv_write(filename, array):
   csvfile = open(filename, 'w', encoding = 'cp437', newline='')
   with csvfile:
      writer = csv.writer(csvfile)
      
      writer.writerows(array)
   csvfile.close()

rawLeon, rawKristi, rawLeon2 = filestuff()
fLeon = main_csv_format(rawLeon, "Leon")
fKristi = main_csv_format(rawKristi, "Kristi")
fLeon2 = filtered_csv_format(rawLeon2)

csv_write("data/newData/formattedLeon.csv", fLeon)
csv_write("data/newData/formattedKristi.csv", fKristi)
csv_write("data/newData/formattedFilterLeon.csv", fLeon2)