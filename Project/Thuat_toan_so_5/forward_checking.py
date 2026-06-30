COLORS = ["red", "orange", "blue", "yellow"]

class Forward_Checking:
    def __init__(self, ward_count, ward_names, neighbors):
        self.ward_count = ward_count
        self.ward_names = ward_names
        self.neighbors = neighbors
        self.assignment = {}
        self.domains = {i: COLORS.copy() for i in range(ward_count)}

    def select_unassigned_variable(self):
        unassigned = [i for i in range(self.ward_count) if i not in self.assignment]

        best = None
        best_domain_size = None
        best_degree = -1

        for ward in unassigned:
            domain_size = len(self.domains[ward])
            degree = len(self.neighbors[ward])

            if best is None or domain_size < best_domain_size or (
                domain_size == best_domain_size and degree > best_degree
            ):
                best = ward
                best_domain_size = domain_size
                best_degree = degree

        return best

    def forward_check(self, ward_index, color):
        removed_list = []
        ok = True

        for neighbor in self.neighbors[ward_index]:
            if neighbor in self.assignment:
                continue
            if color in self.domains[neighbor]:
                self.domains[neighbor].remove(color)
                removed_list.append((neighbor, color))
                if len(self.domains[neighbor]) == 0:
                    ok = False

        return ok, removed_list

    def undo_forward_check(self, color, removed_list):
        for neighbor, removed_color in removed_list:
            self.domains[neighbor].append(removed_color)

    def solve_generator(self):
        if len(self.assignment) == self.ward_count:
            yield ("done", None, None, self.assignment.copy(), [])
            return True

        ward_index = self.select_unassigned_variable()
        yield ("choose", ward_index, None, self.assignment.copy(), [])
        for color in self.domains[ward_index].copy():
            yield ("try", ward_index, color, self.assignment.copy(), [])

            self.assignment[ward_index] = color
            ok, removed_list = self.forward_check(ward_index, color)

            yield ("fc", ward_index, color, self.assignment.copy(), removed_list)

            if ok:
                yield ("valid", ward_index, color, self.assignment.copy(), [])

                result = yield from self.solve_generator()
                if result:
                    return True
            else:
                yield ("domain_empty", ward_index, color, self.assignment.copy(), [])

            self.undo_forward_check(color, removed_list)
            del self.assignment[ward_index]
            yield ("backtrack", ward_index, color, self.assignment.copy(), [])
        return False