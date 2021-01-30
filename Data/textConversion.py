file = open("data/unfilteredText.txt", "r", encoding = 'utf-8')
contents = file.read()
file.close()
contents = contents.split("\n")
formattedContents = [[0, 0, 0]]


state = [True]
date = ""

array = [0] * 3
for i in range(len(contents)):
   if contents[i].rfind("leon02four") == 0:
      print(contents[i])
   elif contents[i].rfind("みどり") == 0: