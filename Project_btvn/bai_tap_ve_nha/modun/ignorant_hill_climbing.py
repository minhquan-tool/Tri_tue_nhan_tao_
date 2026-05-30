from .demo import BaseAlg

class IGNORANT_HC(BaseAlg):
    def solve(self, start_state):
        def count_clean(state):
            clean_count = 0
            grid = state[2]
            for row in range(len(grid)):
                for col in range(len(grid[0])):
                    if grid[row][col] == 0:  # 0 = sạch
                        clean_count += 1
            return clean_count

        current_state = start_state
        path = []
        algorithm_logs = []
        step_counter = 0

        while True:
            step_counter += 1
            current_h = count_clean(current_state)
            log_message = (
                f"Ignorant_HC Duyệt Node #{step_counter} | "
                f"Vị trí: ({current_state[0]},{current_state[1]}) | "
                f"f(n): {current_h}"
            )
            algorithm_logs.append(log_message)

            if self.is_goal(current_state[2]):
                return path, algorithm_logs

            all_actions = self.actions(
                current_state[0], current_state[1], current_state[2]
            )

           
            best_action = None
            best_state = None
            best_h = current_h

            for action in all_actions:
                next_state = self.apply_action(current_state, action)
                next_h = count_clean(next_state)

                if next_h > best_h: 
                    best_h = next_h
                    best_state = next_state
                    best_action = action

  
            if best_state is not None:
                current_state = best_state
                path.append(best_action)
            else:
                break

        return None, algorithm_logs