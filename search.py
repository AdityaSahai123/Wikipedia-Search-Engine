import os, sys
import timeit
from bisect import bisect
from math import log10
from nltk.stem.snowball import SnowballStemmer
import re
from operator import itemgetter

stopWords = set()
docTitleMap = {}
dict_appearance1 = {}
Total_docs = 0
secondaryIndex = []
indexFolder = ""
stemmer = SnowballStemmer("english")
regEx = re.compile(r'(\d+|\s+)')
outFile = open("queries_op.txt​", 'w')


def myNum(word):
	if (len(word) > 4):
		return False
	if '0' in word or '1' in word or '2' in word or '3' in word or '4' in word or '5' in word or '6' in word or '7' in word or '8' in word or '9' in word:
		return True
	return False


def wf(exp, weightedFrequency):
	lis = re.compile(r'(\d+|\s+)').split(exp)
	tagType, Frequency = lis[0], lis[1]

	if tagType == "i":
		freq = int(Frequency) * 50
		weightedFrequency += freq
	elif tagType == "t":
		freq = int(Frequency) * 1000
		weightedFrequency += freq
	elif tagType == "c":
		freq = int(Frequency) * 50
		weightedFrequency += freq
	elif tagType == "r":
		freq = int(Frequency) * 50
		weightedFrequency += freq
	elif tagType == "e":
		freq = int(Frequency) * 50
		weightedFrequency += freq
	elif tagType == "b":
		freq = int(Frequency) * 5
		weightedFrequency += freq
	return weightedFrequency


def writeToFile(global_dict, K):
	LandF_dict = {}
	for k in global_dict:
		try:
			weightedFrequency = 0
			n = len(global_dict[k])
			for x in global_dict[k]:
				x, idf = x.split("_")
				x = x.split(",")
				try:
					for y in x:
						try:
							weightedFrequency = wf(y, weightedFrequency)
						except:
							continue
				except:
					continue
		except:
			continue
		if n in LandF_dict:
			LandF_dict[n][k] = float(log10(1 + weightedFrequency)) * float(idf)
		else:
			LandF_dict[n] = {k: float(log10(1 + weightedFrequency)) * float(idf)}

	count = K

	for k, v in sorted(LandF_dict.items(), reverse=True):
		for k1, v1 in sorted(v.items(), key=itemgetter(1), reverse=True):
			count -= 1
			outFile.write(str(k1) + ", " + str(docTitleMap[k1]))
			if count == 0:
				break
		if count == 0:
			break


def Normal_query_words(queryWords, K):
	wordsToSearch = []
	for word in queryWords:
		try:
			word = word.lower().strip()

			if word not in stopWords:
				word = stemmer.stem(word)

			if ((word.isalpha() and len(word) > 3 and len(word) < 16 and word not in stopWords) or (myNum(word))):
				wordsToSearch.append(word)
		except:
			continue
	global_dict = {}
	for word in wordsToSearch:
		position = bisect(secondaryIndex, word)
		if position < 0:
			continue
		primaryFile = indexFolder + "index" + str(position) + ".txt"
		file = open(primaryFile, "r")
		data = file.read()

		pos_start = data.find(word + ":")
		if pos_start == -1:
			continue
		pos_end = data.find("\n", pos_start + 1)
		required_text = data[pos_start:pos_end]
		word, entry = required_text.split(":")
		posting_list = entry.split("|")
		No_Doc_word_found = len(posting_list)

		idf = log10(Total_docs / No_Doc_word_found)
		for i in posting_list:
			docID, entry = i.split("-")
			if docID in global_dict:
				global_dict[docID].append(entry + "_" + str(idf))
			else:
				global_dict[docID] = [entry + "_" + str(idf)]

	writeToFile(global_dict, K)


def stemming_words(query):
	querywords = []
	words_to_process = query.split()
	field_dict = {}
	for word in words_to_process:
		word = word.lower().strip()

		if word not in stopWords:
			word = stemmer.stem(word)

		if ((word.isalpha() and len(word) > 3 and len(word) < 16 and word not in stopWords) or (myNum(word))):
			if word not in field_dict:
				field_dict[word] = 1
				querywords.append(word)
	return querywords


def field_entry(field_dict, c, index_list, i):
	required_text = query[index_list[i] + 2:index_list[i + 1]]
	Extracted_query = stemming_words(required_text)
	field_dict[c] = Extracted_query


