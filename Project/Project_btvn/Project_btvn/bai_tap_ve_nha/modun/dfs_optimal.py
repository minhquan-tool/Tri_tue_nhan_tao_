
from .demo import BaseAlg

class DFS_OPTIMAL(BaseAlg):
    def solve(self, start_state):
        self.logs = ["[DFS_OPTIMAL] Bắt đầu tìm kiếm sâu tối ưu..."]
        
        if self.is_goal(start_state[2]):
            self.logs.append("[DFS_OPTIMAL] Đích đã đạt ngay từ đầu!")
            return [], self.logs
        
        stack = [(start_state, [])]
        explored = set([start_state])
        
        expanded = 0
        while stack:
            state, path = stack.pop()
            expanded += 1
            
            if self.is_goal(state[2]):
                self.logs.append(f"[DFS_OPTIMAL] Tìm thấy lời giải! Số bước: {len(path)}")
                self.logs.append(f"[DFS_OPTIMAL] Nút đã mở rộng: {expanded}")
                return path, self.logs
            
            for action in self.actions(state[0], state[1], state[2]):
                child_state = self.apply_action(state, action)
                
                if child_state not in explored:
                    explored.add(child_state)
                    stack.append((child_state, path + [action]))
        
        self.logs.append("[DFS_OPTIMAL] Không tìm thấy đường đi!")
        return None, self.logs