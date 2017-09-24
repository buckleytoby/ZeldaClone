







class pathfinding:
  def __init__(self,mapclass,mobclass,ptype): #hopefully neighbors/cost is just a pointer, otherwise will cost a lot of memory for many units
    self.neighbors=mapclass.mobstatnbors[(mobclass.width,mobclass.height)]
    self.cost=mapclass.mobcosts[(mobclass.width,mobclass.height)]
    self.max_check=mobclass.max_check
    self.proximity=3 #max(mobclass.width,mobclass.height)
    self.ptype=ptype #type of path to use
    self.moves=[]
    self.goal=None
    self.start=None
    self.cost_so_far={}
    
    self.tempindex=0
  
  def update(self,start,goal=None):
    if goal==None:
      goal=self.goal
    if start==goal:
      print('start==goal')
      return (0,0)
    if goal!=self.goal:
      if self.tempindex==0:
        del self.moves[:]
        self.cost_so_far.clear()
        self.start=start
        self.goal=goal
        if len(self.moves)==0: #or self.goal!=self.moves[0]: #begin or continue analysis
          if self.ptype=='Astar':
            self.Astar()
          elif self.ptype=='greedy':
            #self.greedy()
            pass
      self.tempindex += 1
      if self.tempindex == 10: #every 10 updates, actually recalc path
        self.tempindex=0
        
    if len(self.moves)>0:
      move=self.moves[-1]
      if start==move:
       del self.moves[-1]
       if len(self.moves)>0:
         move=self.moves[-1]
       else:
         move=(start)
    else:
      move=(start)
    #print(move,'move')
    #else:
    #  print('here')
    #  move=self.moves[-1]
    #  if start==move:
    #    del self.moves[-1]
    #    if len(self.moves)>0:
    #      move=self.moves[-1]
    #    else:
    #      move=(start)
    return (move[0]-start[0],move[1]-start[1])
  
  #def Astar(self):
  #  start=self.start
  #  goal=self.goal
  #  if len(self.moves)==0:
        
  def Astar(self):
    start=self.start
    goal=self.goal
    
    frontier = queue.PriorityQueue()
    frontier.put((0, start))
    came_from = {}
    cost_so_far = {}
    came_from[start] = None
    cost_so_far[start] = 0
    for i in range(self.max_check): #stops fxn from running forever
      current = frontier.get()[1]
      if current == goal:
          break
      for next in self.neighbors[current[0]][current[1]]:
        new_cost = cost_so_far[current] + self.cost[next[0]][next[1]]
        if next not in cost_so_far or new_cost < cost_so_far[next]:
          cost_so_far[next] = new_cost
          priority = new_cost + heuristic(goal, next)
          frontier.put((priority, next))
          came_from[next] = current 
    #current = goal
    #self.moves = [current]
    
    while current != start:
        current = came_from[current]
        self.moves.append(current)
    #if len(self.moves)>self.proximity:
    #  del self.moves[:self.proximity]
    #print(self.moves,'self.moves')