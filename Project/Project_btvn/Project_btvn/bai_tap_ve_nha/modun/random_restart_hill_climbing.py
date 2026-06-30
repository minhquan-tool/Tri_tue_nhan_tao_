from .demo import BaseAlg
import random

class RANDOM_RESTART_HC(BaseAlg):
    def solve(self, start_state):
        def manhattan_h(state):
            robot_row, robot_col = state[0], state[1]
            grid = state[2]
            total = 0
            for r in range(len(grid)):
                for c in range(len(grid[r])):
                    if grid[r][c] == 1:
                        total += abs(robot_row - r) + abs(robot_col - c)
            return total

        def make_random_state(ref_state):
            grid = [row[:] for row in ref_state[2]]  
            rows = len(grid)
            cols = len(grid[0])
            rand_row = random.randint(0, rows - 1)
            rand_col = random.randint(0, cols - 1)
            return (rand_row, rand_col, grid)

        MAX_RESTART = 30
        algorithm_logs = []
        step_counter = 0
        best_path = None    

        for i in range(MAX_RESTART):
            algorithm_logs.append(f"--- RESTART {i} ---")


            current_state = start_state if i == 0 else make_random_state(start_state)

            path = []
            visited = set()

            while True:
                step_counter += 1
                current_h = manhattan_h(current_state)
                algorithm_logs.append(
                    f"RANDOM_RESTART_HC Lượt #{i} | "
                    f"Bước #{step_counter} | "
                    f"Vị trí: ({current_state[0]},{current_state[1]}) | "
                    f"h(n): {current_h}"
                )

                if self.is_goal(current_state[2]):
                    algorithm_logs.append(
                        f"Tìm thấy Goal tại lượt #{i}, bước #{step_counter}!"
                    )
                    return path, algorithm_logs

                state_key = (current_state[0], current_state[1],
                             tuple(tuple(r) for r in current_state[2]))
                if state_key in visited:
                    algorithm_logs.append(f"Vòng lặp tại lượt #{i} → Restart!")
                    break
                visited.add(state_key)

                all_actions = self.actions(
                    current_state[0], current_state[1], current_state[2]
                )

                if "CLEAN" in all_actions:
                    current_state = self.apply_action(current_state, "CLEAN")
                    path.append("CLEAN")
                    continue

                better_neighbors = []
                for action in all_actions:
                    next_state = self.apply_action(current_state, action)
                    next_h = manhattan_h(next_state)
                    if next_h < current_h:
                        better_neighbors.append((next_state, action))

                if not better_neighbors:
                    algorithm_logs.append(
                        f"Bị kẹt tại lượt #{i}, bước #{step_counter} | "
                        f"Vị trí: ({current_state[0]},{current_state[1]}) → Restart!"
                    )
        
                    if best_path is None or len(path) > len(best_path):
                        best_path = path[:]
                    break

                chosen_neighbor = random.choice(better_neighbors)
                current_state = chosen_neighbor[0]
                path.append(chosen_neighbor[1])

        algorithm_logs.append(f"Thất bại sau {MAX_RESTART} lượt restart!")
        return best_path, algorithm_logs  