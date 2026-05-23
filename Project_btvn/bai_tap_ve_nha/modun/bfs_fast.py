from collections import deque
from .demo import BaseAlg

class BFS_FAST(BaseAlg):
    def solve(self, start_state):
        self.logs = ["[BFS_FAST] Bắt đầu tìm kiếm với kiểm tra đích sớm..."]
        
        if self.is_goal(start_state[2]):
            self.logs.append("[BFS_FAST] Đích đã đạt ngay từ đầu!")
            return [], self.logs
        
        x, y, dirt = start_state
        explored = {start_state}
        frontier = deque([(start_state, [])])
        
        expanded = 0
        while frontier:
            state, path = frontier.popleft()
            expanded += 1
            
            for action in self.actions(state[0], state[1], state[2]):
                child_state = self.apply_action(state, action)
                
                if child_state not in explored:
                    explored.add(child_state)
                    
                    if self.is_goal(child_state[2]):
                        self.logs.append(f"[BFS_FAST] Tìm thấy lời giải! Số bước: {len(path) + 1}")
                        self.logs.append(f"[BFS_FAST] Nút đã mở rộng: {expanded}")
                        return path + [action], self.logs
                    
                    frontier.append((child_state, path + [action]))
        
        self.logs.append("[BFS_FAST] Không tìm thấy đường đi!")
        return None, self.logs