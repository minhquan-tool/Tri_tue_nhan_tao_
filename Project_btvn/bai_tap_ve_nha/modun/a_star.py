import heapq
from .demo import BaseAlg

class A_STAR(BaseAlg):
    def heuristic(self, state):
        x, y, dirt = state
        if isinstance(dirt, (set, frozenset, tuple, list)):
            return len(dirt)
        return bin(dirt).count('1')

    def solve(self, start_state):
        self.logs = ["[A*] Bắt đầu tìm kiếm..."]

        if self.is_goal(start_state[2]):
            self.logs.append("[A*] Đích đã đạt ngay từ đầu!")
            return [], self.logs

 
        h_start = self.heuristic(start_state)
        counter = 0
        frontier = []
        heapq.heappush(frontier, (h_start, 0, counter, start_state, []))

        frontier_map = {start_state: (h_start, 0)}
        reached = {} 
        expanded = 0
        while frontier:
            f, g, _, state, path = heapq.heappop(frontier)

            if state in reached:
                continue
            current_fg = frontier_map.get(state)
            if current_fg is None or g > current_fg[1]:
                continue

            expanded += 1

            if self.is_goal(state[2]):
                self.logs.append(f"[A*] Tìm được đường đi! Số bước: {len(path)}")
                self.logs.append(f"[A*] Nút đã mở rộng: {expanded}")
                return path, self.logs

            frontier_map.pop(state, None)
            reached[state] = g

 
            for action in self.actions(state[0], state[1], state[2]):
                child_state = self.apply_action(state, action)
                g_new = g + 1 
                f_new = g_new + self.heuristic(child_state)
                if child_state in reached:
                    if g_new >= reached[child_state]:
                     
                        continue
                    else:
                        del reached[child_state]

                if child_state in frontier_map:
                    if g_new >= frontier_map[child_state][1]:
                   
                        continue
                    else:
                    
                        frontier_map[child_state] = (f_new, g_new)

          
                else:
                    frontier_map[child_state] = (f_new, g_new)

                counter += 1
                heapq.heappush(frontier, (f_new, g_new, counter, child_state, path + [action]))

   
        self.logs.append("[A*] Không tìm thấy đường đi!")
        return None, self.logs
