#!/usr/bin/python3
from shaderwrapper import *
from neuralnet6 import NeuralNet
from testSnakeAI10 import * #function to test a given net
import pygame, time, copy, json
import random
from random import randint

testCount = 50 #was 10
popSize = 150
keepCount = 30
displayFrequency = 20
mode = "mutate"

def avg(a, b):
    return int((a + b) / 2)

random.seed(time.time()) #FIXME

size = (20, 20)
blockSize = 20

if displayFrequency > 0:
    pygame.init()
    screen = pygame.display.set_mode((size[0] * blockSize, size[1] * blockSize))

#TODO: use dynamic values in GLSL
shaderCode = ""
with open("snakeAI2.glsl", "r") as f:
    shaderCode = f.read()

swrapper = ShaderWrapper(shaderCode)

#d = []
#with open("../ai/net5.11a.json", "r") as f:
#    d = json.load(f)

nets = []
for i in range(popSize):
    newNet = NeuralNet(24, 16, 4)
    newNet.init()
    #newNet.weights = copy.deepcopy(d)
    nets.append(newNet)

genCount = 0
minimumScore = 60

perfData = []
netLog = []

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
    
    print("Generation %d" % genCount)
    
    data = []
    lengths = [len(nets[0].weights[0]), len(nets[0].weights[1]), len(nets[0].weights[2])]
    dataLen = lengths[0] + lengths[1] + lengths[2]
    
    data.append(popSize)
    data.append(dataLen)
    data.extend(lengths)
    data.append(randint(0, 100000)) #random seed
    
    for i in range(popSize):
        for sub in range(3):
            data.extend(nets[i].weights[sub])
    
    for i in range(popSize):
        data.append(0)
    
    #test nets on GPU
    dataOut = swrapper.run(data, len(data), popSize)
    results = dataOut[6 + (popSize * dataLen):]
    
    for i in range(popSize):
        nets[i].score = results[i]
    
    sortedNets = sorted(nets, key=lambda x: x.score)
    sortedNets.reverse()
    
    if sortedNets[0].score > minimumScore * testCount:
        if displayFrequency != 0 and genCount % displayFrequency == 0:
            score = testSnakeAI(sortedNets[0], size, blockSize, screen)
            print("%d, %d" % (int(sortedNets[0].score / testCount), score))
        else:
            print(int(sortedNets[0].score / testCount))
        
        #if the net is doing really well, dump the weights
        if (sortedNets[0].score / testCount) > 1000:
            print(json.dumps(sortedNets[0].weights))
    
    if len(sys.argv) >= 2:
        perfData.append(sortedNets[0].score)
        if genCount % 5 == 0:
            with open(sys.argv[1], "w") as f:
                for score in perfData:
                    f.write("%s\n" % score)
    
    if len(sys.argv) >= 3:
        netLog.append(sortedNets[0].weights)
        if genCount % 5 == 0:
            with open(sys.argv[2], "w") as f:
                json.dump(netLog, f)
    
    newNets = sortedNets[:keepCount]
    nets = []
    for i in range(popSize):
        newNet = NeuralNet(24, 16, 4)
        if mode == "genetic":
            parentA = newNets[randint(0, keepCount - 1)]
            parentB = newNets[randint(0, keepCount - 1)]
            
            for s in range(3):
                newNet.weights.append([])
                for i in range(len(parentA.weights[s])):
                    newNet.weights[s].append(avg(parentA.weights[s][i], parentB.weights[s][i]))
        
            #mutation
            #if the score is below the minimum score (the snake is doing nothing), heavily mutate it
            if sortedNets[0].score < minimumScore * testCount:
                newNet.mutate(3, 50) #randomize every 1 in 3 weights by +/- 50
            else:
                if randint(1, 5) == 1: #heavily mutate every 5th net
                    newNet.mutate(3, 70)
                else:
                    if genCount >= 100: #do lighter mutation in the later generations as the net gets more complex
                        newNet.mutate(8, 5)
                    else:
                        newNet.mutate(6, 10)
        elif mode == "genetic2":
            parentA = newNets[randint(0, keepCount - 1)]
            parentB = newNets[randint(0, keepCount - 1)]
            
            threshold = randint(1, 100)
            for s in range(3):
                newNet.weights.append([])
                for i in range(len(parentA.weights[s])):
                    if randint(1, 100) < threshold:
                        newNet.weights[s].append(parentA.weights[s][i])
                    else:
                        newNet.weights[s].append(parentB.weights[s][i])
        
            #mutation
            newNet.mutate(50, 50)
        elif mode == "mutate":
            parent = newNets[randint(0, keepCount - 1)]
            newNet.weights = copy.deepcopy(parent.weights)
        
            #mutation
            #if the score is below the minimum score (the snake is doing nothing), heavily mutate it
            if sortedNets[0].score < minimumScore * testCount:
                newNet.mutate(3, 50) #randomize every 1 in 3 weights by +/- 50
            else:
                if randint(1, 5) == 1: #heavily mutate every 5th net
                    newNet.mutate(3, 70)
                else:
                    if genCount >= 100: #do lighter mutation in the later generations as the net gets more complex
                        newNet.mutate(8, 5)
                    else:
                        newNet.mutate(6, 10)
        else:
            print("Error: Invalid mode") #FIXME - stderr
            exit(1)
        
        nets.append(newNet)
    
    genCount += 1
