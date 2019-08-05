from math import sqrt, log
import random
import copy

class State:
  def __init__(self, grid, player, move):
    self.grid = grid
    self.maxrc = len(grid)-1
    self.grid_count = 19
    self.grid_size = 26

    # instance variables that every State node should have
    self.options = []
    self.player = player
    self.children = []
    self.reward = 0
    self.parent = None
    self.move = move # tuple of coordinates
    self.game_over = False
    self.winner = None
    self.q = 0 # total number of wins
    self.n = 0 # total number of visits

    # load state with possible options upon initialization
    self.get_options(self.grid)

  def isTerminal(self):
    if (self.move == None): # root state
      return False

    if (self.game_over == True or self.check_win(self.move[0], self.move[1]) == True): # if game board is filled (options exhausted) or if winning move
      return True
    else:
      return False    

  def fullyExpanded(self):
    if (len(self.options) == 0): # if game board is filled (options exhausted)
      return True
    else:
      return False

  # calculate possible actions to take from a state
  def get_options(self, grid):
    opts = []

    for r in range(len(grid)):
      for c in range(len(grid)):
        if grid[r][c] == self.player: # look at all possible pieces of player's color   
          if ((c - 1) >= 0 and grid[r][c - 1] == '.'): # if adjacent left spot is empty
            opts.append((r, c - 1))
          if ((c + 1) <= self.maxrc and grid[r][c + 1] == '.'): # right spot empty
            opts.append((r, c + 1))
          if ((r + 1) <= self.maxrc and grid[r + 1][c] == '.'): # down spot empty
            opts.append((r + 1, c))
          if ((r - 1) >= 0 and grid[r - 1][c] == '.'): # up spot empty
            opts.append((r - 1, c))

    self.options = opts

    if len(self.options) == 0:
      # In the unlikely event that no one wins before board is filled
      self.winner = '0'
      self.game_over = True

  def check_win(self, r, c):
    n_count = self.get_continuous_count(r, c, -1, 0)
    s_count = self.get_continuous_count(r, c, 1, 0)
    e_count = self.get_continuous_count(r, c, 0, 1)
    w_count = self.get_continuous_count(r, c, 0, -1)
    se_count = self.get_continuous_count(r, c, 1, 1)
    nw_count = self.get_continuous_count(r, c, -1, -1)
    ne_count = self.get_continuous_count(r, c, -1, 1)
    sw_count = self.get_continuous_count(r, c, 1, -1)
    if (n_count + s_count + 1 >= 5) or (e_count + w_count + 1 >= 5) or \
        (se_count + nw_count + 1 >= 5) or (ne_count + sw_count + 1 >= 5): # if a move caused a win
      self.winner = self.grid[r][c]
      return True
    else:
      return False

  # see if a contiguous line of 5 pieces is on the board
  def get_continuous_count(self, r, c, dr, dc):
    piece = self.grid[r][c]
    result = 0
    i = 1
    while True:
      new_r = r + dr * i
      new_c = c + dc * i
      if 0 <= new_r < self.grid_count and 0 <= new_c < self.grid_count:
        if self.grid[new_r][new_c] == piece:
          result += 1
        else:
          break
      else:
        break
      i += 1
    return result

class MCTS:
  def __init__(self, grid, player):
    self.grid = grid
    self.player = player
    self.winner = None

  def other_player(self, state): # switch to other player for every move
    if state.player == 'b':
      return 'w'
    if state.player == 'w':
      return 'b'

  def uct_search(self):
    count = 200 # iteration count of monte carlo tree search
    i = 0

    rootState = State(copy.deepcopy(self.grid), self.player, None)

    while i < count:
      state = self.tree_policy(rootState) # state from selection and expansion (tree policy)
      reward = self.default_policy(state) # reward from simulation (default policy)
      self.backup(state, reward) # back propagation from terminal node to root
      i+=1

    return self.best_child(rootState).move # return best move from root state

  def tree_policy(self, state):
    while not state.isTerminal(): 
      if not state.fullyExpanded():
        return self.expand(state) # expand state as long as it is not terminal/fully expanded
      else:
        state = self.best_child(state) # if state is fully expanded, select best child
    return state

  def expand(self, state):
    action = self.take_action(state) 

    newGrid = copy.deepcopy(state.grid)
    newGrid[action[0]][action[1]] = state.player

    newState = State(newGrid, self.other_player(state), action)

    newState.parent = state # state is parent of newState
    state.children.append(newState) # newState is child of parent state

    return newState

  def best_child(self, state):
    maxValue = 0
    bestChild = 0
    tempState = None

    for child in state.children: # for all children of given state
      bestChild = (child.q)/(child.n) + 2 * sqrt((2 * log(state.n))/(child.n)) # calculate best child value for each state

      if (bestChild > maxValue): # find state with max best child value
        maxValue = bestChild
        tempState = child
    
    return tempState

  def default_policy(self, state):
    tempState = State(copy.deepcopy(state.grid), state.player, state.move) # start simulation with tempState

    while not tempState.isTerminal(): # rollout simulation from tempState until node is terminal
       action = self.take_action(tempState) 

       newGrid = copy.deepcopy(tempState.grid)
       newGrid[action[0]][action[1]] = tempState.player

       tempState = State(newGrid, self.other_player(state), action)
    
    # return reward of state at end
    if (tempState.winner == self.player):
      return 1
    else:
      return 0

  def take_action(self, state):
    # randomly picked action from options list
    m = random.randint(0, len(state.options)-1)
    moveToTake = state.options[m] 

    del state.options[m] # delete action from options list
    return moveToTake

  # returns move that is used in board.py
  def make_move(self):
    check = True

    # check if entire board is empty
    for i in range(len(self.grid)):
      for j in range(len(self.grid[i])):
        if (self.grid[i][j] != '.'):
          check = False
          break
    
    if (check == True): # if board is empty, place first move at center
      return (9, 9) 
    else:
      return self.uct_search() # if board not empty, run uctsearch algorithm

  def backup(self, state, reward):    
    while state != None:
      # update values
      state.n += 1 
      state.q += reward
      
      state = state.parent # backpropagate up to root