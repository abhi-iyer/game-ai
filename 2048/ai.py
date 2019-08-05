from __future__ import print_function
import copy, random
import sys
import numpy as np

MOVES = {0:'up', 1:'left', 2:'down', 3:'right'}
MAX = 1
CHANCE = 0
ARR_SIZE = 16

class State:
  """game state information"""
  def __init__(self, matrix, player, score, pre_move, movement):
    # save parameter variables to local variables
    self.tm = matrix
    self.player = player
    self.score = score
    self.pre_move = pre_move
    self.children = []
    self.movement = movement
    self.minimaxScore = 0

  def highest_tile(self):
    """Return the highest tile here (just a suggestion, you don't have to)"""
    max_tile = 0

    for i in self.tm:
      temp_max = max(i) # find maximum element in each list of the matrix
      if (temp_max > max_tile): # if a new maximum element exceeds the old max
        max_tile = temp_max # update the maximum tile in the matrix
    
    return max_tile # return highest tile value

class Gametree:
  """main class for the AI"""
  def __init__(self, root, depth):
    self.rootState = State(root, MAX, 0, None, None) # root is max player with score of 0
    self.depth = depth # store depth of minimax tree
    self.dict = {0:[self.rootState], 1:[], 2:[], 3:[], 4:[], 5:[], 6:[]} # dictionary to store structure of tree

  def grow_once(self, state):
    """Grow the tree one level deeper"""

    if (state.player == MAX):
      for direction in MOVES: # expand all possibilities for node
        if (state.pre_move == None): # if the state is a root
          sim = Simulator(copy.deepcopy(state.tm), 0) # score entered into simulator is 0
        else:
          sim = Simulator(copy.deepcopy(state.tm), state.score) # if not root, score entered into simulator is state's score

        if sim.checkIfCanGo(): # if not game over
          sim.move(direction) # move simulator in specified direction

          if sim.tileMatrix != state.tm: # if there was a state chagne
            state.children.append(State(sim.tileMatrix, CHANCE, sim.total_points, state, direction)) # keep track of new State child

    elif (state.player == CHANCE):      
      # expand possibilities for node
      for i in range(len(state.tm)):
        for j in range(len(state.tm[i])):
          if (state.tm[i][j] == 0): # if there is an empty spot in the matrix
            sim = Simulator(copy.deepcopy(state.tm), state.score)
            sim.tileMatrix[i][j] = 2 # simulate a 2 in that empty spot
            
            if sim.checkIfCanGo():
              state.children.append(State(sim.tileMatrix, MAX, sim.total_points, state, None)) # keep track of new State child
    
  def grow(self, state):
    """Grow the full tree from root"""

    depthTemp = 0
    while (depthTemp <= self.depth): 
      for child in self.dict[depthTemp]: # for every node in specified depth
        self.grow_once(child) # grow that node once (one level)
        self.dict[depthTemp + 1].extend(child.children) # add the children of that node to next depth (stored in dictionary)
      depthTemp+=1

  def minimax(self, state):
    """Compute minimax values on the three"""
    if not state.children:
      return (state.score + state.highest_tile()) + (ARR_SIZE - np.count_nonzero(state.tm)) # weighted score of terminal node is score of state + state's highest tile + num of zeroes in the matrix
    elif state.player == MAX:
      value = -sys.maxsize
      for child in state.children:
        value = max(value, self.minimax(child)) # store maximum minimax value for any node
      return value
    elif state.player == CHANCE:
      value = 0
      for child in state.children:
        value = value + self.minimax(child)*(1/len(state.children)) # calculate minimax value for chance node
      return value
    else:
      print("Error!")

  def compute_decision(self):
    """Derive a decision"""
    self.grow(self.rootState) # grow tree from root

    tempMax = 0

    for child in self.dict[1]: # look at max nodes at depth 1 in tree
      child.minimaxScore = self.minimax(child) # find minimax value for each max node
      
      # find node with maximum minimax value
      if child.minimaxScore > tempMax:
        tempMax = child.minimaxScore
        tempState = child

    decision = tempState.movement # decision to make is the decision encoded in max node state with highest minimax value
    print(MOVES[decision])

    #Should also print the minimax value at the root
    print("Minimax value: ", tempMax)

    return decision

class Simulator:
  """Simulation of the game"""
  #Hint: You basically need to copy all the code from the game engine itself.
  #Hint: The GUI code from the game engine should be removed. 
  #Hint: Be very careful not to mess with the real game states. 
  def __init__(self, matrix, score):
    self.tileMatrix = matrix
    self.total_points = score
    self.board_size = 4

  def move(self, direction):
    for i in range(0, direction):
      self.rotateMatrixClockwise()
    if self.canMove():
      self.moveTiles()
      self.mergeTiles()
    for j in range(0, (4 - direction) % 4):
      self.rotateMatrixClockwise()
  def moveTiles(self):
    tm = self.tileMatrix
    for i in range(0, self.board_size):
      for j in range(0, self.board_size - 1):
        while tm[i][j] == 0 and sum(tm[i][j:]) > 0:
          for k in range(j, self.board_size - 1):
            tm[i][k] = tm[i][k + 1]
          tm[i][self.board_size - 1] = 0
  def mergeTiles(self):
    tm = self.tileMatrix
    for i in range(0, self.board_size):
      for k in range(0, self.board_size - 1):
        if tm[i][k] == tm[i][k + 1] and tm[i][k] != 0:
          tm[i][k] = tm[i][k] * 2
          tm[i][k + 1] = 0
          self.total_points += tm[i][k]
          self.moveTiles()
  def checkIfCanGo(self):
    tm = self.tileMatrix
    for i in range(0, self.board_size ** 2):
      if tm[int(i / self.board_size)][i % self.board_size] == 0:
        return True
    for i in range(0, self.board_size):
      for j in range(0, self.board_size - 1):
        if tm[i][j] == tm[i][j + 1]:
          return True
        elif tm[j][i] == tm[j + 1][i]:
          return True
    return False
  def canMove(self):
    tm = self.tileMatrix
    for i in range(0, self.board_size):
      for j in range(1, self.board_size):
        if tm[i][j-1] == 0 and tm[i][j] > 0:
          return True
        elif (tm[i][j-1] == tm[i][j]) and tm[i][j-1] != 0:
          return True
    return False
  def rotateMatrixClockwise(self):	
    tm = self.tileMatrix
    for i in range(0, int(self.board_size/2)):
      for k in range(i, self.board_size- i - 1):
        temp1 = tm[i][k]
        temp2 = tm[self.board_size - 1 - k][i]
        temp3 = tm[self.board_size - 1 - i][self.board_size - 1 - k]
        temp4 = tm[k][self.board_size - 1 - i]
        tm[self.board_size - 1 - k][i] = temp1
        tm[self.board_size - 1 - i][self.board_size - 1 - k] = temp2
        tm[k][self.board_size - 1 - i] = temp3
        tm[i][k] = temp4
  def convertToLinearMatrix(self):
    m = []
    for i in range(0, self.board_size ** 2):
      m.append(self.tileMatrix[int(i / self.board_size)][i % self.board_size])
    m.append(self.total_points)
    return m
