import ast
import random
from QLearning import EXPLORATIONS, VISUALIZATION, DISCOUNT, ALPHA
from middleware_impl.zmq_socket import ZMQSocket
from middleware_impl import REQ

class Agent:
    def __init__(self,host,port):
        self.sock = ZMQSocket(host,port,REQ)
        self.goal = self.get_goal()
        self.max_coord = self.get_max_coord()
        # Get targets
        self.targets_list = self.get_list_targets(self.get_targets(), self.max_coord)
        # Test
        print("List of targets:", self.targets_list)
        # Get rewards
        self.rewards = self.get_reward_dict(self.get_reward(), self.max_coord)
        # Get obstacles
        self.obstacles = self.get_obstacles_dict(self.get_obstacles(), self.max_coord)
        # Get obstacles list
        self.obstacles_list = self.get_obstacles_list(self.get_obstacles(), self.max_coord)
        # Test
        # print(self.obstacles_list)
        # Initialize QTable
        self.qtable = self.initialize_qtable(self.max_coord)
        # Test
        print("Starting QTable:", self.qtable)




    def print_message(self,data):
        print("Data:",data)

    def get_max_coord(self):
        coord = self.sock.execute("info", "maxcoord")
        max_coord = ast.literal_eval(coord)
        # test
        # print('Received maxcoord', max_coord)
        return max_coord

    def get_reward(self):
        '''Return the matrix of rewards'''
        rew = self.sock.execute("info", "rewards")
        # test
        print('Received rewards:', rew)
        return ast.literal_eval(rew)

    def get_reward_dict(self, rewards, max_coord):
        # Return a dictionary of rewards:
        rewards_dict = {}
        # Test
        # print("Max Coordinates x_max=",max_coord[0]," y_max=",max_coord[1])
        for y in range(max_coord[1]):
            for x in range(max_coord[0]):
                rewards_dict[str((x, y))]=rewards[x][y]
        # Test
        # print("Rewards converted: ", rewards_dict)
        return rewards_dict

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



    def initialize_qtable(self, max_coord):
        q_table ={}
        for y in range(max_coord[1]):
            for x in range(max_coord[0]):
                q_table[str((x,y))]=[0,0,0,0]
        # Test
        # print("QTable initialized: ", q_table)
        return q_table

    def set_home(self):
        home = self.sock.execute("command","home",0.01)


    def get_pos(self):
        '''Return the actual position of the agent. '''
        position = self.sock.execute("info", "position", 0.01)
        pos = ast.literal_eval(position)
        # Test
        # print('Received agent\'s position:', pos)
        return pos

    def get_goal(self):
        goal_pos = self.sock.execute("info", "goal")
        goal = ast.literal_eval(goal_pos)
        # Test
        # print('Received agent\'s goal:', goal)
        return goal

    def get_targets(self):
        ''' Return the targets defined in the world.'''
        target_pos = self.sock.execute("info", "targets")
        target = ast.literal_eval(target_pos)
        # Test
        # print('Received targets:', res)
        return target

    def get_list_targets(self, targets, max_coord):
        targets_list =[]
        for y in range(max_coord[1]):
            for x in range(max_coord[0]):
                if targets[x][y] == 1:
                    targets_list.append((x, y))
        # Test
        # print("Targets List:",targets_list)
        return targets_list

    def number_format(self, number):
        if number < 10.0:
           format = '(  %3.1f)'%(number)
        elif number < 100.0:
           format = '( %3.1f)'%(number)
        else:
            format = '(%3.1f)'%(number)
        return format

    def print_qtable(self, qtable, max_coord):
        for i in range(max_coord[1]):
            row_str_n =  "|"
            row_str_w =  "|"
            row_str_s =  "|"
            for j in range(max_coord[0]):
                coordinates = (j,i)
                f_str_n = self.number_format(qtable.get(str(coordinates))[0])
                f_str_s = self.number_format(qtable.get(str(coordinates))[2])
                f_str_w = self.number_format(qtable.get(str(coordinates))[3])
                f_str_e = self.number_format(qtable.get(str(coordinates))[1])
                if coordinates not in self.obstacles_list:
                    row_str_n = row_str_n + "     " + f_str_n + "      |"
                    row_str_s = row_str_s + "     " + f_str_s + "      |"
                    row_str_w = row_str_w + f_str_w + "    " + f_str_e + "|"
                else:
                    row_str_n = row_str_n + "     " + "(   . )" + "      |"
                    row_str_s = row_str_s + "     " + "(   . )" + "      |"
                    row_str_w = row_str_w + "(   . )" + "    " + "(   . )" + "|"
            print(row_str_n)
            print(row_str_w)
            print(row_str_s)
            print()

    def clear_all_server_arrows(self, qtable, max_coord:list):
        ''' Clear all the arrows in the server'''
        for i in range(max_coord[1]):
            for j in range(max_coord[0]):
                msg = self.sock.execute("uarrow",str(i)+","+str(j),0.05)

    def add_server_qtable_arrows(self, qtable, max_coord):
        '''Add arrows for qTable'''
        self.print_qtable(qtable, max_coord)
        arrow =""
        for i in range(max_coord[1]):
            for j in range(max_coord[0]):
                coordinates = (j,i)
                coord_list = [qtable.get(str(coordinates))[0], qtable.get(str(coordinates))[1],
                              qtable.get(str(coordinates))[2], qtable.get(str(coordinates))[3]]
                if coordinates not in self.obstacles_list:
                    if coord_list != None:
                        if coord_list[0] == coord_list[1] == coord_list[2] == coord_list[3]:
                            # Test
                            # print("all directions")
                            arrow ="north_east_south_west"
                            #msg = self.execute_msg("marrow", "north_south_east_west" + "," + str(i) + "," + str(j), 0.05)
                        # Three equal
                        elif coord_list[0] == coord_list[1] == coord_list[2]:
                            arrow ="north_east_south"
                        elif coord_list[0] == coord_list[2] == coord_list[3]:
                            arrow ="north_south_west"
                        elif coord_list[1] == coord_list[2] == coord_list[3]:
                            arrow ="east_south_west"
                        elif coord_list[0] == coord_list[1] == coord_list[3]:
                            arrow ="north_east_west"
                        #Two equal
                        elif coord_list[0] == coord_list[1]:
                            arrow = "north_east"
                        elif coord_list[0] == coord_list[2]:
                            arrow = "north_south"
                        elif coord_list[0] == coord_list[3]:
                            arrow = "north_west"
                        elif coord_list[1] == coord_list[2]:
                            arrow = "east_south"
                        elif coord_list[1] == coord_list[3]:
                            arrow = "east_west"
                        elif coord_list[2] == coord_list[3]:
                            arrow = "south_west"
                        #One bigest
                        else:
                            res = max(coord_list)
                            if res > 0: #not all are zero
                                idx = coord_list.index(res)
                                if  idx == 0:
                                    # north
                                    arrow = "north"
                                # pos = ast.literal_eval(msg)
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
    def run(self):
        # Get the initial position

        for i in range(EXPLORATIONS):
            find_goal = False
            find_target = False
            self.set_home()
            self.initial_pos = self.get_pos()
            path = []  # Keep the path to the goal
            path.append(self.initial_pos)
            while find_goal == False and find_target == False:
                pos = self.get_pos()
                # Select next movement randomly: north, south, east , west
                direction = random.randint(0, 4)
                if direction == 1:
                    value = "north"
                    pos_q_table = 0
                elif direction == 2:
                    value = "south"
                    pos_q_table = 2
                elif direction == 3:
                    value = "east"
                    pos_q_table = 1
                else:
                    value = "west"
                    pos_q_table = 3
                action = "command"
                msg = self.sock.execute(action, value, 0.02)
                new_pos = self.get_pos()
                # New position
                path.append(new_pos)
                # q of the action
                q_pos =self.qtable[str(pos)]
                action_q_pos = q_pos[pos_q_table]
                # Reward in new position
                r = self.rewards[str(new_pos)]
                # Max q in new position
                q_new_pos = self.qtable[str(new_pos)]
                max_q_new_pos = max(q_new_pos)
                # Testing the values
                print("q_pos = ", q_pos)
                print("q_new_pos = ", q_new_pos)
                print("max q new pos = ", max_q_new_pos)
                print("action q pos= ", action_q_pos)

                # Error
                error = ALPHA * ( r + DISCOUNT * max_q_new_pos - action_q_pos )
                new_q = action_q_pos + error
                if value == "north":
                    self.qtable[str(pos)] = [new_q, q_pos[1], q_pos[2], q_pos[3]]
                elif value == "east":
                    self.qtable[str(pos)] = [q_pos[0], new_q, q_pos[2], q_pos[3]]
                elif value == "south":
                    self.qtable[str(pos)] = [q_pos[0], q_pos[1], new_q, q_pos[3]]
                else:
                    self.qtable[str(pos)] = [q_pos[0], q_pos[1], q_pos[2], new_q]

                # Test
                # self.print_message(msg)
                if pos == self.goal:
                    find_goal = True
                if pos in self.targets_list:
                    find_target = True
                # Changing the values of the table using qlearning
            # Test
            # print("The new values for qTable are:")
            # self.print_qtable(self.qtable, self.max_coord)
        self.add_server_qtable_arrows(self.qtable,self.max_coord)
        input()
        self.clear_all_server_arrows(self.qtable, self.max_coord)


