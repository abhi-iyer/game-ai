from __future__ import print_function
#Use priority queues from Python libraries, don't waste time implementing your own
#Check https://docs.python.org/2/library/heapq.html
from heapq import *

class Agent:
    def __init__(self, grid, start, goal, type):
        self.actions = [(0,-1),(-1,0),(0,1),(1,0)]
        self.grid = grid
        self.came_from = {}
        self.checked = []
        self.start = start
        self.grid.nodes[start[0]][start[0]].start = True
        self.goal = goal
        self.grid.nodes[goal[0]][goal[1]].goal = True
        self.new_plan(type)
    def new_plan(self, type):
        self.finished = False
        self.failed = False
        self.type = type
        if self.type == "dfs" :
            self.frontier = [self.start]
            self.checked = []
        elif self.type == "bfs":
            self.frontier = [self.start]
            self.checked = []
        elif self.type == "ucs":
            self.frontier = []
            self.checked = []
            heappush(self.frontier, (0, self.start))
        elif self.type == "astar":
            self.frontier = []
            self.checked = []
            self.costs = {self.start:0} # dictionary for astar to keep track of costs
            heappush(self.frontier, (0, self.start))
    def show_result(self):
        current = self.goal
        while not current == self.start:
            current = self.came_from[current]
            self.grid.nodes[current[0]][current[1]].in_path = True
    def make_step(self):
        if self.start == self.goal:
            self.finished = True
        
        if self.type == "dfs":
            self.dfs_step()
        elif self.type == "bfs":
            self.bfs_step()
        elif self.type == "ucs":
            self.ucs_step()
        elif self.type == "astar":
            self.astar_step()
    def dfs_step(self):
        # if frontier is empty, there is no path
        if not self.frontier:
            self.failed = True
            print("no path")
            return
        current = self.frontier.pop() # pop first element in stack
        print("popped: ", current)
        # mark node just popped as explored and no longer in frontier
        self.grid.nodes[current[0]][current[1]].checked = True
        self.grid.nodes[current[0]][current[1]].frontier = False
        self.checked.append(current)
        # go through 4 different movements from current node (up, down, left, right)
        for i, j in self.actions:
            # for every i, j, calculate nextstep by adding to current position
            nextstep = (current[0]+i, current[1]+j)
            # check if this nextstep was already explored is in frontier currently
            if nextstep in self.checked or nextstep in self.frontier:
                print("expanded before: ", nextstep) # state that this node has been visited before
                continue
            # make sure nextstep is within ranges of grid
            if 0 <= nextstep[0] < self.grid.row_range:
                if 0 <= nextstep[1] < self.grid.col_range:
                    # if nextstep is not a puddle
                    if not self.grid.nodes[nextstep[0]][nextstep[1]].puddle:
                        if nextstep == self.goal:
                            self.finished = True
                        # add nextstep to frontier
                        self.frontier.append(nextstep)
                        # mark that nextstep is currently in frontier
                        self.grid.nodes[nextstep[0]][nextstep[1]].frontier = True
                        # map nextstep to current in dictionary to show adjacent movement
                        self.came_from[nextstep] = current
                        print("pushed: ", nextstep)
                    else:
                        print("puddle at: ", nextstep)
                else:
                    print("out of column range: ", nextstep)
            else:
                print("out of row range: ", nextstep)

    def bfs_step(self):
        # if frontier is empty, there is no path
        if not self.frontier:
            self.failed = True
            print("no path")
            return

        current = self.frontier.pop(0) # pop first element in queue
        print("popped: ", current)
        # mark node just popped as explored and no longer in frontier
        self.grid.nodes[current[0]][current[1]].checked = True
        self.grid.nodes[current[0]][current[1]].frontier = False
        self.checked.append(current)
        # go through 4 different movements from current node (up, down, left, right)
        for i, j in self.actions:
            # for every i, j, calculate nextstep by adding to current position
            nextstep = (current[0]+i, current[1]+j)
            # check if this nextstep was already explored is in frontier currently
            if nextstep in self.checked or nextstep in self.frontier:
                print("expanded before: ", nextstep)
                continue
            # make sure nextstep is within ranges of grid
            if 0 <= nextstep[0] < self.grid.row_range:
                if 0 <= nextstep[1] < self.grid.col_range:
                    # if nextstep is not a puddle
                    if not self.grid.nodes[nextstep[0]][nextstep[1]].puddle:
                        if nextstep == self.goal:
                            self.finished = True
                        # add nextstep to frontier
                        self.frontier.append(nextstep)
                        # mark that nextstep is currently in frontier
                        self.grid.nodes[nextstep[0]][nextstep[1]].frontier = True
                        # map nextstep to current in dictionary to show adjacent movement
                        self.came_from[nextstep] = current
                        print("pushed: ", nextstep)
                    else:
                        print("puddle at: ", nextstep)
                else:
                    print("out of column range: ", nextstep)
            else:
                print("out of row range: ", nextstep)

    def ucs_step(self):
        # if frontier is empty, there is no path
        if not self.frontier:
          self.failed = True
          print("no path")
          return

        # pop current node and cost from priority queue  
        (cost, current) = heappop(self.frontier)

        # print node and cost as program continues
        print("current node: ", current)
        print("current node cost: ", cost)

        print("popped: ", current)

        # mark current node as no longer in frontier and already visited
        self.grid.nodes[current[0]][current[1]].checked = True
        self.grid.nodes[current[0]][current[1]].frontier = False
        self.checked.append(current)

        # for every action
        for i, j in self.actions:       
          nextstep = (current[0] + i, current[1] + j) # calculate nextstep

          if nextstep in self.checked or nextstep in self.frontier:
            print("expanded before: ", nextstep)
            continue
          
          if 0 <= nextstep[0] < self.grid.row_range:
            if 0 <= nextstep[1] < self.grid.col_range:
              if not self.grid.nodes[nextstep[0]][nextstep[1]].puddle:
                #calculate G value
                g_value = cost + self.grid.nodes[nextstep[0]][nextstep[1]].cost()

                if nextstep == self.goal: # if goal is reached
                  self.finished = True
                  print("final cost: ", g_value) # print out final cost of path

                # push nextstep with g_value cost to heap if not in frontier already
                if not (g_value, nextstep) in self.frontier:
                  heappush(self.frontier, (g_value, nextstep))
                
                  self.grid.nodes[nextstep[0]][nextstep[1]].frontier = True
                  self.came_from[nextstep] = current
                  print("pushed: ", nextstep)
              else:
                print("puddle at: ", nextstep)
            else:
              print("out of column range: ", nextstep)
          else:
            print("out of row range: ", nextstep)

    # heuristic function used in A* algorithm
    def heuristic_cost(self, startPoint, endPoint):
      # find absolute value distance in x and y from current point to goal
      dx = abs(endPoint[0] - startPoint[0]) 
      dy = abs(endPoint[1] - startPoint[1])
      return 10*(dx + dy)

    def astar_step(self):
        if not self.frontier:
          self.failed = True
          print("no path")
          return
        
        # pop current node from priority queue
        current = heappop(self.frontier)[1]
        # get current cost from dictionary mapping node to accumulated cost
        cost = self.costs[current]

        # print node and cost as program continues
        print("current node: ", current)
        print("current node cost: ", cost)

        print("popped: ", current)

        # mark current node as no longer in frontier and already visited
        self.grid.nodes[current[0]][current[1]].checked = True
        self.grid.nodes[current[0]][current[1]].frontier = False
        self.checked.append(current)

        for i, j in self.actions:       
          nextstep = (current[0] + i, current[1] + j) # calculate nextstep

          if nextstep in self.checked or nextstep in self.frontier:
            print("expanded before: ", nextstep)
            continue
          
          if 0 <= nextstep[0] < self.grid.row_range:
            if 0 <= nextstep[1] < self.grid.col_range:
              if not self.grid.nodes[nextstep[0]][nextstep[1]].puddle:
                # calculate G value and store in dictionary, mapped to nextstep
                self.costs[nextstep] = cost + self.grid.nodes[nextstep[0]][nextstep[1]].cost()

                if nextstep == self.goal: # if goal is reached
                  self.finished = True
                  print("final cost: ", self.costs[nextstep]) # print out final cost of path

                # calculate F value and store in f_value (F_value = G_value + H_value)
                f_value = self.costs[nextstep] + self.heuristic_cost(nextstep, self.goal)

                # push nextstep with f_value cost if not already in frontier
                if not (f_value, nextstep) in self.frontier:
                  heappush(self.frontier, (f_value, nextstep))
                
                  self.grid.nodes[nextstep[0]][nextstep[1]].frontier = True
                  self.came_from[nextstep] = current
                  print("pushed: ", nextstep)
              else:
                print("puddle at: ", nextstep)
            else:
              print("out of column range: ", nextstep)
          else:
            print("out of row range: ", nextstep)