def get_field_dict(query):
	Extracted_query = []
	field_dict = {}
	index_list = []
	indextotype = {}
	index_category = query.find('c:')
	index_ref = query.find('r:')
	index_ext = query.find('e:')
	index_title = query.find('t:')
	index_body = query.find('b:')
	index_infobox = query.find('i:')

	indextotype[index_category] = 'c'
	indextotype[index_ref] = 'r'
	indextotype[index_ext] = 'e'
	indextotype[index_title] = 't'
	indextotype[index_body] = 'b'
	indextotype[index_infobox] = 'i'

	if index_ref != -1:
		index_list.append(index_ref)
	if index_infobox != -1:
		index_list.append(index_infobox)
	if index_ext != -1:
		index_list.append(index_ext)
	if index_title != -1:
		index_list.append(index_title)
	if index_body != -1:
		index_list.append(index_body)
	if index_category != -1:
		index_list.append(index_category)

	index_list.append(len(query))
	index_list.sort()

	for i in range(0, len(index_list) - 1):
		if indextotype[index_list[i]] == 'c':
			field_entry(field_dict, 'c', index_list, i)

		if indextotype[index_list[i]] == 'r':
			field_entry(field_dict, 'r', index_list, i)

		if indextotype[index_list[i]] == 'e':
			field_entry(field_dict, 'e', index_list, i)
		if indextotype[index_list[i]] == 't':
			field_entry(field_dict, 't', index_list, i)

		if indextotype[index_list[i]] == 'b':
			field_entry(field_dict, 'b', index_list, i)

		if indextotype[index_list[i]] == 'i':
			field_entry(field_dict, 'i', index_list, i)

	return field_dict


def wf2(exp, weightedFrequency):
	lis = re.compile(r'(\d+|\s+)').split(exp)
	tagType, Frequency = lis[0], lis[1]

	if tagType == "i" and tagType == key:
		freq = int(Frequency) * 50
		weightedFrequency += freq
	elif tagType == "t" and tagType == key:
		freq = int(Frequency) * 1000
		weightedFrequency += freq
	elif tagType == "c" and tagType == key:
		freq = int(Frequency) * 50
		weightedFrequency += freq
	elif tagType == "r" and tagType == key:
		freq = int(Frequency) * 50
		weightedFrequency += freq
	elif tagType == "e" and tagType == key:
		freq = int(Frequency) * 50
		weightedFrequency += freq
	elif tagType == "b" and tagType == key:
		freq = int(Frequency) * 5
		weightedFrequency += freq
	return weightedFrequency


def writeToFile2(global_dict, K):
	LandF_dict = {}
	for k in global_dict:
		try:
			weightedFrequency = 0
			n = len(global_dict[k])
			for x in global_dict[k]:
				try:
					x, idf, key = x.split("_")
					x = x.split(",")
					for y in x:
						try:
							weightedFrequency += wf2(y, weightedFrequency, key)
						except:
							continue
				except:
					continue
		except:
			continue
		if n in LandF_dict:
			LandF_dict[n][k] = float(log10(1 + weightedFrequency)) * float(idf)
		else:
			LandF_dict[n] = {k: float(log10(1 + weightedFrequency)) * float(idf)}

	count = K

	for k, v in sorted(LandF_dict.items(), reverse=True):
		for k1, v1 in sorted(v.items(), key=itemgetter(1), reverse=True):
			count -= 1
			outFile.write(str(k1) + ", " + str(docTitleMap[k1]))
			if count == 0:
				break
		if count == 0:
			break


def Field_query_words(query, K):
	query = query.lower()
	docs = {}
	global_dict = {}
	fieldDict = get_field_dict(query)

	for key in fieldDict.keys():
		querywords = fieldDict[key]
		for word in querywords:
			position = bisect(secondaryIndex, word)
			if position < 0:
				continue

			primaryFile = indexFolder + "index" + str(position) + ".txt"
			try:
				file = open(primaryFile, "r")
				data = file.read()
			except:
				print("Primary Index file is not present:" + str(file))

			pos_start = data.find(word + ":")
			if pos_start == -1:
				continue
			pos_end = data.find("\n", pos_start + 1)
			required_text = data[pos_start:pos_end]
			word, entry = required_text.split(":")
			posting_list = entry.split("|")
			No_Doc_word_found = len(posting_list)
			idf = log10(Total_docs / No_Doc_word_found)

			for i in posting_list:
				docID, entry = i.split("-")
				if (key not in entry):
					continue
				if docID in global_dict:
					global_dict[docID].append(entry + "_" + str(idf) + "_" + str(key))
				else:
					global_dict[docID] = [entry + "_" + str(idf) + "_" + str(key)]
	writeToFile2(global_dict, K)


path_to_index = "INDEX"
indexFolder = str(path_to_index)
if (indexFolder[-1:] != '/'):
	indexFolder += "/"
try:
	f = open("stopwords.txt", "r")
	for line in f:
		stopWords.add(line.strip())

	f = open(indexFolder + "secondaryIndex.txt", "r")
	for line in f:
		secondaryIndex.append(line.split()[0])
	f = open(indexFolder + "docTitleMap.txt", "r")
	for line in f:
		docID, titleMap = line.split("#")
		docTitleMap[docID] = titleMap
		Total_docs += 1

except:
	print(indexFolder + "Prerequisite files not found")
	sys.exit(1)

queryFile = open(str(sys.argv[1]), 'r')

for line in queryFile.readlines():
	line = line.split(',')
	K = int(line[0])
	query = line[1]
	start = timeit.default_timer()
	if ":" not in query:
		queryWords = query.split()
		# print(queryWords)
		Normal_query_words(queryWords, K)
	else:
		Field_query_words(query, K)
	stop = timeit.default_timer()
	dn = len(query.split(':'))
	if ":" in query:
		dn -= 1
	outFile.write(str(stop - start) + ", " + str((stop - start) / dn) + "\n\n")

outFile.close()
queryFile.close()
