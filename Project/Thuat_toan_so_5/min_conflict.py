import random


class Min_Conflicts:
    def __init__(self, ward_count, ward_names, neighbors, max_steps=1000, colors=None):
        self.ward_count = ward_count
        self.ward_names = ward_names
        self.neighbors = neighbors
        self.max_steps = max_steps
        self.colors = colors if colors is not None else ["red", "orange", "blue", "yellow"]
        self.assignment = {}

    def initial_assignment(self):
        self.assignment = {
            var: random.choice(self.colors)
            for var in range(self.ward_count)
        }

    def count_conflicts(self, var, color):
        count = 0
        for neighbor in self.neighbors[var]:
            if self.assignment.get(neighbor) == color:
                count += 1
        return count

    def get_conflicted_variables(self):
        conflicted = []
        for var in range(self.ward_count):
            if self.count_conflicts(var, self.assignment[var]) > 0:
                conflicted.append(var)
        return conflicted

    def get_conflict_pairs(self):
        pairs = []
        for var in range(self.ward_count):
            for neighbor in self.neighbors[var]:
                if var < neighbor and self.assignment.get(var) == self.assignment.get(neighbor):
                    pairs.append((var, neighbor))
        return pairs

    def choose_best_color(self, var):
        color_results = [
            (color, self.count_conflicts(var, color))
            for color in self.colors
        ]
        min_conflict = min(count for _, count in color_results)
        best_colors = [color for color, count in color_results if count == min_conflict]
        chosen_color = random.choice(best_colors)
        return color_results, chosen_color

    def solve_generator(self):
        self.initial_assignment()
        yield ("mc_init", None, None, self.assignment.copy())

        for step in range(1, self.max_steps + 1):
            conflict_pairs = self.get_conflict_pairs()
            yield ("mc_check", None, None, self.assignment.copy(), conflict_pairs)

            if not conflict_pairs:
                yield ("done", None, None, self.assignment.copy())
                return True

            conflicted_vars = self.get_conflicted_variables()
            var = random.choice(conflicted_vars)
            yield ("mc_choose", var, None, self.assignment.copy(), conflict_pairs)

            color_results, chosen_color = self.choose_best_color(var)
            yield ("mc_try_all", var, chosen_color, self.assignment.copy(), color_results)

            self.assignment[var] = chosen_color
            yield ("mc_update", var, chosen_color, self.assignment.copy())

        yield ("failed", None, None, self.assignment.copy())
        return False