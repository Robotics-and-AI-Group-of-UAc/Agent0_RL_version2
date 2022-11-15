import ast
import random
from middleware_impl.zmq_socket import ZMQSocket
from middleware_impl import REQ
from MC_FirstVisit import DISCOUNT, EXPLORATIONS

class Agent:
    def __init__(self, host, port):
        self.sock = ZMQSocket(host,port,REQ)
        self.goal = self.get_goal()
        self.max_coord = self.get_max_coord()
        # Get targets
        self.targets_list = self.get_list_targets(self.get_targets(), self.max_coord)
        # Test
        print("Targets list:",self.targets_list)
        # Get rewards
        self.rewards = self.get_reward_dict(self.get_reward(), self.max_coord)
        # Test
        # print("Rewards:",rewards)
        # Get obstacles
        self.obstacles = self.get_obstacles_dict(self.get_obstacles(), self.max_coord)
        # Test
        # print("Obstacles:")
        # print(self.obstacles)

        # Initialize qtable
        # qTable = self.initialize_qtable(self.max_coord)
        # print("Starting qtable:",qtable)

        # Initialize vtable
        self.vtable = self.initialize_vtable(self.max_coord, self.obstacles)
        # Test
        print("vtable values:")
        self.print_vtable_values(self.vtable,self.max_coord)
        print("vtable visits:")
        self.print_vtable_nr_visits(self.vtable,self.max_coord)
        print("vtable possible paths (north,east,south,east):")
        self.print_vtable_paths(self.vtable,self.max_coord)



    def print_message(self,data):
        print("Data:",data)

    def get_max_coord(self):
        value = self.sock.execute("info", "maxcoord")
        max_coord=ast.literal_eval(value)
        # test
        print('Received maxcoord', max_coord)
        return max_coord

    def get_pos(self):
        '''Return the actual position of the agent. '''
        pos = self.sock.execute("info", "position",0.01)
        # test
        # print('Received agent\'s position:', pos)

        return ast.literal_eval(pos)

    def get_goal(self):
        goal = self.sock.execute("info", "goal")
        # test
        # print('Received agent\'s goal:', goal)
        return ast.literal_eval(goal)



    def get_targets(self):
        ''' Return the targets defined in the world.'''
        msg = self.sock.execute("info", "targets")
        # test
        #print('Received targets:', msg)
        return ast.literal_eval(msg)

    def get_targets_dict(self, targets, max_coord):
        '''Return a dictionary of targets'''
        targets_dict = {}
        for y in range(max_coord[1]):
            for x in range(max_coord[0]):
                targets_dict[str((x, y))] = targets[x][y]
        return targets_dict

    def get_list_targets(self, targets, max_coord:list):
        targets_list =[]
        for y in range(max_coord[1]):
            for x in range(max_coord[0]):
                if targets[x][y] == 1:
                    targets_list.append((x, y))
        # test
        # print("Targets List:",targets_list)
        return targets_list

    def set_home(self):
        home = self.sock.execute("command","home",0.01)


    def get_obstacles(self):
        obst = self.sock.execute("info","obstacles")
        # test
        # print('Received map of obstacles:', obst)
        return ast.literal_eval(obst)


    def get_obstacles_list(self, obstacles, max_coord):
        '''Return a list of obstacles'''
        obst_list = []
        for y in range(max_coord[1]):
            for x in range(max_coord[0]):
                if obstacles[x][y] == 1:
                    obst_list.append((x,y))
        return obst_list


    def get_obstacles_dict(self, obstacles, max_coord):
        '''Return a dictionary of obstacles:'''
        obst_dict = {}
        for y in range(max_coord[1]):
            for x in range(max_coord[0]):
                obst_dict[str((x, y))] = obstacles[x][y]
        return obst_dict

    def get_reward(self):
        '''Return the matrix of rewards'''
        rew = self.sock.execute("info", "rewards")
        # test
        # print('Received rewards:', rew)
        return ast.literal_eval(rew)

    def get_reward_dict(self, rewards, max_coord):
        '''Return a dictionary of rewards:'''
        rewards_dict = {}
        for y in range(max_coord[1]):
            for x in range(max_coord[0]):
                rewards_dict[str((x,y))]=rewards[x][y]
        return rewards_dict

    # ---------------------------------------------------
    # Get the coordinates on north, east, south or east
    # ---------------------------------------------------
    def coord_north(self,pos:list, max_coord:list):
        ''' Assuming world is circular, the value of coordinates to north'''
        x,y = pos[0],pos[1]
        if y == 0:  # top
            y1 = max_coord[1] - 1
        else:
            y1 = y - 1
        return (x,y1)

    def coord_south(self,pos:list, max_coord:list):
        ''' Assuming world is circular, the value of coordinates to south'''
        x,y = pos[0],pos[1]
        if y == max_coord[1] - 1:  # bottom
            y2 = 0
        else:
            y2 = y + 1
        return (x,y2)

    def coord_east(self,pos:list, max_coord:list):
        ''' Assuming world is circular, the value of coordinates to east'''
        x,y = pos[0],pos[1]
        if x == max_coord[0] - 1:  # right
            x1 = 0
        else:
            x1 = x + 1
        return (x1,y)

    def coord_west(self,pos:list, max_coord:list):
        ''' Assuming world is circular, the value of coordinates to west'''
        x,y = pos[0],pos[1]
        if x == 0:
            x2 = max_coord[0] - 1
        else:
            x2 = x - 1
        return (x2,y)


    def initialize_vtable(self, max_coord, obstacles):
        v_table = {}
        for y in range(max_coord[1]):
            for x in range(max_coord[0]):
                # Obstacles
                north = 0
                east  = 0
                south = 0
                west  = 0
                # If it is an obstacle it has all directions equal to zero!
                if obstacles[str((x,y))] == 1:
                    v_table[str((x, y))] = [0, 0, (north, east, south, west)]
                else:
                    #North
                    if obstacles[str(self.coord_north((x,y),max_coord))] == 0: #not an obstacle
                        north = 1
                    #South
                    if obstacles[str(self.coord_south((x,y),max_coord))] == 0: #not an obstacle
                        south = 1
                    #East
                    if obstacles[str(self.coord_east((x,y),max_coord))] == 0: #not an obstacle
                        east = 1
                    #West
                    if obstacles[str(self.coord_west((x,y),max_coord))] == 0: #not an obstacle
                        west = 1
                    v_table[str((x,y))]=[0,0,(north,east,south,west)]
        return v_table


    def initialize_qtable(self, max_coord):
        q_table ={}
        for y in range(max_coord[1]):
            for x in range(max_coord[0]):
                q_table[str((x,y))]=[0,0,0,0]
        # Test
        # print("QTable initialized: ", q_table)
        return q_table



    def clear_all_server_arrows(self, qtable, max_coord:list):
        ''' Clear all the arrows in the server'''
        for i in range(max_coord[1]):
            for j in range(max_coord[0]):
                msg = self.sock.execute("uarrow",str(i)+","+str(j),0.05)

    def take_first_elem(self,elem):
        return elem[0]

    def add_server_vtable_arrows(self, vTable, targets, max_coord):
        '''Add arrows for vTable'''
        for i in range(max_coord[0]):
            for j in range(max_coord[1]):
                pos = (i, j)
                values = vTable[str(pos)]
                # There are paths to print
                if sum(values[2]) != 0 and pos != self.get_goal() and pos not in targets:
                    values_around = ( vTable[ str(self.coord_north(pos,max_coord))][0] , vTable[str(self.coord_east(pos,max_coord))][0], vTable[str(self.coord_south(pos,max_coord))][0], vTable[str(self.coord_west(pos,max_coord))][0])

                    # coord_list = list( map(operator.mul, values[2],values_around) )

                    # Test
                    # print("Pos:",pos," has tuple:",coord_list)
                    directions = ["north","east","south","west"]
                    values_dir =[]
                    for k in range(4):
                        if values[2][k] != 0: # Possible direction
                            values_dir.append((values_around[k],directions[k]))
                    values_dir.sort(key=self.take_first_elem)
                    values_dir = values_dir[::-1]
                    arrow_dirs =[]
                    # Test
                    # print("Pos:",pos," has ordered list:",values_dir)
                    if len(values_dir) == 1:
                        arrow_dirs.append(values_dir[0][1]) #Get the direction of unique value
                    if len(values_dir) == 2:
                        if values_dir[0][0] > values_dir[1][0]:
                            arrow_dirs.append(values_dir[0][1])
                        else:
                            arrow_dirs.append(values_dir[0][1])
                            arrow_dirs.append(values_dir[1][1])
                    if len(values_dir) == 3:
                        if values_dir[0][0] > values_dir[1][0]:
                            arrow_dirs.append(values_dir[0][1])
                        elif values_dir[0][0] == values_dir[1][0] and values_dir[0][0] > values_dir[2][0]:
                            arrow_dirs.append(values_dir[0][1])
                            arrow_dirs.append(values_dir[1][1])
                        else: # values_dir[0][0] == values_dir[1][0] == values_dir[2][0]:
                            arrow_dirs.append(values_dir[0][1])
                            arrow_dirs.append(values_dir[1][1])
                            arrow_dirs.append(values_dir[2][1])
                    if len(values_dir) == 4:
                        if values_dir[0][0] > values_dir[1][0]:
                            arrow_dirs.append(values_dir[0][1])
                        elif values_dir[0][0] == values_dir[1][0] and values_dir[0][0] > values_dir[2][0]:
                            arrow_dirs.append(values_dir[0][1])
                            arrow_dirs.append(values_dir[1][1])
                        elif values_dir[0][0] == values_dir[1][0] == values_dir[2][0] and values_dir[0][0] > values_dir[3][0]:
                            arrow_dirs.append(values_dir[0][1])
                            arrow_dirs.append(values_dir[1][1])
                            arrow_dirs.append(values_dir[2][1])
                        else:
                            arrow_dirs.append(values_dir[0][1])
                            arrow_dirs.append(values_dir[1][1])
                            arrow_dirs.append(values_dir[2][1])
                            arrow_dirs.append(values_dir[3][1])

                    arrow = ""
                    nr = 0
                    if "north" in arrow_dirs:
                        arrow="north"
                        nr = nr + 1
                    if "east" in arrow_dirs:
                        if nr > 0:
                            arrow = arrow + "_east"
                        else:
                            arrow = "east"
                        nr = nr + 1
                    if "south" in arrow_dirs:
                        if nr > 0:
                            arrow = arrow + "_south"
                        else:
                            arrow = "south"
                        nr = nr + 1
                    if "west" in arrow_dirs:
                        if nr > 0:
                            arrow = arrow + "_west"
                        else:
                            arrow = "west"
                    msg = self.sock.execute("marrow", arrow +","+str(j)+","+str(i), 0.05)

    def add_server_qtable_arrows(self, qTable, max_coord:list):
        '''Add arrows for qTable'''
        arrow =""
        for i in range(max_coord[1]):
            for j in range(max_coord[0]):
                coordinates = (j,i)
                coord_list = [qTable.get(str(coordinates))[0], qTable.get(str(coordinates))[1],
                              qTable.get(str(coordinates))[2], qTable.get(str(coordinates))[3]].sort()
                ##res = max(coord_list)
                #test
                print("(",j,",",i,")=",coord_list)
                #All identical
                if coord_list[0] == coord_list[1] == coord_list[2] == coord_list[3]:
                    print("all directions")
                    arrow ="north_south_east_west"
                    #msg = self.execute_msg("marrow", "north_south_east_west" + "," + str(i) + "," + str(j), 0.05)
                # Three equal
                elif coord_list[0] == coord_list[1] == coord_list[2]:
                    arrow ="north_south_east"
                elif coord_list[0] == coord_list[2] == coord_list[3]:
                    arrow ="north_south_west"
                elif coord_list[1] == coord_list[2] == coord_list[3]:
                    arrow ="south_east_west"
                elif coord_list[0] == coord_list[1] == coord_list[3]:
                    arrow ="north_east_west"
                # Two equal
                elif coord_list[0] == coord_list[1]:
                    arrow = "north_east"
                elif coord_list[0] == coord_list[2]:
                    arrow = "north_south"
                elif coord_list[0] == coord_list[3]:
                    arrow = "north_west"
                elif coord_list[1] == coord_list[2]:
                    arrow = "south_east"
                elif coord_list[1] == coord_list[3]:
                    arrow = "east_west"
                elif coord_list[2] == coord_list[3]:
                    arrow = "south_west"
                # One bigest
                else:
                    res = max(coord_list)
                    if res > 0: #not all are zero
                        idx = coord_list.index(res)
                        if  idx == 0:
                            #north
                            arrow = "north"
                        #pos = ast.literal_eval(msg)
                        elif idx == 1:
                            # east
                            arrow = "east"
                        elif idx == 2:
                            # south
                            arrow = "south"
                        else:
                            # west
                            arrow = "west"
                msg = self.sock.execute("marrow", arrow+","+str(i)+","+str(j), 0.05)

    def print_vtable_values(self, vTable, max_coord:list):
        '''For each state, return the function value...'''
        for i in range(max_coord[1]):
            str_row = "|"
            for j in range(max_coord[0]):
                coordinates = (j,i)
                str_row = str_row + '(%3.1f)'%(vTable.get(str(coordinates))[0]) + "|"
            print(str_row)

    def print_vtable_nr_visits(self, vTable, max_coord:list):
        '''For each state, return the number of visits...'''
        for i in range(max_coord[1]):
            str_row = "|"
            for j in range(max_coord[0]):
                coordinates = (j,i)
                str_row = str_row + '(%3.1f)'%(vTable.get(str(coordinates))[1]) + "|"
            print(str_row)

    def print_vtable_paths(self, vTable, max_coord:list):
        '''For each state, return possibe paths...'''
        for i in range(max_coord[1]):
            str_row = "|"
            for j in range(max_coord[0]):
                coordinates = (j,i)
                str_row = str_row + str(vTable.get(str(coordinates))[2]) + "|"
            print(str_row)

    def print_qtable(self, qTable, max_coord:list):
        for i in range(max_coord[1]):
            row_str_n =  "|"
            row_str_w =  "|"
            row_str_s =  "|"
            for j in range(max_coord[0]):
                coordinates = (j,i)
                f_str_n = '(%3.1f)'%(qTable.get(str(coordinates))[0])
                f_str_s = '(%3.1f)'%(qTable.get(str(coordinates))[2])
                f_str_w = '(%3.1f)'%(qTable.get(str(coordinates))[3])
                f_str_e = '(%3.1f)'%(qTable.get(str(coordinates))[1])
                row_str_n = row_str_n + "    " + f_str_n + "    |"
                row_str_s = row_str_s + "    " + f_str_s + "    |"
                row_str_w = row_str_w + f_str_w + "    " + f_str_e + "|"
            print(row_str_n)
            print(row_str_w)
            print(row_str_s)
            print()


    def run(self):
        for i in range(EXPLORATIONS):
            # Move home or move to a aleatory position without obstacles
            #  -- get list of positions not obstacles ...
            #  -- select randomly one of them as first position...
            msg = self.sock.execute("command", "home", 0.02)
            # Get the initial position
            self.set_home()
            self.initial_pos = self.get_pos()

        # Find goal or find target
            # find_target = False
            find_goal = False
            find_target = False
            # List of lists [p,d], p = position in coordinates and d = direction of previous movement
            path = []  # Keep the path to the goal

            path.append([self.initial_pos, ""])
            while find_goal == False and find_target == False:
                # while find_goal == False:
                # Test if it found a goal!
                # Options:
                # -- selecting next movement randomly: north, south, east , west
                # -- following the policy
                # Random
                direction = random.randint(1, 4)
                if direction == 1:
                    value = "north"
                elif direction == 2:
                    value = "south"
                elif direction == 3:
                    value = "east"
                else:
                    value = "west"
                # Selecting Policy
                # ...
                action = "command"
                # Test
                # print("Action Value pair:", action, ":", value)
                msg = self.sock.execute(action, value, 0.02)
                pos = self.get_pos()
                path.append([pos, value])  # New position

                #input()
                # Test
                # agent.print_message(msg)

                # Final Position
                # if pos == goal or pos in one of the targets!!
                if pos == self.goal:
                    find_goal = True
                if pos in self.targets_list:
                    find_target = True
            # End ...
            print("Found the goal!\n")
            print("Path:", path)
            path_reversed = path[::-1]
            # Final position
            pos = path_reversed[0][0]
            # Remove final position
            del path_reversed[0]  # Remove the last element
            incremental_return = self.rewards[str(pos)]
            self.vtable[str(pos)][0] = incremental_return
            last_pos = pos  # Position is now the last position
            print("Return of the final position,", last_pos, ":", incremental_return)

            for step in path_reversed:
                pos = step[0]  # actual position
                reward = self.rewards[str((pos))]
                movement = step[1]  # movement type
                # Incremental Return R with discount
                incremental_return = reward + DISCOUNT * incremental_return
                # Get the actual VTable values
                actual_vtable = self.vtable[str(pos)]
                # Test
                print("Actual vTable value:", actual_vtable[0])
                print("Counting visits in actual vTable:", actual_vtable[1])
                # Get the new value
                new_vtable_count = actual_vtable[1] + 1
                new_vtable_value = actual_vtable[0] + (incremental_return - actual_vtable[0]) / new_vtable_count
                self.vtable[str(pos)] = [new_vtable_value, new_vtable_count, actual_vtable[2]]
                # Test
                print("For position x=", pos[0], " y=", pos[1], ":")
                print("VTable value:", self.vtable[str(pos)][0])
                print("VTable count:", self.vtable[str(pos)][1])
                print("VTable directions:", self.vtable[str(pos)][2])
                print("Incremental return:", incremental_return)
                print("--------------------------------------------------")
                last_pos = pos
                # input()
                # Test
                print("VTable values:")
                self.print_vtable_values(self.vtable,self.max_coord)
                print("VTable visits:")
                self.print_vtable_nr_visits(self.vtable,self.max_coord)
                print("VTable possible paths (north,east,south,east):")
                self.print_vtable_paths(self.vtable,self.max_coord)
                print("-------------------------------------------------")

            # Test: stops
