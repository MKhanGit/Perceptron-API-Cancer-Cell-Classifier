#!/usr/bin/python3
#Author: Mohsin Khan
#Webpage front-end for Neural Network Classifier connected to MongoDB
#using PyMongo driver

import cgi
import cgitb
import hashlib
import sys
import pymongo
import pprint
import datetime
from mongoFunctions import pullRandomSamples, pullRandomSamplesMongo

print("content-type: text/html\r\n\r\n")
cgitb.enable()

#predefined mongo db and collection for the apidb
DATABASE='apidb'
COLLECTION='digits'
#Pull random samples to test the network with. Two methods here, one using a
#text based db and the other using mongo.

#random_samples=pullRandomSamples()
random_samples=pullRandomSamplesMongo()

jscript = '<script>var text = ' + str(random_samples) + ';</script>'
print(jscript)

with open("./main.html",'r') as fh:
    html = fh.read()
print(html)
