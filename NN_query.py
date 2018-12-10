#!/usr/bin/python
#Author: Mohsin Khan

#Querying a trained network and return result to web ui
import cgitb
import cgi
import numpy
import scipy.special
import dill
import pickle
import sys
print("content-type: text/html\r\n\r\n")
cgitb.enable()
form = cgi.FieldStorage()
try:
    sys_inputs=[form["thickness"].value,
                form["size"].value,
                form["shape"].value,
                form["adhesion"].value,
                form["single_size"].value,
                form["nuclei"].value,
                form["chromatin"].value,
                form["nucleoli"].value,
                form["mitoses"].value,
                form["class"].value]
    if len(sys_inputs)<10:
        print("invalid parameter set.")
        sys.exit(0)
except:
    print("invalid parameter set.")
    sys.exit(0)

class neuralNetwork:

    def __init__(self, inputnodes, hiddennodes, outputnodes, learningrate):
        self.inodes = inputnodes
        self.hnodes = hiddennodes
        self.onodes = outputnodes
        self.wih = numpy.random.normal(0.0, pow(self.hnodes, -0.5), (self.hnodes, self.inodes))
        self.who = numpy.random.normal(0.0, pow(self.onodes, -0.5), (self.onodes, self.hnodes))
        self.lr = learningrate
        # activation function is the sigmoid function
        self.activation_function = lambda x: scipy.special.expit(x)
        pass

    def train(self, inputs_list, targets_list):
        # convert inputs list to 2d array
        inputs = numpy.array(inputs_list, ndmin=2).T
        targets = numpy.array(targets_list, ndmin=2).T
        # calculate signals into hidden layer
        hidden_inputs = numpy.dot(self.wih, inputs)
        # calculate the signals emerging from hidden layer
        hidden_outputs = self.activation_function(hidden_inputs)
        # calculate signals into final output layer
        final_inputs = numpy.dot(self.who, hidden_outputs)
        # calculate the signals emerging from final output layer
        final_outputs = self.activation_function(final_inputs)
        # output layer error is the (target - actual)
        output_errors = targets - final_outputs
        # hidden layer error is the output_errors, split by weights, recombined at hidden nodes
        hidden_errors = numpy.dot(self.who.T, output_errors)
        # update the weights for the links between the hidden and output layers
        self.who += self.lr * numpy.dot((output_errors * final_outputs * (1.0 - final_outputs)), numpy.transpose(hidden_outputs))
        # update the weights for the links between the input and hidden layers
        self.wih += self.lr * numpy.dot((hidden_errors * hidden_outputs * (1.0 - hidden_outputs)), numpy.transpose(inputs))
        pass

    def query(self, inputs_list):
        # convert inputs list to 2d array
        inputs = numpy.array(inputs_list, ndmin=2).T
        # calculate signals into hidden layer
        hidden_inputs = numpy.dot(self.wih, inputs)
        # calculate the signals emerging from hidden layer
        hidden_outputs = self.activation_function(hidden_inputs)
        # calculate signals into final output layer
        final_inputs = numpy.dot(self.who, hidden_outputs)
        # calculate the signals emerging from final output layer
        final_outputs = self.activation_function(final_inputs)
        return final_outputs

#MAIN RUNTIME HERE
neural_network_memories = open("Neural_Network_Data.bin", 'r')
n = pickle.load(neural_network_memories)
neural_network_memories.close()

# load the test from command line arguments passed by POST to server
correct_label = int(sys_inputs[9])
inputs = numpy.asfarray(sys_inputs[:9])
outputs = n.query(inputs)
label = numpy.argmax(outputs)

#based on class 0 or 1, print the prediction of the Network
identifier=["<font style='color:green;'>Benign</font>","<font style='color:red;'>Malignant</font>"]
print(identifier[label])

if (label == correct_label):
# network's answer matches correct answer send appropriate label
    print("<br><font style='font-size:14px;color:darkgreen;'>(Network was correct)</font>")
else:
    print("<br><font style='font-size:14px;color:red;'>(Network was not correct)</font>")
