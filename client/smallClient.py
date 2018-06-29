import requests
import codecs
import locale
import math
import time
import numpy as np

# Run with Python 3

url = 'http://localhost:8888/translator/translate'

def sendRequest(data):
     response = requests.post(url, data=data)
     return response
     #print(response.json())

def shortenSentence(sentence, averLen):
    splitSentence = sentence.split(" ")
    newSentence = ""
    for i in range(averLen):
        newSentence = newSentence + " " + splitSentence[i]
    return newSentence

def sendBatch(sentencesFiltered, batchsize):
    latencies = []
    for i in range(0, (len(sentencesFiltered) - batchsize), batchsize):
        #print(i)
        data = '''['''
        for j in range(0, (batchsize)):
            data = data + '''{"id": 100, "src": "'''
            #print(j)
            data = data + sentencesFiltered[(i+j)] + '''"}'''
            if (j != (batchsize - 1) ):
                data = data + ","
        data = data + ''']'''
        start = time.time()
        result = sendRequest(data)
        end = time.time()
        #print("Time: " + str(end - start))
        #print(result)
        if (result.status_code == 200):
            latencies.append((end - start))

    return latencies

fullFilePath = '/home/kate/OpenNMT-py/client/benchmarkdata/news.2016.en.shuffled'

testFilePath = '/home/kate/OpenNMT-py/client/benchmarkdata/news.2016.en.shuffled.short'

shortFilePath = '/home/kate/OpenNMT-py/client/benchmarkdata/news.2016.en.shuffled.short.2'

file = open(shortFilePath, 'rb')

sentences = []
lengthSum = 0
lengthCount = 0

for bline in file:
    try:
        line = bline.decode('utf-8')
        print(lengthCount)
        print(line)
        sentences.append(line)
        lengthCount = lengthCount + 1
        lengthSum = lengthSum + len(line.split(" "))
    except (UnicodeEncodeError, UnicodeDecodeError):
        continue

averageLength = math.floor(lengthSum/lengthCount)
print(averageLength)
sentencesFiltered = []
for i in sentences:
    if (len(i.split(" ")) > averageLength):
        sentencesFiltered.append(shortenSentence(i, averageLength))
    print(i)

#for j in sentencesFiltered:
#    print(j)

file.close()


data = '''[
  {
  	"id": 100,
    "src": "Hello my name is"
  },
  {
    "id": 100,
    "src": "What's up?"
  }
]'''
#for k in sentencesFiltered:
#    data = '''[{"id": 100, "src": "''' + k + '''"}]'''
#    print(data)
#    start = time.time()
#    sendRequest(data)
#    end = time.time()
#    print("Time: " + str(end - start))

for batch in [1,2,4,5,8,10,15,16,20]:
    print("Batch size = " + str(batch))
    batchsize = batch
    latencies = sendBatch(sentencesFiltered, batchsize)
    print(latencies)
    latenciesAr = np.array(latencies)
    print(latenciesAr)
    if (len(latencies) != 0):
        print("95th percentile " + str(np.percentile(latenciesAr, 95)))
        print("99th percentile " + str(np.percentile(latenciesAr, 99)))
        print("Median " + str(np.percentile(latenciesAr, 50)))
        print("Average " + str(np.average(latenciesAr)))
