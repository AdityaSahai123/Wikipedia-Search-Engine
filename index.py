import os, sys
from xml.sax import parse, ContentHandler
import re
import timeit
import glob
from heapq import heapify, heappush, heappop
from nltk.stem.snowball import SnowballStemmer

stemmer = SnowballStemmer("english")

totalTokensInIdexFile = 0
invertedindexStat = ""
stopWords = set()
setUnusedWords = set()
indexFolder = "2019201051/indexFiles/"
docIdToData = None
lastDocId = 0
invertedIndexTable = {}
FileLimit = 5000
folderToStore = ""


def writeStat():
	global setUnusedWords
	global totalTokensInIdexFile
	tempFile = open(invertedindexStat, "w")
	tempFile.write(str(totalTokensInIdexFile + len(setUnusedWords)) + "\n")
	tempFile.write(str(totalTokensInIdexFile) + "\n")


def myNum(word):
	if (len(word) > 4):
		return False
	if '0' in word or '1' in word or '2' in word or '3' in word or '4' in word or '5' in word or '6' in word or '7' in word or '8' in word or '9' in word:
		return True
	return False


def writeInvertedIndexToFile(docID):
	tempFile = open(indexFolder + str(docID) + ".txt", "w")
	for key, val in sorted(invertedIndexTable.items()):
		try:
			tempString = str(key) + ":"
			for k, v in sorted(val.items()):
				try:
					tempString += str(k) + "-"
					for tempKey, tempVal in v.items():
						try:
							tempString = tempString + str(tempKey) + str(tempVal) + ","
						except:
							continue

					tempString = tempString[:-1] + "|"
				except:
					continue
			if tempString != "":
				tempFile.write(str(tempString[:-1]) + "\n")
				global totalTokensInIdexFile
				totalTokensInIdexFile += 1
		except:
			continue
	tempFile.close()
	invertedIndexTable.clear()
	print(docID, " Documents Processed...")


def writeToTable(wordList, docID, temp):
	global setUnusedWords
	for word in wordList:
		try:
			if ((word.isalpha() and word not in stopWords and len(word) > 3 and len(word) < 16) or (myNum(word))):
				word = stemmer.stem(word)
				if word in invertedIndexTable:
					if docID in invertedIndexTable[word]:
						if temp in invertedIndexTable[word][docID]:
							invertedIndexTable[word][docID][temp] += 1
						else:
							invertedIndexTable[word][docID][temp] = 1
					else:
						invertedIndexTable[word][docID] = {temp: 1}
				else:
					invertedIndexTable[word] = dict({docID: {temp: 1}})
			else:
				setUnusedWords.add(word)
		except:
			continue


regEx1 = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', re.DOTALL)
regEx2 = re.compile(r'{\|(.*?)\|}', re.DOTALL)
regEx3 = re.compile(r'{{v?cite(.*?)}}', re.DOTALL)
regEx4 = re.compile(r'[-.,:;_?()"/\']', re.DOTALL)
regEx5 = re.compile(r'\[\[file:(.*?)\]\]', re.DOTALL)
regEx6 = re.compile(r'<(.*?)>', re.DOTALL)
regEx7 = re.compile(r'[~`!@#$%-^*+{\[}\]\|\\<>/?]', re.DOTALL)


def cleanText(text):
	try:
		text = re.compile(regEx1).sub('', text)
		text = re.compile(regEx2).sub('', text)
		text = re.compile(regEx3).sub('', text)
		text = re.compile(regEx4).sub(' ', text)
		text = re.compile(regEx5).sub('', text)
		text = re.compile(regEx6).sub('', text)
	except:
		return text
	return text


