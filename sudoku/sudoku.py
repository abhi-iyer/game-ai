from __future__ import print_function


class Grid:
    def __init__(self, problem):
        self.spots = [(i, j) for i in range(1, 10) for j in range(1, 10)]
        self.domains = {}

        # Need a dictionary that maps each spot to its related spots
        self.peers = {}
        self.marked = {}

        self.parse(problem)
        self.define_peers()

    def parse(self, problem):
        for i in range(0, 9):
            for j in range(0, 9):
                c = problem[i * 9 + j]
                if c == '.':
                    self.domains[(i + 1, j + 1)] = list(range(1, 10))
                else:
                    self.domains[(i + 1, j + 1)] = [ord(c) - 48]
                    self.marked[(i + 1, j + 1)] = self.domains[(i + 1, j + 1)]  # keep track of tiles initially marked

    def define_peers(self):
        for eachSpot in self.domains:
            self.peers[eachSpot] = []

            self.peers[eachSpot].extend([(eachSpot[0], x) for x in range(1, 10)])  # add all peers in the column
            self.peers[eachSpot].extend([(x, eachSpot[1]) for x in range(1, 10)])  # add all peers in the row
            self.peers[eachSpot].extend(self.get_box(eachSpot))  # add all peers in the box

            # remove duplicates of all tiles
            temp = self.peers[eachSpot]
            self.peers[eachSpot] = []
            for each in set(temp):
                self.peers[eachSpot].append(each)

            self.peers[eachSpot].remove(eachSpot)  # remove original tile itself

    def get_box(self, spot):
        # spots in each box (1 - 9) of the grid
        box1 = [(1, 1), (1, 2), (1, 3), (2, 1), (2, 2), (2, 3), (3, 1), (3, 2), (3, 3)]
        box2 = [(1, 4), (1, 5), (1, 6), (2, 4), (2, 5), (2, 6), (3, 4), (3, 5), (3, 6)]
        box3 = [(1, 7), (1, 8), (1, 9), (2, 7), (2, 8), (2, 9), (3, 7), (3, 8), (3, 9)]

        box4 = [(4, 1), (4, 2), (4, 3), (5, 1), (5, 2), (5, 3), (6, 1), (6, 2), (6, 3)]
        box5 = [(4, 4), (4, 5), (4, 6), (5, 4), (5, 5), (5, 6), (6, 4), (6, 5), (6, 6)]
        box6 = [(4, 7), (4, 8), (4, 9), (5, 7), (5, 8), (5, 9), (6, 7), (6, 8), (6, 9)]

        box7 = [(7, 1), (7, 2), (7, 3), (8, 1), (8, 2), (8, 3), (9, 1), (9, 2), (9, 3)]
        box8 = [(7, 4), (7, 5), (7, 6), (8, 4), (8, 5), (8, 6), (9, 4), (9, 5), (9, 6)]
        box9 = [(7, 7), (7, 8), (7, 9), (8, 7), (8, 8), (8, 9), (9, 7), (9, 8), (9, 9)]

        # if tile is in a specific box, return all tiles in that box
        if spot in box1:
            return box1
        if spot in box2:
            return box2
        if spot in box3:
            return box3
        if spot in box4:
            return box4
        if spot in box5:
            return box5
        if spot in box6:
            return box6
        if spot in box7:
            return box7
        if spot in box8:
            return box8
        if spot in box9:
            return box9

    def display(self):
        for i in range(0, 9):
            for j in range(0, 9):
                d = self.domains[(i + 1, j + 1)]
                if len(d) == 1:
                    print(d[0], end='')
                else:
                    print('.', end='')
                if j == 2 or j == 5:
                    print(" | ", end='')
            print()
            if i == 2 or i == 5:
                print("---------------")


