from .demo import BaseAlg
import random

class RANDOM_HC(BaseAlg):
    def solve(self, start_state):
        def count_clean(state):
            clean_count = 0
            grid = state[2]
            for row in range(len(grid)):
                for col in range(len(grid[0])):
                    if grid[row][col] == 0:  
                        clean_count += 1
            return clean_count

        current_state = start_state
        path = []
        algorithm_logs = []
        step_counter = 0

        while True:
            step_counter = step_counter + 1
            current_h = count_clean(current_state)
            log_message = f"RANDOM_HC Duyệt Node #{step_counter} | Vị trí: ({current_state[0]},{current_state[1]}) | f(n): {current_h}"
            algorithm_logs.append(log_message)

            if self.is_goal(current_state[2]):
                return path, algorithm_logs

            all_actions = self.actions(current_state[0], current_state[1], current_state[2])

            
            better_neighbors = []
            for action in all_actions:
                next_state = self.apply_action(current_state, action)
                next_h = count_clean(next_state)
                if next_h > current_h: 
                    better_neighbors.append((next_state, action))

           
            if len(better_neighbors) == 0:
                break

         
            chosen_neighbor = random.choice(better_neighbors)
            current_state = chosen_neighbor[0]
            path.append(chosen_neighbor[1])

        return None, algorithm_logs