def processTitle(docData, docNo):
	text = docData.lower()
	text = cleanText(text)
	global setUnusedWords
	wordList = text.split()
	usefulWords = []
	for word in wordList:
		try:
			if (word.isalpha() and word not in stopWords and len(word) > 3 and len(word) < 16):
				usefulWords.append(re.compile(regEx7).sub(' ', word))
			elif (myNum(word)):
				usefulWords.append(word)
			else:
				setUnusedWords.add(word)
		except:
			continue

	writeToTable(usefulWords, docNo, "t")


def variousCats(cats, extractedDict, docNo):
	if (len(extractedDict[cats])):
		tempCats = ' '.join(extractedDict[cats])
		tempCats = re.compile(regEx7).sub(' ', tempCats)
		extractedDict[cats] = tempCats.split()
		subCat = cats.lower()
		writeToTable(extractedDict[cats], docNo, str(subCat[0]))


def cleanData(extractedDict, docNo):
	for infoList in extractedDict["Infobox"]:
		try:
			tokenList = []
			tokenList = re.findall(r'=(.*?)\|', infoList, re.DOTALL)
			tokenList = ' '.join(tokenList)
			tokenList = re.compile(regEx7).sub(' ', tokenList)
			tokenList = tokenList.split()
			writeToTable(tokenList, docNo, "i")
		except:
			continue

	variousCats("Categories", extractedDict, docNo)
	variousCats("References", extractedDict, docNo)
	variousCats("Body", extractedDict, docNo)
	variousCats("ELinks", extractedDict, docNo)


def processText(docData, docNo):
	text = docData.lower()
	text = cleanText(text)
	global setUnusedWords
	extractedDict = {}
	extractedDict["Body"] = []
	extractedDict["Infobox"] = []
	extractedDict["Categories"] = []
	extractedDict["References"] = []
	extractedDict["ELinks"] = []
	lines = text.split("\n")
	index = -1
	while index < len(lines) - 1:
		try:
			index += 1
			if lines[index].startswith("{{infobox"):
				while True:
					if ((index + 1) >= len(lines) or lines[index + 1].endswith("}}")):
						break
					index = index + 1
					line = lines[index]
					extractedDict["Infobox"].append(line)

			elif index < len(lines) and "[[category" in lines[index]:
				line = lines[index][11:-2]
				extractedDict["Categories"].append(line)
			elif index < len(lines) and lines[index].startswith("="):
				titleText = lines[index].replace("=", "")

				if titleText == "references" or titleText == "see also" or titleText == "further reading" or titleText == "external links":
					while index < len(lines):
						if (index + 1) >= len(lines) or lines[index + 1].startswith("="):
							break
						index = index + 1
						line = lines[index]
						if (titleText == "references"):
							extractedDict["References"].append(line)
						elif (titleText == "external links" and line.startswith("*")):
							extractedDict["ELinks"].append(line)
					continue

			else:
				tokensInLine = lines[index]
				extractedDict["Body"].append(tokensInLine)
		except:
			continue
	cleanData(extractedDict, docNo)
	global lastDocId
	lastDocId = docNo
	if docNo % FileLimit == 0:
		writeInvertedIndexToFile(docNo)


def docNoToTitle(docNo, doc_title, docData):
	docIdToData.write(str(docNo) + "#" + str(doc_title) + "\n")


class dumpHandler(ContentHandler):
	def __init__(self):
		self.docNo = 0
		self.documentData = ""
		self.documentTitle = ""
		self.isFirstID = False

	def startElement(self, element, attribute):
		if element == "title":
			self.documentData = ""
			self.isFirstID = True

		if element == "page":
			self.docNo = self.docNo + 1

		if element == "text":
			self.documentData = ""

		if element == "id" and self.isFirstID:
			self.documentData = ""

	def endElement(self, element):
		if element == "title":
			processTitle(self.documentData, self.docNo)
			self.documentTitle = self.documentData
			self.documentData = ""

		elif element == "text":
			processText(self.documentData, self.docNo)
			self.buffer = ""

		elif element == "id" and self.isFirstID:
			docNoToTitle(str(self.docNo), self.documentTitle, self.documentData)
			self.isFirstID = False
			self.documentData = ""

	def characters(self, docData):
		self.documentData = self.documentData + docData


