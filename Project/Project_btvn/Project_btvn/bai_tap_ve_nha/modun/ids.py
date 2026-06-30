from collections import deque
from .demo import BaseAlg

class IDS(BaseAlg):
    def solve(self, start_state):
        depth_limit = 0
        total_steps = 0
        logs = []
        MAX_DEPTH = 30

        while depth_limit <= MAX_DEPTH:
            logs.append(f"[IDS] Bắt đầu tìm kiếm  Độ sâu Giới hạn:  {depth_limit} ---")
            status, path, total_steps, logs = self.depth_limited_search(start_state, depth_limit, total_steps, logs)

            if status == "FOUND":
                return path, logs
            elif status == "NOT_FOUND":
                logs.append(f"[IDS] : Tất cả các trạng thái có thể tiếp cận đều đã được kiểm tra | KHÔNG TÌM THẤY GIẢI PHÁP!")
                return None, logs

            depth_limit += 1

        logs.append(f"[IDS] Dừng hoạt động vì đã vượt quá giới hạn an toàn {MAX_DEPTH} tầng.")
        return None, logs

    def depth_limited_search(self, start_state, depth_limit, total_steps, logs):
        stack = deque()
        start_key = (start_state[0], start_state[1], start_state[2])
        stack.append((start_state, [], 0, frozenset([start_key])))

        has_nodes_beyond_limit = False

        while stack:
            current_state, current_path, current_depth, visited_keys = stack.pop()
            total_steps += 1

            if total_steps % 100 == 0 or current_depth == depth_limit:
                logs.append(
                    f"IDS Visiting Node #{total_steps} | "
                    f"Position: ({current_state[0]}, {current_state[1]}) | "
                    f"Depth: {current_depth}/{depth_limit}"
                )

            if self.is_goal(current_state[2]):
                logs.append(f"-> [IDS] Tìm thấy đích thành công tại Node #{total_steps}!")
                return "FOUND", current_path, total_steps, logs

            if current_depth == depth_limit:
                for action in self.actions(current_state[0], current_state[1], current_state[2]):
                    child_state = self.apply_action(current_state, action)
                    child_key = (child_state[0], child_state[1], child_state[2])
                    if child_key not in visited_keys:
                        has_nodes_beyond_limit = True
                        break
                continue

            for action in self.actions(current_state[0], current_state[1], current_state[2]):
                next_state = self.apply_action(current_state, action)
                next_key = (next_state[0], next_state[1], next_state[2])
                if next_key not in visited_keys:
                    next_visited = visited_keys | frozenset([next_key])
                    stack.append((next_state, current_path + [action], current_depth + 1, next_visited))

        if has_nodes_beyond_limit:
            return "REACHED_LIMIT", None, total_steps, logs
        else:
            return "NOT_FOUND", None, total_steps, logs