#            if i == 2:
#                input()
            if i == 250:
                input()

                # Select the direction of agent's movement

                # if pos[0] ==  last_pos[0]: # No movement on x
                #    if pos[1] > last_pos[1] and pos[1] - last_pos[1] == 1:
                #        movement = "north"
                #    elif pos[1] < last_pos[1] and pos[1] - last_pos[1] == -1:
                #        movement = "south"
                #    elif pos[1] == 0 and last_pos[1] == max_coord[1] -1:
                #        movement = "north"
                #    elif  pos[1]== max_coord[1] - 1 and last_pos[1] == 0:
                #        movement = "south"
                # elif pos[1] == last_pos[1]: #There is no movement on YY
                #    if pos[0] > last_pos[0] and pos[0] - last_pos[0] == 1:
                #        movement ="west"
                #    elif pos[0] < last_pos[0] and pos[0] - last_pos[0] == -1:
                #        movement ="east"
                #    elif pos[0]== 0 and last_pos[0] == max_coord[0] - 1:
                #        movement ="west"
                #    elif pos[0]==max_coord[0] - 1 and last_pos[0] == 0:
                #        movement ="east"
                ##else:
                #    # Error: none
                #    movement =""

                # Get the r

                # if movement == "north":
                #    last_value = qTable[str(pos)]
                #    r = rewards[str(last_pos)]
                #    new_r = r + weight*last_reward
                #    last_reward = new_r # Reward to send to next action

                # if last_value[0] < new_r:
                #   qTable[str(pos)]= [(new_r + last_value[0]) / 2,last_value[1],last_value[2],last_value[3]]
                # elif movement == "east":
                #    last_value = qTable[str(pos)]
                #    r = rewards[str(last_pos)]
                #    new_r = r + weight*last_reward
                #    last_reward = new_r # Reward to send to next action
                # if last_value[1] < new_r:
                #    qTable[str(pos)]= [last_value[0],(new_r + last_value[1]) / 2,last_value[2],last_value[3]]

                # elif movement == "south":
                #    last_value = qTable[str(pos)]
                #    r = rewards[str(last_pos)]
                #    new_r = r + weight*last_reward
                #    last_reward = new_r # Reward to send to next action
                # if last_value[2] < new_r:
                #    qTable[str(pos)]= [last_value[0],last_value[1],(new_r + last_value[2]) / 2,last_value[3]]
                # else:
                #    last_value = qTable[str(pos)]
                #    r = rewards[str(last_pos)]
                #    new_r = r + weight * last_reward
                #    last_reward = new_r  # Reward to send to next action
                # if last_value[3] < new_r:
                #    qTable[str(pos)]= [last_value[0],last_value[1],last_value[2],(new_r + last_value[3]) / 2]
                # Update weight
                # weight = weight_constant * weight
            # Test
            # print("The movement from ",pos," to ",last_pos," had the direction ", movement )
            # print("New weight:",weight)
            # print("last_reward (feeding next steps:",last_reward)
            # Update movement
            # Test
            # print("The new values for qTable are:")
            # agent.printQTable(qTable)

            # Add Arrows to server (qTable)
            # agent.addServerArrows(qTable)
            #self.add_server_vtable_arrows(self.vtable, self.targets_list,self.max_coord)
            #input()
        self.add_server_vtable_arrows(self.vtable, self.targets_list,self.max_coord)