def main_Wroking():
	global docIdToData
	docIdToData = open(str(folderToStore) + "docTitleMap.txt", "w")
	tempFile = open("2019201051/stopwords.txt", "r")
	global stopwords
	for line in tempFile:
		line = line.strip()
		stopWords.add(line)

	print("Processing the input Dump:-")
	start = timeit.default_timer()
	parse(sys.argv[1], dumpHandler())
	writeInvertedIndexToFile(lastDocId)
	stop = timeit.default_timer()
	writeStat()
	print("Total Time for Indexing:- ", stop - start, " seconds.")
	print("Around ", float(stop - start) / float(60), " minutes.")


def take_Arguments():
	if len(sys.argv) != 4:
		print("Error: Invalid command line arguments")
		sys.exit(1)
	global folderToStore
	folderToStore = str(sys.argv[2])
	if (folderToStore[-1:] != '/'):
		folderToStore += "/"
	global invertedindexStat
	invertedindexStat = str(sys.argv[3])

	if not os.path.exists(folderToStore[:-1]):
		os.makedirs(folderToStore[:-1])
	if not os.path.exists(indexFolder[:-1]):
		os.makedirs(indexFolder[:-1])
	main_Wroking()


take_Arguments()

indexFileCount = 0
secondaryIndex = {}
chunkSize = 5000

indexFiles = glob.glob("2019201051/indexFiles/*")
completedFiles = []
filePointers = []
currentRowOfFile = []
percolator = []
words = {}
total = 0
invertedIndex = {}


def writeToPrimary():
	offset = []
	firstWord = True
	global indexFileCount
	indexFileCount += 1
	fileName = folderToStore + "index" + str(indexFileCount) + ".txt"
	fp = open(fileName, "w")
	for i in sorted(invertedIndex):
		if firstWord:
			secondaryIndex[i] = indexFileCount
			firstWord = False
		toWrite = str(i) + ":" + invertedIndex[i] + "\n"
		fp.write(toWrite)


def writeToSecondary():
	fileName = folderToStore + "secondaryIndex.txt"
	fp = open(fileName, "w")
	for i in sorted(secondaryIndex):
		toWrite = str(i) + " " + str(secondaryIndex[i]) + "\n"
		fp.write(toWrite)


start = timeit.default_timer()

fileCount = 0
for i in range(len(indexFiles)):
	completedFiles.append(1)
	fp = open(indexFiles[i], "r")
	filePointers.append(fp)
	fileCount += 1
	currentRowOfFile.append(filePointers[i].readline())
	words[i] = currentRowOfFile[i].split(':')
	# print (words[i])
	if words[i][0] not in percolator:
		heappush(percolator, words[i][0])

while True:
	if completedFiles.count(0) == len(indexFiles):
		# print(completedFiles)
		break
	else:
		total += 1
		word = heappop(percolator)
		for i in range(len(indexFiles)):
			if completedFiles[i] and words[i][0] == word:
				if word in invertedIndex:
					invertedIndex[word] += "|" + words[i][1]
				else:
					invertedIndex[word] = words[i][1]

				if total == chunkSize:
					total = 0
					writeToPrimary()
					invertedIndex.clear()

				currentRowOfFile[i] = filePointers[i].readline().strip()

				if currentRowOfFile[i]:
					words[i] = currentRowOfFile[i].split(':')
					if words[i][0] not in percolator:
						heappush(percolator, words[i][0])
				else:
					completedFiles[i] = 0
					filePointers[i].close()
					os.remove(indexFiles[i])

writeToPrimary()
writeToSecondary()
stop = timeit.default_timer()

print("Time for Merging:", stop - start, " seconds.")
mins = float(stop - start) / float(60)
print("Time for Merging:", mins, " Minutes.")