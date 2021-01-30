def filestuff():
   file = open("data/testdoc.txt", "r", encoding = 'utf-8')
   contents = file.read()
   file.close()
   contents = contents.split("\n")
   return contents

def arraystuff():
   formattedContents = [[0, 0, 0]]
   date = ""

   for i in range(len(contents)):
      array = [0] * 3
      string = contents[i]
      header = False

      if string.rfind("leon02four") == 0:
         state = True
         header = True
         date = string[-10:]
      elif string.rfind("みどり") == 0:
         state = False
         header = True
      if state == True and header == False:
         array[0] = "Leon"
         array[1] = date
         array[2] = string
         formattedContents.append(array)
   return formattedContents

contents = filestuff()
state = True
formatted = arraystuff()
print(formatted)