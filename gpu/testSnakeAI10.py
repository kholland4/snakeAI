#!/usr/bin/python3
import pygame, time
from snake2 import SnakeGame

def testSnakeAI(net, size=(20, 20), blockSize=20, screen=None): #TODO: kwargs?
    #TODO: dynamic code that can handle varying sizes
    game = SnakeGame(size, blockSize)
    frameCount = 0
    
    lastDir = 1
    foodBonus = 0
    shortestDistanceToFood = 25
    
    while frameCount < 10000:
        inputs = []
        for i in range(28):
            inputs.append(0)
        
        #7 0 1
        #6   2
        #5 4 3
        probeDirMap = [(0, -1), (1, -1), (1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1)]
        
        for i in range(8):
            #distance to self
            move = probeDirMap[i]
            dist = 0
            pos = game.data[0]
            while True:
                pos = (pos[0] + move[0], pos[1] + move[1])
                for segment in game.data:
                    if segment == pos:
                        break
                dist += 1
                if dist == 25:
                    break
            
            inputs[i] = dist * 4
        
        for i in range(8):
            #distance to walls
            move = probeDirMap[i]
            #move = probeDirMap[lastDir * 2] #FIXME: test this - only looks in current direction
            dist = 0
            pos = game.data[0]
            while True:
                pos = (pos[0] + move[0], pos[1] + move[1])
                if pos[0] < 0 or pos[0] >= game.size[0] or pos[1] < 0 or pos[1] >= game.size[1]:
                    break
                dist += 1
            inputs[i + 8] = dist * 2
        
        for i in range(8):
            #distance to food
            move = probeDirMap[i]
            dist = 0
            pos = game.data[0]
            while True:
                pos = (pos[0] + move[0], pos[1] + move[1])
                if pos[0] < 0 or pos[0] >= game.size[0] or pos[1] < 0 or pos[1] >= game.size[1]:
                    dist = 25
                    break
                dist += 1
                if pos == game.food:
                    break
            if dist < shortestDistanceToFood:
                shortestDistanceToFood = dist
            inputs[i + 16] = dist * 2
            #inputs[i + 16] = 100
        
        for i in range(4):
            #inputs are inverted
            if lastDir == i:
                inputs[i + 24] = 0
            else:
                inputs[i + 24] = 100
        
        newDir = lastDir
        outputs = net.process(inputs)
        for i in range(4):
            if outputs[i]:
                newDir = i
        
        if not (lastDir == 0 and newDir == 2) and not (lastDir == 2 and newDir == 0) and not (lastDir == 1 and newDir == 3) and not (lastDir == 3 and newDir == 1):
            game.go(newDir)
        else:
            newDir = lastDir
        
        if lastDir != newDir:
            lastDir = newDir
        
        lfood = game.food
        
        ok = game.processFrame()
        if not ok:
            break
        
        if game.food != lfood: #FIXME
            foodBonus += 25 #works now that we're not using len(game.data) in the score calculation
            shortestDistanceToFood = 25
        
        if screen != None:
            screen.blit(game.render(), (0, 0))
            pygame.display.flip()
            time.sleep(0.01)
        
        frameCount += 1
    
    return ((25 - shortestDistanceToFood) * 2) + (foodBonus * 3) #reward extra for getting the food
