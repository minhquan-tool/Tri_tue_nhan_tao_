from .demo import BaseAlg
class IDA_STAR(BaseAlg):
    def solve(self, start_state):

        def count_dirt(state):
            dirt_count = 0
            grid = state[2]
            for row in range(len(grid)):
                for col in range(len(grid[0])):
                    if grid[row][col] == 1:
                        dirt_count += 1
            return dirt_count

        algorithm_logs = []
        step_counter = 0
        iteration = 0

        def search(state, g_cost, path, current_path_states, threshold):
            nonlocal step_counter

            h_cost = count_dirt(state)    # h(n)
            f_cost = g_cost + h_cost      # f(n) = g(n) + h(n)

            if f_cost > threshold:
                return f_cost, None

            if self.is_goal(state[2]):
                return "FOUND", path

            step_counter += 1
            log_message = (
                f"IDA* Node #{step_counter:3d} | "
                f"Vị trí: ({state[0]},{state[1]}) | "
                f"g={g_cost:2d} | h={h_cost:2d} | f={f_cost:2d} | "
                f"Ngưỡng (threshold)={threshold}"
            )
            algorithm_logs.append(log_message)

            min_threshold = float('inf')
            all_actions = self.actions(state[0], state[1], state[2])

            for action in all_actions:
                next_state = self.apply_action(state, action)
                if next_state in current_path_states:
                    continue

                next_path = path + [action]
                current_path_states.add(next_state)

                status, result = search(
                    next_state, g_cost + 1, next_path,
                    current_path_states, threshold
                )

                if status == "FOUND":
                    return "FOUND", result

                current_path_states.remove(next_state)

                if status < min_threshold:
                    min_threshold = status

            return min_threshold, None

        threshold = count_dirt(start_state)  

        while threshold != float('inf'):
            iteration += 1
            algorithm_logs.append(
                f"=== Lần lặp {iteration}: threshold = {threshold} ==="
            )

            start_states_set = {start_state}
            status, result = search(
                start_state, 0, [], start_states_set, threshold
            )

            if status == "FOUND":
                algorithm_logs.append(
                    f">>> TÌM THẤY ĐÍCH sau {step_counter} bước duyệt"
                )
                return result, algorithm_logs

            if status == float('inf'):
                break

            threshold = status 

        algorithm_logs.append(">>> KHÔNG TÌM THẤY ĐÍCH")
        return None, algorithm_logs