#!/usr/bin/python3
import random
import json
from copy import deepcopy
import pymongo
import pprint

#parameters which define the mongoDB and the document template
DATABASE='apidb'
COLLECTION='cells'
sdict={ "thickness": 0,
        "size": 0,
        "shape": 0,
        "adhesion": 0,
        "single_size": 0,
        "nuclei": 0,
        "chromatin": 0,
        "nucleoli": 0,
        "mitoses": 0,
        "class": 0}

def pullRandomSamplesMongo(HOST='localhost',PORT=27017):
    mclient = pymongo.MongoClient(HOST,PORT)
    db = mclient[DATABASE]
    collection = db[COLLECTION]
    documents=[]
    records=collection.find({});
    for document in records:
        document.pop('_id')
        documents.append(document)
    sample=random.sample(documents,5)
    return(sample)

def pullRandomSamples():
    th=open('/var/www/html/cells/data/bc_test.csv','r')
    test_data=th.readlines()
    th.close()
    records=[]
    for line in test_data:
        records.append(line.strip("\n").split(","))
    sample=random.sample(records,5)
    jobjs=[]
    for record in sample:
        jdict=deepcopy(sdict)
        i=0
        for keyval in jdict.keys():
            jdict[keyval]=record[i]
            i+=1
        jobjs.append(jdict)
    return(jobjs)

def mongoInsertOne(document, HOST='localhost', PORT=27017):
    mclient = pymongo.MongoClient(HOST,PORT)
    db = mclient[DATABASE]
    collection = db[COLLECTION]
    try:
        collection.insert_one(document)
        return(True)
    except Exception as e:
        print(str(e))
        return(False)

def mongoInsertMany(documents, HOST='localhost', PORT=27017):
    mclient = pymongo.MongoClient(HOST,PORT)
    db = mclient[DATABASE]
    collection = db[COLLECTION]
    try:
        collection.insert_many(documents)
        return(True)
    except Exception as e:
        print(str(e))
        return(False)
