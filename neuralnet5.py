#!/usr/bin/python3
import sys
from random import randint

#Artificial neural network
#Weights are integers between 1 and 100 - TODO: should really be 0 - 100

class NeuralNet:
    weights = []
    numInput = 0
    numHidden = 0
    numOutput = 0
    score = 0
    
    thresholdInput = 0.2
    thresholdHidden = 0.15
    thresholdOutput = 0.15
    
    hiddenLinkCount = 4
    outputLinkCount = 4
    
    hiddenTrigMap = []
    outputTrigMap = []
    
    def __init__(self, numInput, numHidden, numOutput):
        self.numInput = numInput
        self.numHidden = numHidden
        self.numOutput = numOutput
        self.weights = []
        self.score = 0
        self.hiddenTrigMap = []
        self.outputTrigMap = []
        
        #Generate internal structure of net
        
        #Mapping of connections between input and hidden neurons
        #Each hidden neuron connects to <hiddenLinkCount> nearby input neurons
        rangeToCover = self.numInput - self.hiddenLinkCount
        step = rangeToCover / self.numHidden
        n = 0
        for i in range(self.numHidden):
            w = []
            for m in range(self.hiddenLinkCount):
                w.append(n + m)
            self.hiddenTrigMap.append(w)
            
            #FIXME
            if n <= i * step: #less than/equal to target
                n += 2
            elif n > i * step: #greater than target
                n += 1
            n = min(n, rangeToCover)
        
        #Mapping of connections between hidden and output neurons
        #Each hidden neuron connects to <hiddenLinkCount> neurons
        #Connections are spaced out by <numHidden> / <outputLinkCount> units
        #FIXME - doesn't work for all configurations
        spacing = int(self.numHidden / self.outputLinkCount)
        
        offset = 0
        for i in range(self.numOutput):
            w = []
            n = offset
            for m in range(self.outputLinkCount):
                w.append(n)
                n += spacing
            self.outputTrigMap.append(w)
            
            offset += 1
    def init(self):
        #generate weights
        #this init() function is only used for the initial population
        #uses flat arrays for easier genetic crossover / whateever other algorithm
        
        inputNeurons = []
        for i in range(self.numInput):
            inputNeurons.append(randint(1, 100))
        self.weights.append(inputNeurons)
        
        hiddenNeurons = []
        for i in range(self.numHidden * self.hiddenLinkCount):
            hiddenNeurons.append(randint(1, 100))
        self.weights.append(hiddenNeurons)
        
        outputNeurons = []
        for i in range(self.numOutput * self.outputLinkCount):
            outputNeurons.append(randint(1, 100))
        self.weights.append(outputNeurons)
    
    def process(self, inputs):
        #Inputs is a list of integers from 0 to 100 corresponding to each input neuron
        
        #Input neurons
        inputsFired = []
        for i in range(self.numInput):
            #only one input
            amount = ((100 - inputs[i]) / 100) * (self.weights[0][i] / 100)
            inputsFired.append(amount >= self.thresholdInput)
        
        hiddenFired = []
        for i in range(self.numHidden):
            amount = 0
            for n in range(self.hiddenLinkCount):
                inputState = inputsFired[self.hiddenTrigMap[i][n]]
                weight = self.weights[1][(i * self.hiddenLinkCount) + n]
                amount += int(inputState * (weight / 100))
            amount = amount / self.hiddenLinkCount
            hiddenFired.append(amount >= self.thresholdHidden)
        
        outputFired = []
        for i in range(self.numOutput):
            amount = 0
            for n in range(self.outputLinkCount):
                inputState = hiddenFired[self.outputTrigMap[i][n]]
                weight = self.weights[2][(i * self.outputLinkCount) + n]
                amount += int(inputState * (weight / 100))
            amount = amount / self.outputLinkCount
            outputFired.append(amount >= self.thresholdOutput)
        
        return outputFired
    
    def mutate(self, amount=8, level=20):
        for s in range(3):
            for i in range(len(self.weights[s])):
                if randint(1, amount) == 1:
                    self.weights[s][i] = min(max(self.weights[s][i] + randint(-level, level), 1), 100)
