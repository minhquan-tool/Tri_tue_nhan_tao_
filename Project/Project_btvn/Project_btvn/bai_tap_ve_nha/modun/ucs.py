import heapq
from collections import deque
from .demo import BaseAlg

class UCS(BaseAlg):
    def solve(self, start_state):
        self.logs = ["[UCS] Bắt đầu tìm kiếm..."]

        if self.is_goal(start_state[2]):
            self.logs.append("[UCS] Đích đã đạt ngay từ đầu!")
            return [], self.logs

        counter = 0
        frontier = [(0, counter, start_state, [])]
        visited = {}          # state -> cost nhỏ nhất đã xử lý

        expanded = 0
        while frontier:
            cost, _, state, path = heapq.heappop(frontier)

            if state in visited and visited[state] <= cost:
                continue
            visited[state] = cost
            expanded += 1

            for action in self.actions(state[0], state[1], state[2]):
                child_state = self.apply_action(state, action)
                step_cost = 1  # Mỗi hành động có chi phí là 1
                new_cost = cost + step_cost
                new_path = path + [action]

                if self.is_goal(child_state[2]):
                    self.logs.append(
                        f"[UCS] Tìm thấy lời giải! "
                        f"Số bước: {len(new_path)} | Chi phí: {new_cost}"
                    )
                    self.logs.append(f"[UCS] Nút đã mở rộng: {expanded}")
                    return new_path, self.logs

                if child_state not in visited or visited[child_state] > new_cost:
                    counter += 1
                    heapq.heappush(
                        frontier,
                        (new_cost, counter, child_state, new_path)
                    )

        self.logs.append("[UCS] Không tìm thấy đường đi!")
        return None, self.logs