from .demo import BaseAlg
import random
import math


class SIMULATED_ANNEALING(BaseAlg):
    def __init__(self):
        self.T0 = 100;self.Tmin = 0.2;self.alpha = 0.85
    def heuristic(self, state):
        robot_r, robot_c, grid = state
        dirt_positions = []
        for r in range(len(grid)):
            for c in range(len(grid[0])):
                if grid[r][c] == 1:
                    dirt_positions.append((r, c))

        # Goal
        if not dirt_positions:
            return 0

        nearest = min(
            abs(robot_r - r) + abs(robot_c - c)
            for r, c in dirt_positions
        )

        return len(dirt_positions) * 5 + nearest


    def random_neighbor(self, state):
        r, c, room = state
        possible_actions = self.actions(r, c, room)
        if not possible_actions:
            return None, None
        if "CLEAN" in possible_actions:
            action = "CLEAN"
        else:
            action = random.choice(possible_actions)
        next_state = self.apply_action(state, action)
        return next_state, action
    def solve(self, start_state):
        logs = []
        # current_state = start
        current_state = start_state
        current_path = []
        # T = T0
        T = self.T0
        step = 0
        limit = 500
        logs.append(
            f"SIMULATED ANNEALING START | "
            f"T0={self.T0} | "
            f"Tmin={self.Tmin} | "
            f"alpha={self.alpha}"
        )

        while T > self.Tmin and step < limit:
            step += 1
            current_h = self.heuristic(current_state)
            r, c, _ = current_state
            logs.append(
                f"\nStep {step} | "
                f"Pos=({r},{c}) | "
                f"h={current_h} | "
                f"T={round(T, 2)}"
            )
            if self.is_goal(current_state[2]):
                logs.append("GOAL rồi ní!")
                logs.append(
                    f"Tìm thấy lời giải sau {step} bước"
                )
                logs.append(
                    f"Path length = {len(current_path)}"
                )
                return current_path, logs
            next_state, action = self.random_neighbor(
                current_state
            )
            if next_state is None:
                logs.append(
                    "Không có neighbor nào khả thi"
                )
                break

            next_h = self.heuristic(next_state)
            # Delta = h(next) - h(current)
            delta = next_h - current_h

            logs.append(
                f"Action={action} | "
                f"Next h={next_h} | "
                f"Delta={delta}"
            )
            if delta < 0:
                current_state = next_state
                current_path.append(action)
                logs.append(
                    "Chấp nhận state tốt hơn"
                )

            elif delta == 0:
                logs.append(
                    "Reject equal state"
                )

            else:
                probability = math.exp(-delta / T)
                rand_value = random.random()
                logs.append(
                    f"Probability="
                    f"{round(probability,4)} | "
                    f"Random="
                    f"{round(rand_value,4)}"
                )
                # chấp nhận với xác suất
                if rand_value < probability:
                    current_state = next_state
                    current_path.append(action)
                    logs.append(
                        "Chấp nhận state tệ hơn"
                    )
                else:
                    logs.append(
                        "Từ chối state"
                    )
            T = self.alpha * T
        logs.append("FAILED")
        return None, logs