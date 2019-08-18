#version 430 core
//TODO: move num in/hidden/out to constants
layout(local_size_x = 50) in;

layout(std430, binding = 3) buffer DataBuf {
  int data[];
};

#define sizeX 20
#define sizeY 20

//https://stackoverflow.com/a/4275343
float rand(vec2 co){
    return fract(sin(dot(co.xy ,vec2(12.9898,78.233))) * 43758.5453);
}

vec2 getFood(int frameCount, int randSeed) {
  vec2 nFood = vec2(sizeX / 2, sizeY / 2);
  //for(int i = 0; i < 10000; i++) {
  int i = 0;
    bool ok = true;
    float rX = rand(vec2(gl_GlobalInvocationID.x + randSeed, frameCount + i)) * 100; //FIXME - real randomness
    float rY = rand(vec2(gl_GlobalInvocationID.x + randSeed, frameCount + i + 1)) * 100; //FIXME - real randomness
    nFood = vec2(int(rX) % sizeX, int(rY) % sizeY);
    //TODO - better placement
    return nFood;
  //}
  //return nFood;
}

void main() {
  int popSize = data[0];
  int netLen = data[1];
  int sLen0 = data[2];
  int sLen1 = data[3];
  int sLen2 = data[4];
  int randSeed = data[5];
  
  int netOff = 6 + int(gl_WorkGroupID.x * netLen);
  int outputOff = 6 + int((popSize * netLen) + gl_WorkGroupID.x);
  
  vec2 size = vec2(sizeX, sizeY);
  
  //snake init
  vec2 snake_data[200];
  snake_data[0] = vec2(3, 10);
  snake_data[1] = vec2(2, 10);
  snake_data[2] = vec2(1, 10);
  int snake_len = 3;
  
  vec2 food = getFood(0, randSeed);
  
  vec2 motion = vec2(1, 0);
  int grow = 0;
  //end snake init
  
  int frameCount = 0;
  int lastDir = 1;
  int foodBonus = 0;
  int shortestDistanceToFood = 25;
  
  int inputs[24];
  
  vec2 probeDirMap[8] = {
    vec2(0, -1),
    vec2(1, -1),
    vec2(1, 0),
    vec2(1, 1),
    vec2(0, 1),
    vec2(-1, 1),
    vec2(-1, 0),
    vec2(-1, -1)
  };
  
  while(frameCount < 10000) {
    //distance to self
    for(int i = 0; i < 8; i++) {
      vec2 move = probeDirMap[i];
      int dist = 0;
      vec2 pos = snake_data[0];
      while(true) {
        pos = pos + move;
        for(int n = 0; n < snake_len; n++) {
          if(snake_data[n] == pos) {
            break;
          }
        }
        dist++;
        if(dist == 25) {
          break;
        }
      }
      inputs[i] = dist * 4;
    }
    
    //distance to walls
    for(int i = 0; i < 8; i++) {
      vec2 move = probeDirMap[i];
      int dist = 0;
      vec2 pos = snake_data[0];
      while(true) {
        pos = pos + move;
        if(pos.x < 0 || pos.x >= size.x || pos.y < 0 || pos.y >= size.y) {
          break;
        }
        dist++;
      }
      inputs[i + 8] = dist * 2;
    }
    
    //distance to food
    for(int i = 0; i < 8; i++) {
      vec2 move = probeDirMap[i];
      int dist = 0;
      vec2 pos = snake_data[0];
      while(true) {
        pos = pos + move;
        if(pos.x < 0 || pos.x >= size.x || pos.y < 0 || pos.y >= size.y) {
          dist = 25;
          break;
        }
        dist++;
        if(pos == food) {
          break;
        }
      }
      if(dist < shortestDistanceToFood) {
        shortestDistanceToFood = dist;
      }
      inputs[i + 16] = dist * 2;
    }
    
    int newDir = lastDir;
    //int outputs[4];
    
    //---NET PROCESSING---
    int numInput = 24;
    int numHidden = 16;
    int numOutput = 4;
    
    float thresholdInput = 0.2;
    float thresholdHidden = 0.15;
    float thresholdOutput = 0.15;
    
    int hiddenLinkCount = 4;
    int outputLinkCount = 4;
    
    ivec4 hiddenTrigMap[] = {
      ivec4(0, 1, 2, 3),
      ivec4(2, 3, 4, 5),
      ivec4(3, 4, 5, 6),
      ivec4(4, 5, 6, 7),
      ivec4(5, 6, 7, 8),
      ivec4(7, 8, 9, 10),
      ivec4(8, 9, 10, 11),
      ivec4(9, 10, 11, 12),
      ivec4(10, 11, 12, 13),
      ivec4(12, 13, 14, 15),
      ivec4(13, 14, 15, 16),
      ivec4(14, 15, 16, 17),
      ivec4(15, 16, 17, 18),
      ivec4(17, 18, 19, 20),
      ivec4(18, 19, 20, 21),
      ivec4(19, 20, 21, 22)
    };
    
    ivec4 outputTrigMap[] = {
      ivec4(0, 4, 8, 12),
      ivec4(1, 5, 9, 13),
      ivec4(2, 6, 10, 14),
      ivec4(3, 7, 11, 15)
    };
    
    bool inputsFired[24];
    for(int i = 0; i < numInput; i++) {
      float amount = (float(100 - inputs[i]) / 100.0) * (float(data[netOff + i]) / 100.0);
      inputsFired[i] = amount >= thresholdInput;
    }
    
    bool hiddenFired[16];
    for(int i = 0; i < numHidden; i++) {
      float amount = 0;
      for(int n = 0; n < hiddenLinkCount; n++) {
        int m = 0;
        
        if(n == 0) {
          m = hiddenTrigMap[i].x;
        } else if(n == 1) {
          m = hiddenTrigMap[i].y;
        } else if(n == 2) {
          m = hiddenTrigMap[i].z;
        } else if(n == 3) {
          m = hiddenTrigMap[i].w;
        }
        
        int inputState = 0;
        if(inputsFired[m]) { inputState = 1; }
        int weight = data[netOff + sLen0 + (i * hiddenLinkCount) + n];
        amount += float(inputState) * (float(weight) / 100.0);
      }
      
      amount = amount / float(hiddenLinkCount);
      hiddenFired[i] = amount >= thresholdHidden;
    }
    
    bool outputFired[4];
    for(int i = 0; i < numOutput; i++) {
      float amount = 0;
      for(int n = 0; n < outputLinkCount; n++) {
        int m = 0;
        
        if(n == 0) {
          m = outputTrigMap[i].x;
        } else if(n == 1) {
          m = outputTrigMap[i].y;
        } else if(n == 2) {
          m = outputTrigMap[i].z;
        } else if(n == 3) {
          m = outputTrigMap[i].w;
        }
        
        int inputState = 0;
        if(hiddenFired[m]) { inputState = 1; }
        int weight = data[netOff + sLen0 + sLen1 + (i * outputLinkCount) + n];
        amount += float(inputState) * (float(weight) / 100.0);
      }
      
      amount = amount / float(outputLinkCount);
      outputFired[i] = amount >= thresholdOutput;
    }
    ///---END NET PROCESSING---
    
    for(int i = 0; i < numOutput; i++) {
      if(outputFired[i]) {
        newDir = i;
      }
    }
    
    if(!(lastDir == 0 && newDir == 2) && !(lastDir == 2 && newDir == 0) && !(lastDir == 1 && newDir == 3) && !(lastDir == 3 && newDir == 1)) {
      lastDir = newDir;
    }
    
    //---GAME PROCESSING---
    if(lastDir == 0) {
      motion = vec2(0, -1);
    } else if(lastDir == 1) {
      motion = vec2(1, 0);
    } else if(lastDir == 2) {
      motion = vec2(0, 1);
    } else if(lastDir == 3) {
      motion = vec2(-1, 0);
    }
    
    vec2 newPos = snake_data[0] + motion;
    if(newPos == food) {
      grow++;
      food = getFood(frameCount, randSeed);
      
      foodBonus += 25;
      shortestDistanceToFood = 25;
    }
    
    for(int i = 180; i >= 0; i--) { //gets stuck here compiling when using i = snake_len - 1
      snake_data[i + 1] = snake_data[i];
    }
    /*for(int i = 0; i < snake_len; i++) { //gets stuck here
      snake_data[(snake_len - i - 1) + 1] = snake_data[(snake_len - i - 1)];
    }*/
    snake_data[0] = newPos;
    if(grow > 0) {
      snake_len++;
      grow--;
    }
    
    if(newPos.x < 0 || newPos.x >= size.x || newPos.y < 0 || newPos.y >= size.y) {
      break;
    }
    
    bool dead = false;
    for(int i = 1; i < snake_len; i++) {
      if(snake_data[i] == newPos) {
        dead = true; //collision with self
        break;
      }
    }
    if(dead) {
      break;
    }
    //---END GAME PROCESSING---
    
    frameCount += 1;
  }
  
  int score = ((25 - shortestDistanceToFood) * 2) + (foodBonus * 3);
  
  atomicAdd(data[outputOff], score);
}
