import csp
from sys import stderr
from itertools import product, permutations
from functools import reduce
from random import  shuffle, randint, choice
from time import time
from csv import writer
import numpy as np



def generate(size):

    initial_board = []
    for i in range(size):
        temp = []
        for j in range(size):
            temp.append( ( (i+j)%size )+1 )
        initial_board.append(temp)
    for _ in range(size):
        shuffle(initial_board)

    board = {}
    for i in range(size):
        for j in range(size):
            board[(i+1,j+1)] = initial_board[j][i]

    uncaged = sorted(board.keys(), key=lambda var: var[1])

    cliques = []
    while uncaged:

        cliques.append([])

        csize = np.random.choice(range(1, 5), p=[0.1, 0.4, 0.3, 0.2])

        cell = uncaged[0]

        uncaged.remove(cell)

        cliques[-1].append(cell)

        for _ in range(csize - 1):

            adjs = []
            for cell2 in uncaged:
                temp =[cell[0]-cell2[0],cell[1]-cell2[1]]
                if( (temp[0] ==0 and abs(temp[1])==1 ) or ( temp[1]==0 and abs(temp[0])==1 )  ):
                    adjs.append(cell2)

            cell = choice(adjs) if adjs else None

            if not cell:
                break

            uncaged.remove(cell)

            cliques[-1].append(cell)

        csize = len(cliques[-1])
        if csize == 1:
            cell = cliques[-1][0]
            cliques[-1] = ((cell, ), '', board[cell])
            continue
        elif csize == 2:
            fst, snd = cliques[-1][0], cliques[-1][1]
            if board[fst] / board[snd] > 0 and not board[fst] % board[snd]:
                operator = "/"
            elif board[fst] - board[snd] > 0:
                operator = "-"
            else:
                operator = choice("+*")
        else:
            operator = choice("+*")

        target = reduce(operation(operator), [board[cell] for cell in cliques[-1]])

        cliques[-1] = (tuple(cliques[-1]), operator, int(target))

    return size, cliques


def RowXorCol(xy1, xy2):

    return (xy1[0] == xy2[0]) != (xy1[1] == xy2[1])


def conflicting(A, a, B, b):

    for i in range(len(A)):
        for j in range(len(B)):
            mA = A[i]
            mB = B[j]

            ma = a[i]
            mb = b[j]
            if RowXorCol(mA, mB) and ma == mb:
                return True

    return False

def satisfies(values, operation, target):

    for p in permutations(values):
        if reduce(operation, p) == target:
            return True

    return False

def gdomains(size, cliques):

    domains = {}
    for clique in cliques:
        members, operator, target = clique

        domains[members] = list(product(range(1, size + 1), repeat=len(members)))

        qualifies = lambda values: not conflicting(members, values, members, values) and \
                                   satisfies(values, operation(operator), target)

        domains[members] = list(filter(qualifies, domains[members]))

    return domains

def gneighbors(cliques):

    neighbors = {}
    for members, _, _ in cliques:
        neighbors[members] = []

    for A, _, _ in cliques:
        for B, _, _ in cliques:
            if A != B and B not in neighbors[A]:
                if conflicting(A, [-1] * len(A), B, [-1] * len(B)):
                    neighbors[A].append(B)
                    neighbors[B].append(A)

    return neighbors