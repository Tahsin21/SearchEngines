import json

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

def mergeIntersection(list):
    result = list[0]
    for i in list[1:]:
        result = mergeTwoLists(result, i)
    return result

def mergeTwoLists(list1, list2):
    result = []
    i, j = 0, 0

    while i < len(list1) and j < len(list2):
        if list1[i] == list2[j]:
            result.append(list1[i])
            i += 1
            j += 1
        elif list1[i] < list2[j]:
            i += 1
        else:
            j += 1
    return result

metaPath = indexFiles + "/metadata.txt"
with open(metaPath, 'r') as file:
    data = json.load(file)

invPath = indexFiles + "/invIndex.txt"
with open(invPath, 'r') as file:
    invIndex = json.load(file)

termIntPath = indexFiles + "/termToInt.txt"
with open(termIntPath, 'r') as file:
    termInt = json.load(file)

topicDict = {}
with open(topicPath, 'r') as file:
    lines = file.readlines()
    for i in range(0,len(lines) - 1,2):
        key = lines[i].strip()
        value = tokenize(lines[i + 1].strip())
        topicDict[key] = value

searchResults = {}
for topicID, queryTokens in topicDict.items():
    postingsPerTopic = []

    for word in queryTokens:
        if word in termInt:
            tempTerm = str(termInt[word])
            docID = []
            for docTuple in invIndex[tempTerm]:
                docID.append(data[str(docTuple[0])].get('DOCNO'))
            postingsPerTopic.append(docID)
    searchResults[topicID] = mergeIntersection(postingsPerTopic)

runTag = "t27hassaAND"
resultsPath = indexFiles + "/" + resultFileName

with open(resultsPath, 'w') as file:
    for topicID, docNos in searchResults.items():
        rank = 1
        score = len(docNos) - 1

        for docno in docNos:
            file.write(f"{topicID} Q0 {docno} {rank} {score} {runTag}\n")
            rank += 1
            score -= 1
