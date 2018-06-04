#!/usr/bin/python3

import pygame
from random import randint
from math import sqrt

class SnakeGame:
    size = (20, 20)
    blockSize = 20
    data = []
    motion = (1, 0)
    grow = 0
    
    food = (0, 0)
    def getFood(self):
        i = 0
        while i < 10000:
            ok = True
            
            food = (randint(0, self.size[0] - 1), randint(0, self.size[1] - 1))
            
            dist = sqrt(pow(self.food[0] + self.data[0][0], 2) + pow(self.food[1] + self.data[0][1], 2))
            if dist < 6:
                ok = False
            
            if ok:
                for segment in self.data:
                    if segment == food:
                        ok = False
            
            if ok:
                return food
            i += 1
        #give up
        return food #FIXME
    
    def __init__(self, size=(20, 20), blockSize=20):
        #TODO: clean up/rearrange
        self.size = size
        self.blockSize = blockSize
        self.data = []
        self.motion = (1, 0)
        self.grow = 0
        for i in range(3, 0, -1):
            self.data.append((i, int(size[1] / 2)))
        self.food = self.getFood()
    
    def processFrame(self):
        length = len(self.data)
        newPos = (self.data[0][0] + self.motion[0], self.data[0][1] + self.motion[1])
        
        if newPos == self.food:
            self.grow += 1
            self.food = self.getFood()
        
        self.data.insert(0, newPos)
        if self.grow == 0:
            del self.data[-1]
        else:
            self.grow -= 1
            length += 1
        
        if newPos[0] < 0 or newPos[0] >= self.size[0] or newPos[1] < 0 or newPos[1] >= self.size[1]:
            return False #out of bounds
        
        for segment in self.data[1:]:
            if segment == newPos:
                return False #collision with self
        
        return True
    
    def go(self, direction):
        """
           0
         3   1
           2
        """
        if direction == 0:
            self.motion = (0, -1)
        elif direction == 1:
            self.motion = (1, 0)
        elif direction == 2:
            self.motion = (0, 1)
        elif direction == 3:
            self.motion = (-1, 0)
    
    def render(self):
        surface = pygame.Surface((self.size[0] * self.blockSize, self.size[1] * self.blockSize))
        surface.fill((0, 0, 0))
        
        blankBox = pygame.Surface((self.blockSize, self.blockSize))
        blankBox.fill((0, 0, 0))
        #pygame.draw.rect(blankBox, (255, 255, 255), pygame.Rect(1, 1, self.blockSize - 2, self.blockSize - 2), 2)
        
        filledBox = pygame.Surface((self.blockSize, self.blockSize))
        filledBox.fill((255, 255, 255))
        #pygame.draw.rect(filledBox, (0, 0, 0), pygame.Rect(1, 1, self.blockSize - 2, self.blockSize - 2), 2)
        
        foodBox = pygame.Surface((self.blockSize, self.blockSize))
        foodBox.fill((255, 0, 0))
        #pygame.draw.rect(foodBox, (0, 0, 0), pygame.Rect(1, 1, self.blockSize - 2, self.blockSize - 2), 2)
        
        for y in range(self.size[1]):
            for x in range(self.size[0]):
                surface.blit(blankBox, (x * self.blockSize, y * self.blockSize))
        
        for segment in self.data:
            surface.blit(filledBox, (segment[0] * self.blockSize, segment[1] * self.blockSize))
        
        surface.blit(foodBox, (self.food[0] * self.blockSize, self.food[1] * self.blockSize))
        
        return surface
