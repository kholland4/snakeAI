#!/usr/bin/python3
from OpenGL.GLUT import *

from OpenGL.GL import *
from OpenGL.GL import shaders

from numpy import array

import ctypes

class ShaderWrapper:
    sizeOfInt = 4 #hopefully
    
    shader = None
    
    def __init__(self, shaderCode):
        self.initGLUT()
        self.initShader(shaderCode)
    
    def array_type(self, data):
        return array(data, 'i')

    def initGLUT(self):
        glutInit()
        glutInitDisplayMode(GLUT_RGBA)
        glutInitWindowSize(400, 400)
        
        glutInitContextVersion(4, 3)
        glutInitContextProfile(GLUT_CORE_PROFILE)

        glutCreateWindow("main")

    def initShader(self, shaderCode):
        shaderSub = shaders.compileShader(shaderCode, GL_COMPUTE_SHADER)
        
        self.shader = shaders.compileProgram(shaderSub)

    def run(self, data, outSize, groupCount):
        dataSize = len(data) * self.sizeOfInt
        
        shaders.glUseProgram(self.shader)
        
        ssbo = glGenBuffers(1)
        glBindBuffer(GL_SHADER_STORAGE_BUFFER, ssbo)
        glBufferData(GL_SHADER_STORAGE_BUFFER, dataSize, self.array_type(data), GL_DYNAMIC_DRAW)
        glBindBufferBase(GL_SHADER_STORAGE_BUFFER, 3, ssbo)
        glBindBuffer(GL_SHADER_STORAGE_BUFFER, 0)
        
        glDispatchCompute(groupCount, 1, 1)
        glMemoryBarrier(GL_SHADER_STORAGE_BARRIER_BIT);
        glBindBufferBase(GL_SHADER_STORAGE_BUFFER, 0, 0);
        
        glBindBuffer(GL_SHADER_STORAGE_BUFFER, ssbo);
        
        dataOut = glMapBuffer(GL_SHADER_STORAGE_BUFFER, GL_READ_ONLY)
        
        #print(dataOut)
        g = (ctypes.c_int * outSize).from_address(dataOut)
        out = []
        for i in range(outSize):
            out.append(g[i])
        
        glUnmapBuffer(GL_SHADER_STORAGE_BUFFER)
        
        return out
