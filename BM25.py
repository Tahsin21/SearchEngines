import json
import math

indexFiles = input("Where is the directory of the Index File: ")
topicPath = input("Directory of the query .txt file: ")
resultFileName = input("Name of file that will output the results: ")

def tokenize(text):
    tokens = []
    text = text.lower()
    start = 0

    for i in range(len(text)):
        c = text[i]
        if not c.isalnum():
            if start != i:
                token = text[start:i]
                tokens.append(token)
            start = i + 1

    if start != i:
        tokens.append(text[start:])

    return tokens

def bm25(docFreq, termFreq, docLen, k1, b, N, avgdl):
    k = k1 * ((1-b) + b * (docLen/avgdl))
    first = termFreq / (k + termFreq)
    second = math.log((N - docFreq + 0.5)/(docFreq + 0.5))
    return first * second

metaPath = indexFiles + "/metadata.txt"
with open(metaPath, 'r') as file:
    data = json.load(file)

invPath = indexFiles + "/invIndex.txt"
with open(invPath, 'r') as file:
    invIndex = json.load(file)

termIntPath = indexFiles + "/termToInt.txt"
with open(termIntPath, 'r') as file:
    termInt = json.load(file)

doclengthPath = indexFiles + "/doc-lengths.txt"
with open(doclengthPath, 'r') as file:
    docLenMap = json.load(file)


k1 = 1.2
b = 0.75
N = len(docLenMap)
avgdl = sum(docLenMap.values()) / N

topicDict = {}
with open(topicPath, 'r') as file:
    lines = file.readlines()
    for i in range(0,len(lines) - 1,2):
        key = lines[i].strip()
        value = tokenize(lines[i + 1].strip())
        topicDict[key] = value

searchResults = {}
for topicID, queryTokens in topicDict.items():
    docScores = {}
    for term in queryTokens:
        if term in termInt:
            termID = str(termInt[term])
            if termID in invIndex:
                docFreq = len(invIndex[termID])
                for docTuple in invIndex[termID]:
                    docID = docTuple[0]
                    termFreq = docTuple[1]
                    docLen = docLenMap.get(str(docID))
                    if docID not in docScores:
                        docScores[docID] = 0
                    docScores[docID] += bm25(docFreq, termFreq, docLen, k1, b, N, avgdl)
        
    sortedDocs = sorted(docScores.items(), key=lambda x: x[1], reverse=True)
    searchResults[topicID] = sortedDocs

runTag = "t27hassaBM25"
resultsPath = indexFiles + "/" + resultFileName

with open(resultsPath, 'w') as file:
    for topicID, scoredDocs in searchResults.items():
        rank = 1
        for docID, score in scoredDocs:
            if rank <= 1000: 
                docno = data[str(docID)]['DOCNO']
                file.write(f"{topicID} Q0 {docno} {rank} {score:.3f} {runTag}\n")
                rank += 1 
            else:
                break


