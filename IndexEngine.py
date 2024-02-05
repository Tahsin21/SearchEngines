import re
import os
import json
import gzip

gzipFile = input("Path of the gzip file: ")
storeFiles = input("Path to where they will be placed: ")

if os.path.exists(storeFiles):
    raise ValueError("Directory Already Exists")

if len(gzipFile) == 0 or len(storeFiles) == 0:
    raise TypeError("No input(s) was given: This program reads a gzipped file and parses through the entire document, filtering each document into its own .txt file based on starting and ending <doc> tag")

def saveDoc(newDoc):
    filePath = storeFiles + makeFileName(newDoc)
    directory = os.path.split(filePath)

    os.makedirs(directory[0], exist_ok = True)

    with open(filePath, 'w') as file:
        for item in newDoc:
            file.write(item) 
        
def makeFileName(newDoc):
    docNo_regex = re.compile(r'<DOCNO>\s*(LA(\d{2})(\d{2})(\d{2})-(\d+))\s*</DOCNO>')

    doc_str = ''.join(newDoc)

    if docNo_regex.search(doc_str):
        docno = docNo_regex.search(doc_str).group(1)
        month = docNo_regex.search(doc_str).group(2)
        day = docNo_regex.search(doc_str).group(3)
        year = docNo_regex.search(doc_str).group(4)
        seq = docNo_regex.search(doc_str).group(5)
        return("/" + year + "/" + month + "/" + day + "/" + docno + '.txt')

def extractMeta(newDoc):
    date = ''
    title = ''
    docno = ''
    text = ''
    graphic = ''

    docNo_regex = re.compile(r'<DOCNO>\s*(LA(\d{2})(\d{2})(\d{2})-(\d+))\s*</DOCNO>')
    title_regex = re.compile(r'<HEADLINE>([\s\S]*?)<\/HEADLINE>')
    text_regex = re.compile(r'<TEXT>([\s\S]*?)<\/TEXT>')
    graphic_regex = re.compile(r'<GRAPHIC>([\s\S]*?)<\/GRAPHIC>')
    
    doc_str = ''.join(newDoc)

    if docNo_regex.search(doc_str):
        docno = docNo_regex.search(doc_str).group(1)
        month = docNo_regex.search(doc_str).group(2)
        day = docNo_regex.search(doc_str).group(3)
        year = docNo_regex.search(doc_str).group(4)
        date = month + "-" + day + "-" + year

    if title_regex.search(doc_str):
        title = title_regex.search(doc_str).group(1).replace('\n', '').replace('<P>', '').replace('</P>', '')
    
    if text_regex.search(doc_str):
        text = text_regex.search(doc_str).group(1).replace('\n', '').replace('<P>', '').replace('</P>', '')
    
    if graphic_regex.search(doc_str):
        graphic = graphic_regex.search(doc_str).group(1).replace('\n', '').replace('<P>', '').replace('</P>', '')

    return(docno,date,title,text,graphic)

def writeMeta(data):
    filePath = storeFiles + "/metadata.txt"

    os.makedirs(storeFiles, exist_ok = True)

    with open(filePath, 'w') as file:
        file.write(json.dumps(data)) 

def writeTermtoInt(data):
    filePath = storeFiles + "/termToInt.txt"

    os.makedirs(storeFiles, exist_ok = True)

    with open(filePath, 'w') as file:
        file.write(json.dumps(data)) 

def writeintToTerm(data):
    filePath = storeFiles + "/intToTerm.txt"

    os.makedirs(storeFiles, exist_ok = True)

    with open(filePath, 'w') as file:
        file.write(json.dumps(data)) 

def writeDocLen(data):
    filePath = storeFiles + "/doc-lengths.txt"

    os.makedirs(storeFiles, exist_ok = True)

    with open(filePath, 'w') as file:
        file.write(json.dumps(data)) 

def writeInvIndex(data):
    filePath = storeFiles + "/invIndex.txt"

    os.makedirs(storeFiles, exist_ok = True)

    with open(filePath, 'w') as file:
        file.write(json.dumps(data)) 

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

def tokensToID(tokens, lexicon):
    tokenIDs = []
    tokenToID = {}

    for token in tokens:
        if token in lexicon:
            tokenIDs.append(lexicon[token])
        else:
            lexicon[token] = len(lexicon)
            tokenIDs.append(lexicon[token])

        tokenToID[token] = lexicon[token]
    return tokenIDs, tokenToID

def countWords(tokenIDs):
    wordCounts = {}
    for id in tokenIDs:
        if id in wordCounts:
            wordCounts[id] += 1
        else:
            wordCounts[id] = 1
    return wordCounts

def AddtoPostings(wordCounts, docID, invIndex):
    for termID in wordCounts:
        count = wordCounts[termID]
        postings = invIndex.get(termID, [])
        postings.append((docID, count))
        invIndex[termID] = postings
    
    return invIndex
            
doc = []
data = {}
lexicon = {}
invIndex = {}
docLength_data = {}
allTokenIDMap = {}
allTokenIDs = []
counter = 0
text = ""
tokens = []
tokenIDs = []

#with open(r"/Users/tahsinhassan/Documents/School/3B/MSCI 541/Assignments/A1/SmallDoc.txt", 'r') as finder:
with gzip.open(gzipFile, 'rt') as finder:
    for line in finder:
        doc.append(line)
        if line.strip() == '</DOC>':  # Stripping leading/trailing whitespaces to match correctly
            docno,date,title,text,graphic = extractMeta(doc)
            data[counter] = {'DOCNO': docno, 'Date': date, 'Title': title}
            text = title + " " + text + " " + graphic
            tokens = (tokenize(text))
            tokenIDs, tokenIDMap = tokensToID(tokens, lexicon)
            allTokenIDMap.update(tokenIDMap)
            allTokenIDs.append(tokenIDs)
            wordCounts = countWords(tokenIDs)
            invIndex = AddtoPostings(wordCounts, counter, invIndex)
            docLength_data[counter] = len(tokens)
            counter += 1
            saveDoc(doc)
            doc = []

allTermIDMap = {a: b for b, a in allTokenIDMap.items()}

writeMeta(data)
writeDocLen(docLength_data)
writeTermtoInt(allTokenIDMap)
writeintToTerm(allTermIDMap)
writeInvIndex(invIndex)
