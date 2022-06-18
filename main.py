import math
import random
from tqdm import tqdm
from sys import exit

THRESHOLD = 10**-10
N_POINTS = 3000000
N_ITERATIONS = 4

"""
Problem statement:
 - A point P is randomly generated within the equilateral triangle ABC
 - What is the probability that the area of triangle APB is greater than that of each triangle APC and triangle BPC
"""


class Fraction:
    def __init__(self, numerator, denominator):
        self.denominator = denominator
        self.numerator = numerator
        
        if denominator != 0:
            self.simplify()

    def simplify(self):
        a = self.denominator
        b = self.numerator
        gcd = math.gcd(a, b)
        self.denominator = a // gcd
        self.numerator = b // gcd

    def lcm(self, a, b):
        return math.fabs(a * b) // math.gcd(a, b)

    def divide(self, fraction):
        self.numerator = int(self.numerator * fraction.denominator)
        self.denominator = int(self.denominator * fraction.numerator)

        self.simplify()
    
    def add(self, fraction):
        if fraction.numerator == 0 or fraction.denominator == 0:
            return
        elif self.numerator == 0 or self.denominator == 0:
            self.numerator = fraction.numerator
            self.denominator = fraction.denominator
            return
            
        denominatorLcm = int(self.lcm(int(fraction.denominator), int(self.denominator)))
        newNominator = self.numerator * (denominatorLcm / self.denominator) + fraction.numerator * (denominatorLcm / fraction.denominator)

        self.numerator = int(newNominator)
        self.denominator = denominatorLcm

        self.simplify()

    def __str__(self, indent = 0):
        return f"{' ' * indent}Fraction: [{int(self.numerator)} / {int(self.denominator)}]\n{' ' * indent}Decimal Equivalent: {self.toDecimal()}"

    def toDecimal(self):
        return self.numerator / self.denominator


def decorateText(text, decorator):
    return f"{decorator}{text}{bcolors.ENDC}"


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def perpendicularDistance(line, point):
    if line.gradient == 0:
        return math.fabs(point[1] - line.getY(point[0]))

    # get change in y between the point and the point above and collinear with it at 90deg
    deltaY = math.fabs(line.getY(point[0]) - point[1])

    # get change in x between the point and the point horizontally aligned and collinear with it
    deltaX = math.fabs(line.getX(point[1]) - point[0])

    res = (deltaX * deltaY) / math.sqrt(deltaY**2 + deltaX**2)
    return res


def getAreaTriangle(b, h):
    return b * h / 2


class Line:
    def __init__(self, gradient=1, yIntercept=0):
        self.gradient = gradient
        self.yIntercept = yIntercept

    def __str__(self):
        return f"y = {self.gradient}x + {self.yIntercept}"

    def getY(self, x):
        return self.gradient * x + self.yIntercept

    def getX(self, y):
        return (y - self.yIntercept) / self.gradient

    def isAboveSlope(self, x, y, allowEqual=False):
        # if on the Line
        yBound = self.getY(x)
        if yBound == y:
            return allowEqual

        return yBound < y

    def isBelowSlope(self, x, y, allowEqual=False):
        # if on the Line
        yBound = self.getY(x)
        if yBound == y:
            return allowEqual

        return yBound > y


class MultiPointLine(Line):
    """
    p1 = tuple(x, y)
    p2 = tuple(x, y)
    """
    def __init__(self, p1, p2):
        gradient = (p1[1] - p2[1]) / (p1[0] - p2[0])
        y1 = p1[1]
        x1 = p1[0]

        yIntercept = y1 - gradient * x1

        Line.__init__(self, gradient, yIntercept)
        self.p1 = p1
        self.p2 = p2


class Triangle:
    def __init__(self, base, left, right):
        self.base = base
        self.left = left
        self.right = right

    def __str__(self):
        return f"""
Lines in triangle:
    base: {self.base}
    left side: {self.left}
    right side: {self.right}
"""


def generateRandomPoint(triangle):
    xBounds = [0, 3]
    yBounds = [0, 3]

    while True:
        x = random.uniform(xBounds[0], xBounds[1])
        y = random.uniform(yBounds[0], yBounds[1])

        if triangle.left.isBelowSlope(x, y) and triangle.right.isBelowSlope(
                x, y) and triangle.base.isAboveSlope(x, y):
            return (x, y)


def getTriangle():
    # generate lines
    leftLine = Line(math.sqrt(3), 0)
    baseLine = Line(0, 0)
    rightLine = Line(-math.sqrt(3), 3 * math.sqrt(3))

    triangle = Triangle(baseLine, leftLine, rightLine)
    return triangle


def findDup(points):
    seen = set({})

    for p in points:
        if p in seen:
            return p
        seen.add(p)
        return False


"""
Tests the statement: triangle ABD has a greater area than the other two triangles
"""


def testStatement(triangle, p):
    h1 = perpendicularDistance(triangle.base, p)
    h2 = perpendicularDistance(triangle.left, p)
    h3 = perpendicularDistance(triangle.right, p)

    trA = getAreaTriangle(3, h1)
    trB = getAreaTriangle(3, h2)
    trC = getAreaTriangle(3, h3)

    computedSum = trA + trB + trC

    triangleArea = (3**2 * math.sqrt(3) / 4)

    if math.fabs(computedSum - triangleArea) > THRESHOLD:
        exit("Error boundary for the computed areas is exceeded!")

    return trA > trB and trA > trC


def getProbability(triangle):
    points = []

    statementTrueCount = 0

    print(decorateText("Generating random points...", bcolors.BOLD))
    for _ in tqdm(range(N_POINTS)):
        randPoint = generateRandomPoint(triangle)
        points.append(randPoint)

    print(decorateText("No duplicates...", bcolors.BOLD))
    if findDup(points):
        print(
            decorateText("Found duplicates, exiting the process.",
                         bcolors.FAIL))
        return
    else:
        print(decorateText("Duplicate check passed.", bcolors.OKGREEN))

    print(decorateText("Computing probability...", bcolors.BOLD))
    for point in tqdm(points):
        if testStatement(triangle, point):
            statementTrueCount += 1

    return Fraction(statementTrueCount, N_POINTS)


def main():

    triangle = getTriangle()

    resultFractions = []

    for i in range(1, N_ITERATIONS + 1):
        print(decorateText(f"\nIteration #{i}", bcolors.HEADER))
        resultFractions.append(getProbability(triangle))
        print()

    average = Fraction(0, 0)
    for result in resultFractions:
        average.add(result)

    average.divide(Fraction(N_ITERATIONS, 1))

    print(f"Average probability from {N_ITERATIONS} iterations:\n  {average}")


if __name__ == "__main__":
    main()
