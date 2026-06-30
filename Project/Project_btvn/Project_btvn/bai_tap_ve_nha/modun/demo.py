from abc import ABC, abstractmethod

class BaseAlg(ABC):
    def __init__(self):
        self.logs = []
    
    def is_goal(self, dirt):
        # chạy hết lưới, còn ô nào == 1 là chưa xong
        return all(cell != 1 for row in dirt for cell in row)
    
    def actions(self, x, y, ground):
        room = []
        m, n = len(ground), len(ground[0])
        

        if x > 0 and ground[x-1][y] != 2:
            room.append("UP")
        if x < m-1 and ground[x+1][y] != 2:
            room.append("DOWN")
        if y > 0 and ground[x][y-1] != 2:
            room.append("LEFT")
        if y < n-1 and ground[x][y+1] != 2:
            room.append("RIGHT")

        if 0 <= x < m and 0 <= y < n and ground[x][y] == 1:
            room.append("CLEAN")
        
        return room

    def apply_action(self, state, action):
        x, y, dirt = state
        dirt = [list(row) for row in dirt]  # copy để không đụng state cũ

        if action == "UP":      x -= 1
        elif action == "DOWN":  x += 1
        elif action == "LEFT":  y -= 1
        elif action == "RIGHT": y += 1
        elif action == "CLEAN": dirt[x][y] = 0
        
        return (x, y, tuple(tuple(row) for row in dirt))
    

    def solve(self, start_state):
        pass