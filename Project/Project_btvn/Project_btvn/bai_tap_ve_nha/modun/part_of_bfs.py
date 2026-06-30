from collections import deque
from .demo import BaseAlg


class BFS_1_PHAN(BaseAlg):
    
    def __init__(self):
        super().__init__()
        self.start_node_used = None   

    def solve(self, start_state):
        self.start_node_used = None

        S1 = start_state
        S2 = self._make_second_start(start_state)

        queue   = deque()          # Hàng đợi BFS (FIFO)
        visited = set()            # Tập node đã thăm
        parent  = {}               # parent[node]  → node cha
        act_map = {}               # act_map[node] → action đã dùng
        origin  = {}               # origin[node]  → "S1" hoặc "S2"

        for label, state in [("S1", S1), ("S2", S2)]:
            if state not in visited:
                self._enqueue(queue, visited, parent, act_map, origin,
                              node=state, par=None, act=None, src=label)


                if self.is_goal(state[2]):
                    self.start_node_used = state
                    return [], [f"Goal ngay tại trạng thái xuất phát {label}!"]

        logs = []

        step = 0
        while queue:
            current = queue.popleft()
            step   += 1

            x, y, ground = current
            src_label     = origin[current]

            logs.append(
                f"[Bước {step}] Xét node | Nguồn: {src_label} | "
                f"Vị trí: ({x},{y}) | Ground: {ground}"
            )

            # Sinh tất cả node con từ current
            for action in self.actions(x, y, ground):
                child = self.apply_action(current, action)

                if child in visited:
                    continue  
                self._enqueue(queue, visited, parent, act_map, origin,
                              node=child, par=current, act=action,
                              src=origin[current])

                logs.append(
                    f"  → Sinh con | Action: {action:6s} | "
                    f"Node: ({child[0]},{child[1]}) | Ground: {child[2]}"
                )

                if self.is_goal(child[2]):
                    logs.append(
                        f" GOAL tìm thấy ní! "
                        f"Nguồn: {origin[child]} | "
                        f"Node: ({child[0]},{child[1]})"
                    )
                    self.start_node_used = self._trace_to_root(child, parent)
                    path = self._build_path(child, parent, act_map)
                    return path, logs

        self.start_node_used = S1
        logs.append(" Không tìm thấy goal sau khi duyệt hết không gian.")
        return None, logs

    def _enqueue(self, queue, visited, parent, act_map, origin,
                 node, par, act, src):
        visited.add(node)
        parent[node]  = par
        act_map[node] = act
        origin[node]  = src
        queue.append(node)

    def _make_second_start(self, start_state):
        x, y, ground = start_state
        for action in self.actions(x, y, ground):
            if action != "CLEAN":
                return self.apply_action(start_state, action)
        return start_state   # Fallback: nếu không có action di chuyển

    def _trace_to_root(self, node, parent):
        while parent[node] is not None:
            node = parent[node]
        return node

    def _build_path(self, goal_node, parent, act_map):
        path = []
        node = goal_node

        while parent[node] is not None:
            path.append(act_map[node])
            node = parent[node]

        path.reverse()   
        return path