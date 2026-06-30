from .demo import BaseAlg
import random


class LOCAL_BEAM_SEARCH(BaseAlg):
    def __init__(self):
        self.k = 2

    def heuristic(self, state):
        grid = state[2]
        dirt_count = 0

        for row in grid:
            dirt_count += row.count(1)
        return dirt_count

    def random_state(self, start_state):

        grid = [row[:] for row in start_state[2]]

        rows = len(grid)
        cols = len(grid[0])

        rand_r = random.randint(0, rows - 1)
        rand_c = random.randint(0, cols - 1)

        return (rand_r, rand_c, grid)

    def state_key(self, state):

        return (
            state[0],
            state[1],
            tuple(tuple(row) for row in state[2])
        )


    def solve(self, start_state):

        logs = []
        current_state_set = []

        current_state_set.append({
            "state": start_state,
            "path": []
        })

        for _ in range(self.k - 1):

            current_state_set.append({

                "state": self.random_state(start_state),

                "path": []
            })

        logs.append(
            f"LOCAL BEAM SEARCH | k={self.k}"
        )
        visited = set()
        limit = 200
        step = 0
        while step < limit:

            step += 1

            neighbor_states = []

            logs.append(
                f"\n===== ITERATION {step} ====="
            )
            for idx, node in enumerate(current_state_set):

                current_state = node["state"]
                current_path = node["path"]

                r, c, room = current_state

                h = self.heuristic(current_state)

                logs.append(
                    f"Beam[{idx}] "
                    f"Pos=({r},{c}) "
                    f"h={h}"
                )

                # GOAL TEST
                if self.is_goal(room):

                    logs.append("GOAL FOUND")

                    return current_path, logs

                actions = self.actions(r, c, room)

                for action in actions:

                    next_state = self.apply_action(
                        current_state,
                        action
                    )

                    key = self.state_key(next_state)

                    # tránh lặp
                    if key in visited:
                        continue

                    visited.add(key)

                    next_path = current_path + [action]

                    neighbor_states.append({

                        "state": next_state,
                        "path": next_path
                    })

            if len(neighbor_states) == 0:

                logs.append(
                    "No more neighbors"
                )

                break
            logs.append(
                f"Generated "
                f"{len(neighbor_states)} neighbors"
            )
            neighbor_states.sort(

                key=lambda x:
                self.heuristic(x["state"])
            )

            current_state_set = neighbor_states[:self.k]

            logs.append(
                f"Select top {self.k} states:"
            )

            for idx, node in enumerate(current_state_set):

                s = node["state"]

                logs.append(

                    f"Top[{idx}] "
                    f"Pos=({s[0]},{s[1]}) "
                    f"h={self.heuristic(s)}"
                )

        logs.append("FAILED")

        return None, logs