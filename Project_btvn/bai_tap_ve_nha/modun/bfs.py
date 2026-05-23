from collections import deque
from .demo import BaseAlg

class BFS(BaseAlg):
    def solve(self, start_state):
        self.logs = ["[BFS] Bắt đầu tìm kiếm..."]
        
        if self.is_goal(start_state[2]):
            self.logs.append("[BFS] Đích đã đạt ngay từ đầu!")
            return [], self.logs
        
        x, y, dirt = start_state
        frontier = deque([(start_state, [])])
        reached = {start_state}
        
        expanded = 0
        while frontier:
            state, path = frontier.popleft()
            expanded += 1
            
            for action in self.actions(state[0], state[1], state[2]):
                child_state = self.apply_action(state, action)
                new_path = path + [action]
                
                if self.is_goal(child_state[2]):
                    self.logs.append(f"[BFS] Tìm thấy lời giải! Số bước: {len(new_path)}")
                    self.logs.append(f"[BFS] Nút đã mở rộng: {expanded}")
                    return new_path, self.logs
                
                if child_state not in reached:
                    reached.add(child_state)
                    frontier.append((child_state, new_path))
        
        self.logs.append("[BFS] Không tìm thấy đường đi!")
        return None, self.logs