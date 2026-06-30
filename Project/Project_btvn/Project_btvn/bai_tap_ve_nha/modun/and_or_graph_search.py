from .demo import BaseAlg

class And_Or_Search(BaseAlg):
    def solve(self, start_state):
        logs = []
        plan = self.or_search(start_state, [], logs)

        if plan == "failure":
            return None, logs

        path = self.flatten_plan(plan)
        return path, logs

    def or_search(self, state, path, logs):
        logs.append(f"OR: {state[0]}, {state[1]}")
        if self.is_goal(state[2]):
            return []

        if state in path:
            return "failure"

        for action in self.actions(state[0], state[1], state[2]):
            result_states = self.results(state, action)

            plan = self.and_search(result_states, path + [state], logs)
            if plan != "failure":
                return [action, plan]

        return "failure"

    def and_search(self, states, path, logs):
        plans = {}
        for s in states:
            logs.append(f"AND: {s[0]}, {s[1]}")
            plan_s = self.or_search(s, path, logs)
            if plan_s == "failure":
                return "failure"

            plans[s] = plan_s
        return plans

    def results(self, state, action):
        next_state = self.apply_action(state, action)
        return [next_state]

    def flatten_plan(self, plan):
        result = []
        if plan == []:
            return result
        action = plan[0]
        sub_plan = plan[1]
        result.append(action)
        if isinstance(sub_plan, dict):
            for p in sub_plan.values():
                result.extend(self.flatten_plan(p))

        return result