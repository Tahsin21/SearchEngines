import json
import math
import re
import time
import heapq

indexFiles = input("Where is the directory of the Index File: ")

def tokenize(text):
    tokens = []
    text = text.lower()
    for i in range(len(text)):
        if text[i].isalnum():
            start = i
            while i < len(text) and text[i].isalnum():
                i += 1
            tokens.append(text[start:i])
    return tokens

def bm25(docFreq, termFreq, docLen, k1, b, N, avgdl):
    k = k1 * ((1-b) + b * (docLen/avgdl))
    first = termFreq / (k + termFreq)
    second = math.log((N - docFreq + 0.5) / (docFreq + 0.5))
    return first * second

def makeFileName(str):
    docNo_regex = re.compile(r'^LA(\d{2})(\d{2})(\d{2})-(\d+)$')

    if docNo_regex.search(str):
        month = docNo_regex.search(str).group(1)
        day = docNo_regex.search(str).group(2)
        year = docNo_regex.search(str).group(3)
        seq = docNo_regex.search(str).group(4)
        return("/" + year + "/" + month + "/" + day + "/" + str + '.txt')

def getDoc(docNo):
    newPath = indexFiles + makeFileName(docNo)
    print("Raw Document:")
    with open(newPath, 'r') as file:
        for line in file:
            print(line.strip())

def processText(docText):
    textContent = re.search(r'<TEXT\b[^>]*>(.*?)</TEXT>', docText, re.DOTALL)
    if textContent:
        text = textContent.group(1)

        text = text.replace('\n', '')
        clean = re.compile('<.*?>')
        text = re.sub(clean, '', text)

        sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a.z]\.)(?<=\.|\?)\s', text)
    return sentences

def scoreSentences(sentences, queryTokens):
    heap = []
    for i, x in enumerate(sentences):
        l = 0
        c = 0
        d = 0
        k = 0
        
        tokenizedSentence = tokenize(x)
        querySet = set(queryTokens)

        if i == 1:
            l = 2
        elif i == 2:
            l = 1
        else:
            l = 0

        for token in queryTokens:
            c += tokenizedSentence.count(token)    
        
        for word in querySet:
            d += tokenizedSentence.count(word)

        k = contiguousRun(tokenizedSentence, queryTokens)

        score = l + c + d + k
        heapq.heappush(heap, (-score, x))
    return heap

def contiguousRun(tokenizedSentence, queryTokens):
    longestRun = 0
    currentRun = 0
    for word in tokenizedSentence:
        if word in queryTokens:
            currentRun += 1
            longestRun = max(longestRun, currentRun)
        else:
            currentRun = 0
    return longestRun

def getBestSnippet(docText, queryTokens):
    maxHeap = scoreSentences(docText, queryTokens)
    _, topSentence = heapq.heappop(maxHeap)
    
    return topSentence

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

print("Data has been loaded!")

while True:
    query = input("Please enter a query (Input 'Q' to quit the program): ")
    if query.upper() == "Q":
        exit()
    start = time.time()
    queryTokens = tokenize(query)

    docScores = {}

    for term in queryTokens:
        if term in termInt:
            termID = str(termInt[term])
            if termID in invIndex:
                docFreq = len(invIndex[termID])
                for docTuple in invIndex[termID]:
                    docID, termFreq = docTuple
                    docLen = docLenMap.get(str(docID))
                    if docID not in docScores:
                        docScores[docID] = 0
                    docScores[docID] += bm25(docFreq, termFreq, docLen, k1, b, N, avgdl)

    sortedDocs = sorted(docScores.items(), key=lambda x: x[1], reverse=True)[:10]

    end = time.time()

    duration = end - start

    for rank, (docID, _) in enumerate(sortedDocs, 1):
        docData = data.get(str(docID))
        title = docData.get('Title')
        date = docData.get('Date')
        docNo = docData.get('DOCNO')
        print(f"{rank}: {title}; ({date})")

        docPath = indexFiles + makeFileName(docNo)
        with open(docPath, 'r') as file:
            docText = file.read()
            textContent = processText(docText)
            snippet = getBestSnippet(textContent, queryTokens)
            print(f"{snippet} ({docNo})\n")

    print(f"Retrieval took {duration:.3f} seconds.")

    while True:
        view = input("Input Rank of Document You Would Like to View (N for new query, Q to quit): ")
        if view.upper() == "N":
            break
        elif view.upper() == "Q":
            exit()
        
        try:
            intView = int(view)
            if intView in range(1, len(sortedDocs) + 1):
                docID = sortedDocs[intView - 1][0]
                docData = data.get(str(docID))
                docNo = docData.get('DOCNO')
                getDoc(docNo)
            else:
                print("Please input a valid rank within the range of documents displayed.")
        except ValueError:
            print("Please input a valid rank.")


