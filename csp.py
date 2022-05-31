def count(seq):
    return sum(bool(x) for x in seq)


def first(iterable, default=None):
    try:
        return iterable[0]
    except IndexError:
        return default
    except TypeError:
        return next(iterable, default)

class CSP():


    def __init__(self, variables, domains, neighbors, constraints):

        variables = variables or list(domains.keys())

        self.variables = variables
        self.domains = domains
        self.neighbors = neighbors
        self.constraints = constraints
        self.curr_domains = None
        self.nassigns = 0

    def assign(self, var, val, assignment):
        assignment[var] = val
        self.nassigns += 1

    def unassign(self, var, assignment):
        if var in assignment:
            del assignment[var]

    def nconflicts(self, var, val, assignment):

        def conflict(var2):
            return (var2 in assignment and
                    not self.constraints(var, val, var2, assignment[var2]))
        return count(conflict(v) for v in self.neighbors[var])

    def goal_test(self, state):

        assignment = dict(state)
        return (len(assignment) == len(self.variables)
                and all(self.nconflicts(variables, assignment[variables], assignment) == 0
                        for variables in self.variables))


    def support_pruning(self):

        if self.curr_domains is None:
            self.curr_domains = {v: list(self.domains[v]) for v in self.variables}

    def suppose(self, var, value):

        self.support_pruning()
        removals = [(var, a) for a in self.curr_domains[var] if a != value]
        self.curr_domains[var] = [value]
        return removals

    def prune(self, var, value, removals):

        self.curr_domains[var].remove(value)
        if removals is not None:
            removals.append((var, value))

    def choices(self, var):

        return (self.curr_domains or self.domains)[var]


    def restore(self, removals):

        for B, b in removals:
            self.curr_domains[B].append(b)


def AC3(csp, queue=None, removals=None):

    if queue is None:
        queue = [(Xi, Xk) for Xi in csp.variables for Xk in csp.neighbors[Xi]]
    csp.support_pruning()
    while queue:
        (Xi, Xj) = queue.pop()
        if revise(csp, Xi, Xj, removals):
            if not csp.curr_domains[Xi]:
                return False
            for Xk in csp.neighbors[Xi]:
                if Xk != Xj:
                    queue.append((Xk, Xi))
    return True


def forward_checking(csp, var, value, assignment, removals):
    csp.support_pruning()
    for B in csp.neighbors[var]:
        if B not in assignment:
            for b in csp.curr_domains[B][:]:
                if not csp.constraints(var, value, B, b):
                    csp.prune(B, b, removals)
            if not csp.curr_domains[B]:
                return False
    return True



def revise(csp, Xi, Xj, removals):
    revised = False
    for x in csp.curr_domains[Xi][:]:
        if all(not csp.constraints(Xi, x, Xj, y) for y in csp.curr_domains[Xj]):
            csp.prune(Xi, x, removals)
            revised = True
    return revised


def first_unassigned_variable(assignment, csp):
    return first([var for var in csp.variables if var not in assignment])


def unordered_domain_values(var, assignment, csp):
    return csp.choices(var)

def no_inference(csp, var, value, assignment, removals):
    return True

def arc_consistency(csp, var, value, assignment, removals):
    MAC = AC3(csp, [(X, var) for X in csp.neighbors[var]], removals)

    return MAC