# naive constraint solver
class Solver:
    def __init__(self, grid):
        # sigma is the assignment function
        self.sigma = {}
        self.grid = grid

        # sigma contains initial assignments
        for each in self.grid.marked:
            self.sigma[each] = self.grid.marked[each][0]

    def solve(self):
        solution = self.search(self.sigma)  # get solution

        if solution != None:  # if solution non-null, return that solution is possible
            return True
        else:
            return False

    def search(self, sigma):
        if (len(sigma) == 81):  # if all values are assigned
            return sigma

        # for every unmarked spot on the grid
        for spot in self.grid.domains:
            if spot not in sigma:
                selected_var = spot
                break

        for value in self.grid.domains[selected_var]:
            inferences = {}

            if self.consistent(selected_var, value, sigma):  # check if selected spot is consistent with current sigma
                sigma[selected_var] = value  # assign value to sigma

                inferences = self.infer(sigma)  # find inferences after placing selected spot

                if len(inferences) > 0:  # if inferences =/ failure
                    for each_inf in inferences:
                        sigma[each_inf] = inferences[each_inf]  # add each inference to sigma

                result = self.search(sigma)  # recursive function call

                if result and len(result) == 81:  # if result =/ failure
                    return result

            # remove selected spot and inferences from assignment
            if selected_var in sigma:
                del sigma[selected_var]  # remove selected spot

            if inferences is not None:  # remove each inference
                for each_inf in inferences:
                    if each_inf in sigma:
                        del sigma[each_inf]

        return None

    def consistent(self, spot, value, sigma):
        # consistency check
        for each in self.grid.peers[spot]:
            if each in sigma:
                if sigma[each] == value:  # if current tile has same value as any of its peers, return False
                    return False

        return True

    def infer(self, sigma):
        inferences = {}
        marked_values = []

        # for every spot on the grid that is not assigned
        for spot in self.grid.domains:
            if spot not in sigma:
                marked_values = self.marked_peers(spot, sigma)  # values of all assigned peers

                values = []
                for domain_value in self.grid.domains[spot]:  # find all possible values of a single spot
                    if domain_value not in marked_values:
                        values.append(domain_value)

                if (len(values) == 1 and self.consistent(spot, values[0], dict(list(sigma.items()) +
                                                                               list(inferences.items())))):
                    # if only one inference is possible (and is consistent with board and
                    # inferences already made), it is valid
                    inferences[spot] = values[0]  # keep track of inference made

        return inferences

    def marked_peers(self, spot, sigma):
        marked_values = []

        for each in self.grid.peers[spot]:  # for every peer for a spot that is marked, return all marked peer values
            if each in sigma:
                marked_values.append(sigma[each])

        return marked_values

    def displaySolution(self, sigma):
        # method to display final solution on screen
        for i in range(0, 9):
            for j in range(0, 9):
                print(sigma[(i + 1, j + 1)], end=' ')
                if j == 2 or j == 5:
                    print(" | ", end=' ')
            print()
            if i == 2 or i == 5:
                print("-------------------------")


