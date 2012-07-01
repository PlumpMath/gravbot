# basic pathfinding

from panda3d.core import Mat4, Point3, Vec3, Point2
from panda3d.bullet import BulletBodyNode
from chunks import Chunk
from math import hypot
from heapq import heappop, heappush

# Build a voxel based representation
# For the next n steps with delta d
def buildMap(collidableEntities, offset=None, steps=1, delta=1.0):
    if (offset == None):
        offset = Point2(0, 0)

    cmap = [[0 for i in range(40)] for j in range(40)]
    for entity in collidableEntities:
        if (isinstance(entity, Chunk)):
            pos = entity.np.getPos()
            tfm = entity.np.getMat()
            for i in range(entity.bnode.getNumShapes()):
                stfm = entity.bnode.getShapeMat(i)
                spos = entity.bnode.getShapePos(i)
                stfm = tfm * stfm
                tfp = stfm.xformPoint(spos)
                tfp -= spos
                # might be out of range    
                try:     
                    cmap[int(tfp.z-offset.y)][int(tfp.x-offset.x)] = 1
                except:
                    pass
    return cmap

def findPath(location, target, cmap, size = 1.0):
    start = 0 
    goal = 0
    if isinstance(location, Point3):
        start = P2(int(location.x), int(location.z))
    if isinstance(location, Point2):    
        start = P2(int(location.x), int(location.y))

    if isinstance(target, Point3):
        goal = P2(int(target.x), int(target.z))
    if isinstance(target, Point2):    
        goal = P2(int(target.x), int(target.y))

    # with apologies to Stack Overflow
    # http://stackoverflow.com/questions/4159331/python-speed-up-an-a-star-pathfinding-algorithm
    open_set = set()
    open_heap = []
    closed_set = set()
    
    def retracePath(current):
        path = [Point2(current.x, current.y)]
        while current.parent is not None:
            current = current.parent
            path.append(Point2(current.x, current.y))
        path.reverse()
        return path

    open_set.add(start)
    open_heap.append((0,start))

    while open_set:
        current = heappop(open_heap)[1]
        if current == goal:
            return retracePath(current)
        open_set.remove(current)
        closed_set.add(current)
        for tile in neighbor_list(current, cmap):
            if tile not in closed_set:
                tile.h = (abs(goal.x-tile.x)+abs(goal.y-tile.y))*10
                if tile not in open_set:
                    open_set.add(tile)
                    heappush(open_heap, (tile.h, tile))
                tile.parent = current
    return []            

def cost(point, goal):
    return math.hypot(point.x - goal.x, point.y - goal.y)

# Includes the diagonals    
def neighbor_list(p, cmap):
    nlist = list()

    if p.x < len(cmap)-1:
        if cmap[p.x+1][p.y] == 0:
            nlist.append(P2(p.x+1, p.y))
        if p.y < len(cmap[0])-1:
            if cmap[p.x+1][p.y+1] == 0:
                nlist.append(P2(p.x+1 ,p.y+1))
        if p.y > 0:
            if cmap[p.x+1][p.y-1] == 0:
                nlist.append(P2(p.x+1 ,p.y-1))

    if p.x > 0:
        if cmap[p.x-1][p.y] == 0:
            nlist.append(P2(p.x-1, p.y))
        if p.y < len(cmap[0])-1:
            if cmap[p.x-1][p.y+1] == 0:
                nlist.append(P2(p.x-1, p.y+1))
        if p.y > 0:
            if cmap[p.x-1][p.y-1] == 0:
                nlist.append(P2(p.x-1, p.y-1))

    if p.y > 0:
        if cmap[p.x][p.y-1] == 0:
            nlist.append(P2(p.x, p.y-1))
    if p.y < len(cmap[0]) - 1:
        if cmap[p.x][p.y+1] == 0:
            nlist.append(P2(p.x, p.y+1))

    return nlist    


class P2():
    def __init__(self, x, y, parent=None, h=0):
        self.x = x
        self.y = y
        self.h = h
        self.parent = parent

    def __eq__(self, other):
        if self.x == other.x and self.y == other.y:
            return True
        else:
            return False    

    def __hash__(self):
        return hash((self.x, self.y)) 

    def __repr__(self):
        return "[" + str(self.x) + "," + str(self.y) + "]"

def printMap(cmap):
    s = ""
    for i in range(20):
        line = ""
        for j in range(20):
            line = line + str(cmap[i][j])
        s = line + '\n' + s
    print s



