from collections import deque


class AC_3:
    def __init__(self, ward_count, ward_names, neighbors, colors=None):
      
        self.ward_count = ward_count
        self.ward_names = ward_names
        self.neighbors = neighbors
        self.colors = colors if colors is not None else ["red", "orange", "blue", "yellow"]

        # domain[var] = danh sách giá trị còn hợp lệ cho biến var
        self.domains = {
            var: self.colors.copy()
            for var in range(self.ward_count)
        }
        self.assignment = {}

    def revise(self, xi, xj):
        removed = []
        for x in self.domains[xi][:]:
            # kiểm tra có tồn tại y trong domain(xj) thỏa mãn ràng buộc không
            has_support = any(x != y for y in self.domains[xj])
            if not has_support:
                self.domains[xi].remove(x)
                removed.append(x)
        return removed

    def ac3(self):
        queue = deque()
        seen_arcs = set()
        for xi in range(self.ward_count):
            for xj in self.neighbors[xi]:
                arc = (xi, xj)
                if arc not in seen_arcs:
                    seen_arcs.add(arc)
                    queue.append(arc)

        yield ("ac3_init", None, None, self.assignment.copy(), list(queue), self.copy_domains())

        while queue:
            xi, xj = queue.popleft()
            yield ("ac3_check", xi, xj, self.assignment.copy(), list(queue), self.copy_domains())

            removed = self.revise(xi, xj)
            if removed:
                yield ("ac3_remove", xi, xj, self.assignment.copy(), removed, self.copy_domains())

                if len(self.domains[xi]) == 0:
                    yield ("domain_empty", xi, None, self.assignment.copy())
                    return False

                for xk in self.neighbors[xi]:
                    if xk != xj:
                        arc = (xk, xi)
                        if arc not in queue:  
                            queue.append(arc)
                            yield ("ac3_add", xk, xi, self.assignment.copy(), list(queue), self.copy_domains())

        return True

    def is_valid(self, var, color):
        for neighbor in self.neighbors[var]:
            if self.assignment.get(neighbor) == color:
                return False
        return True

    def select_unassigned_variable(self):
        for var in range(self.ward_count):
            if var not in self.assignment:
                return var
        return None

    def backtrack(self):
        if len(self.assignment) == self.ward_count:
            yield ("done", None, None, self.assignment.copy())
            return True

        var = self.select_unassigned_variable()
        yield ("choose", var, None, self.assignment.copy())

        for color in self.domains[var]:
            yield ("try", var, color, self.assignment.copy())

            if self.is_valid(var, color):
                self.assignment[var] = color
                yield ("valid", var, color, self.assignment.copy())

                result = yield from self.backtrack()
                if result:
                    return True

                del self.assignment[var]
                yield ("backtrack", var, color, self.assignment.copy())
            else:
                yield ("invalid", var, color, self.assignment.copy())

        return False

    def solve_generator(self):
        ac3_result = yield from self.ac3()
        if not ac3_result:
            yield ("failed", None, None, self.assignment.copy())
            return False

        yield ("ac3_done", None, None, self.assignment.copy(), None, self.copy_domains())

        bt_result = yield from self.backtrack()
        if not bt_result:
            yield ("failed", None, None, self.assignment.copy())

        return bt_result

    def copy_domains(self):
        return {
            var: values.copy()
            for var, values in self.domains.items()
        }