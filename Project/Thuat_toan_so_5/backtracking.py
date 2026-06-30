COLORS = ["red", "orange", "blue", "yellow"]

class Backtracking:
    def __init__(self, ward_count, ward_names, neighbors):
        self.ward_count = ward_count
        self.ward_names = ward_names
        self.neighbors = neighbors
        self.assignment = {}

    def is_valid(self, ward_index, color):
        for neighbor in self.neighbors[ward_index]:
            if self.assignment.get(neighbor) == color:
                return False
        return True

    def select_unassigned_variable(self):
        for i in range(self.ward_count):
            if i not in self.assignment:
                return i
        return None

    def solve_generator(self):
        if len(self.assignment) == self.ward_count:
            yield ("done", None, None, self.assignment.copy())
            return True

        ward_index = self.select_unassigned_variable()
        yield ("choose", ward_index, None, self.assignment.copy())

        for color in COLORS:
            yield ("try", ward_index, color, self.assignment.copy())

            if not self.is_valid(ward_index, color):
                yield ("invalid", ward_index, color, self.assignment.copy())
                continue

            self.assignment[ward_index] = color
            yield ("valid", ward_index, color, self.assignment.copy())


            success = yield from self.solve_generator()
            if success:
                return True

            del self.assignment[ward_index]
            yield ("backtrack", ward_index, color, self.assignment.copy())


        return False