# heuristically guided solver that prunes domain
class PrunedSolver:
    def __init__(self, grid):
        # sigma is the assignment function
        self.sigma = {}
        self.grid = grid
        self.domains = self.grid.domains
        self.peers = self.grid.peers

        # sigma contains initial assignments
        for each in self.grid.marked:
            self.sigma[each] = self.grid.marked[each][0]

        # prune domain to begin with (rule out possible values based on already assigned tiles)
        for assigned_spot in self.sigma:
            for spot in self.peers[assigned_spot]:
                if spot not in self.sigma and self.sigma[assigned_spot] in self.domains:
                    self.domains[spot].remove(self.sigma[assigned_spot])

    def solve(self):
        solution = self.search(self.sigma, self.domains, self.peers)  # get solution to puzzle

        if solution:  # if solution is non-null, return that solution is possible
            return True
        else:
            return False

    def search(self, sigma, domains, peers):
        if len(sigma) == 81:  # if all values are assigned
            return sigma

        # pop an unmarked spot that has the most assigned peers already
        selected_var = self.spot_with_max_assigned_peers(sigma, peers, domains)

        for value in domains[selected_var]:
            inferences = {}

            if (self.consistent(selected_var, value, sigma,
                                peers)):  # check if selected spot is consistent with current sigma
                sigma[selected_var] = value  # assign value to sigma

                inferences = self.infer(sigma, peers, domains)  # find inferences after placing selected spot

                if len(inferences) > 0:  # if inferences =/ failure
                    for each_inf in inferences:
                        sigma[each_inf] = inferences[each_inf]  # add each inference to sigma

                result = self.search(sigma, domains, peers)  # recursive function call

                if result and len(result) == 81:  # if result =/ failure
                    return result

            # remove selected spot and inferences from assignment
            if selected_var in sigma:
                del sigma[selected_var]  # remove selected spot

            if inferences is not None:  # remove each inference
                for each_inf in inferences:
                    if each_inf in sigma:
                        del sigma[each_inf]

        return None

    def consistent(self, spot, value, sigma, peers):
        # consistency check
        for each in peers[spot]:
            if each in sigma:
                if sigma[each] == value:  # if current value has same value as any of its peers, return false
                    return False

        return True

    def infer(self, sigma, peers, domains):
        inferences = {}
        marked_values = []

        # for every spot on the grid that is not assigned
        for spot in domains:
            if spot not in sigma:
                marked_values = self.marked_peers(spot, sigma, peers)  # values of all assigned peers

                values = []
                for domain_value in domains[spot]:
                    if domain_value not in marked_values:  # find all possible values of a single spot
                        values.append(domain_value)

                if (len(values) == 1 and self.consistent(spot, values[0],
                                                         dict(list(sigma.items()) + list(inferences.items())),
                                                         peers)):  # if only one inference is possible (and is consistent with board and inferences already made), it is valid
                    inferences[spot] = values[0]  # keep track of inference made

        return inferences

    def spot_with_max_assigned_peers(self, sigma, peers, domains):
        markedPeers = {}
        sortedPeers = {}

        for spot in domains:
            if spot not in sigma:  # for each unmarked spot, find its marked peers
                markedPeers[spot] = self.marked_peers(spot, sigma, peers)

        sortedPeers = {k: markedPeers[k] for k in sorted(markedPeers, key=lambda k: len(markedPeers[k]),
                                                         reverse=True)}  # sort all unmarked spots by number of already assigned peers

        return list(sortedPeers.keys())[
            0]  # return first value - this unmarked spot has the highest number of assigned peers

    def marked_peers(self, spot, sigma, peers):
        marked_values = []

        for each in peers[spot]:  # for every peer that is already assigned, store assigned value
            if each in sigma:
                marked_values.append(sigma[each])

        return list(set(marked_values))  # remove duplicates and return

    def displaySolution(self, sigma):
        # method to display final solution
        for i in range(0, 9):
            for j in range(0, 9):
                print(sigma[(i + 1, j + 1)], end=' ')
                if j == 2 or j == 5:
                    print(" | ", end=' ')
            print()
            if i == 2 or i == 5:
                print("-------------------------")


# two easy puzzles
easy = ["..3.2.6..9..3.5..1..18.64....81.29..7.......8..67.82....26.95..8..2.3..9..5.1.3..",
        "2...8.3...6..7..84.3.5..2.9...1.54.8.........4.27.6...3.1..7.4.72..4..6...4.1...3"]

# two hard puzzles
hard = ["4.....8.5.3..........7......2.....6.....8.4......1.......6.3.7.5..2.....1.4......",
        "52...6.........7.13...........4..8..6......5...........418.........3..2...87....."]

print("====Problem (easy puzzle)====")
g1 = Grid(easy[1])
# Display the original problem
g1.display()
s = Solver(g1)

if s.solve():
    print("====Solution===")
    # Display the solution
    s.displaySolution(s.sigma)
else:
    print("==No solution==")

print()
print()

print("====Problem (hard puzzle)====")
g2 = Grid(hard[1])
# Display the original problem
g2.display()
pruned_solver = PrunedSolver(g2)

if pruned_solver.solve():
    print("====Solution===")
    # Display the solution
    pruned_solver.displaySolution(pruned_solver.sigma)
else:
    print("==No solution==")
