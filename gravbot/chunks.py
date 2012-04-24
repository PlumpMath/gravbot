# World is an ordered list of chunks.
# current chunk is where the current player is
# simulate the current, previous and next chunks

from entity import Entity
from panda3d.core import Point2, Point3, BoundingBox, BoundingSphere, Vec3
from panda3d.core import PerlinNoise2
from panda3d.core import TransformState
from player import Player
from panda3d.bullet import BulletWorld
from panda3d.bullet import BulletPlaneShape
from panda3d.bullet import BulletBoxShape
from panda3d.bullet import BulletConvexHullShape 
from panda3d.bullet import BulletRigidBodyNode

from math import hypot 
import utilities
from random import randint
from items import Flame
from copy import copy
from utilities import Pix

class Wall(Entity):
    def __init__(self, world, posX, posY, group, tile):
        super(Wall, self).__init__()

        self.health = 100
	self.world = world

	self.posX = posX
	self.posY = posY

	self.obj = utilities.loadObject(tile, depth=0, pos = Point2(posX - group.cog.x, posY - group.cog.y))
	self.obj.reparentTo(group.np)
	self.obj.hide()

	self.shape = BulletBoxShape(Vec3(0.5, 1.0, 0.5))
	self.group = group
	group.bnode.addShape(self.shape, TransformState.makePos(Point3(posX - group.cog.x, 0, posY - group.cog.y)))

    def destroy(self):
        self.obj.remove()
    
    def hitby(self, projectile):
        self.health -= projectile.damage 
        if (self.health < 0):
            return True
        greyscale  = 0.3 + (0.01 * self.health)
        self.obj.setColor(greyscale, greyscale,greyscale,greyscale)
        return False

    def rebuild(self, diffX, diffY):
        self.group.bnode.addShape(self.shape, TransformState.makePos(Point3(self.posX - diffX - self.group.cog.x, 0, self.posY - diffY - self.group.cog.y)))
	self.obj.reparentTo(self.group.np)
	self.obj.setPos(self.posX - self.group.cog.x, 0, self.posY - self.group.cog.y)

    def __repr__(self):
        return "(" + str(self.x) + ", " + str(self.y) + ")"

    def __eq__(self, other):
        if isinstance(other, int):
	    return False
        return self.x == other.x and self.y == other.y


# Probably want to convert the list of points to a graph to support
# cutting an object into two pieces
# Except we need the flat list so that the bullet manifold point
# gives an index that can actually be used without jumping through hoops!

#cog args are the world position of the nodepath and
# take no notice of the size of the object
class ChunkGroup(Entity):
    chunkmass = 500.0
    def __init__(self, world, wallpoints, posX=0.0, posY=0.0, walls=None):
        super(ChunkGroup, self).__init__()

	self.mass = len(wallpoints)*ChunkGroup.chunkmass
	self.wallpoints = wallpoints
	self.world = world

	self.minMax()

	self.cog = Point2((self.minX+self.maxX) / 2.0, (self.minY+self.maxY) / 2.0)
	    
	self.walls = list()
        self.bnode = BulletRigidBodyNode()

        self.bnode.setMass(len(wallpoints))
	self.bnode.setAngularFactor(Vec3(0,1,0))
        self.np = utilities.app.render.attachNewNode(self.bnode)
        self.np.setPos(posX,20,posY)

	self.bnode.setPythonTag("entity", self)

	self.inScope = False # culling

	# if no walls supplied, this must be new
	# so generate some walls
        if walls == None:
	    self.walls = list()
            for p in wallpoints:
	        # remove offsets inherited from my earlier stupidity
	        p.x -= self.minX
		p.y -= self.minY

                tile = "wall"
	        if randint(0, 10) < 8:
	            tile = "floor1"
	        else:
	            tile = "floor2"
	        self.walls.append(Wall(world, p.x, p.y, self, tile))
	else:
	    self.walls = walls # BYO walls
	    for wall in self.walls:
	        wall.group = self

	# requires walls    
	self.buildMatrix()

	world.bw.attachRigidBody(self.bnode)
	self.hitlist = dict()

    def update(self, timer):

	for index in self.hitlist:
            # returns true if the wall is destroyed by the hit
            if self.walls[index].hitby(self.hitlist[index]):
                self.rebuild(index)

	self.hitlist.clear()    

    # remove an element and rebuild
    def rebuild(self, index):
        for shape in self.bnode.getShapes():
            self.bnode.removeShape(shape)

        self.minMax()
	px = self.wallpoints[index].x - self.minX
	py = self.wallpoints[index].y - self.minY

	# Get the objects' spatial locations
	# so when we get split we can divvy up the 
	# instances of walls / other things that might have
	# state such as damage
        self.buildMatrix()

	# Remove the denoted wall from the matrix
	# then search for new wallgroups
	# (0 - 4 depending on circumstance)
	newMatrices = self.dfs(int(px), int(py))

        # remove the dead wall from the group
        self.walls[index].destroy()
        self.walls.pop(index)
        self.wallpoints.pop(index)

	if len(newMatrices) > 1:    
	    for matrix in newMatrices:
	        self.makeGroupFromMatrix(matrix, Point2(self.np.getPos().x, self.np.getPos().z), self.np.getHpr(self.np))
            for shape in self.bnode.getShapes():
                self.bnode.removeShape(shape)
            self.world.bw.removeRigidBody(self.bnode)
            self.remove = True
	    return

        # if the last block is removed delete the
	# bullet node
        if len(self.walls) == 0:
            for shape in self.bnode.getShapes():
                self.bnode.removeShape(shape)
            self.world.bw.removeRigidBody(self.bnode)
            self.remove = True
            return

        print "do we ever get here?"
        self.minMax()
        newcog = Point2((self.minX+self.maxX) / 2.0, (self.minY+self.maxY) / 2.0)

        # The amount we need to shift every shape to compensate
        # for moving our centre of gravity
        diff = newcog - self.cog
        self.cog = newcog

        # add back in all the walls
        for wall in self.walls:
            wall.rebuild(diff.x, diff.y)

        self.np.setPos(self.np, diff.x, 0, diff.y)

    def minMax(self):
        self.minX = self.wallpoints[0].x
        self.minY = self.wallpoints[0].y
        self.maxX = self.wallpoints[0].x
        self.maxY = self.wallpoints[0].y

        for point in self.wallpoints:
            self.minX = min(point.x, self.minX)
            self.minY = min(point.y, self.minY)
            self.maxX = max(point.x, self.maxX)
            self.maxY = max(point.y, self.maxY)


    # Creates a 2D representation from the list
    # of wall points
    def buildMatrix(self):
	self.matrix = [[0 for row in range(self.maxX - self.minX + 1)] for col in range(self.maxY - self.minY + 1)]

	for i in range (0, len(self.wallpoints)):
	    self.matrix[self.wallpoints[i].y - self.minY][self.wallpoints[i].x - self.minX] = self.walls[i] 

    # Subtract one element and search, beginning with the 4 surrounding squares
    # to determine if the solid has been split
    def dfs(self, j, i):
        self.matrix[i][j] = int(0)

        groups = list()
	self.xbound = len(self.matrix)
	self.ybound = len(self.matrix[0])

        if i > 0:
            wmatrix = [[0 for e in row] for row in self.matrix]
            self.mkgrp(wmatrix, i-1,j)
            groups.append(wmatrix)
        if i < self.xbound-1:
            ematrix = [[0 for e in row] for row in self.matrix]
            self.mkgrp(ematrix, i+1,j)
            groups.append(ematrix)
        if j < self.ybound-1:
            nmatrix = [[0 for e in row] for row in self.matrix]
            self.mkgrp(nmatrix, i,j+1)
            groups.append(nmatrix)
        if j > 0:
            smatrix = [[0 for e in row] for row in self.matrix]
            self.mkgrp(smatrix, i,j-1)
            groups.append(smatrix)

        if len(groups) == 0:
            return
        else:
            # there is trouble afoot
	    flattened = [[x for sublist in g for x in sublist] for g in groups]
	    uniques = list()

	    for flat in flattened:
	        #if sum(flat) != 0:
		if flat not in uniques:
		    uniques.append(flat)
	    return uniques		

    # search a given matrix and generate a new one
    def mkgrp(self, matrix, i, j):
        # is there a block here?
        if self.matrix[i][j] == 0:
	    return # nope so go away
	# yes, have we already counted it?    
	if matrix[i][j] != 0:
	    return
	matrix[i][j] = self.matrix[i][j] # Now it's counted

	# Scan the area for hostiles.
        if i > 0:
            self.mkgrp(matrix, i-1,j)
        if i < self.xbound-1:
            self.mkgrp(matrix, i+1,j)
        if j < self.ybound-1:
            self.mkgrp(matrix, i,j+1)
        if j > 0:
            self.mkgrp(matrix, i,j-1)

    def destroy(self):
        for shape in self.bnode.getShapes():
            self.bnode.removeShape(shape)
        self.world.bw.removeRigidBody(self.bnode)
	    
        return

    def hitby(self, projectile, index):
        self.hitlist[index] = projectile


    def makeGroupFromMatrix(self, matrix, cog, hpr):
        wallpoints = list()
	walls = list()
	for wall in matrix:
	    if wall != 0:
	        wallpoints.append(Point2(wall.posX, wall.posY))
	        walls.append(wall)
	if len(wallpoints) == 0:
	    return
	wg = ChunkGroup(self.world, wallpoints, cog.x, cog.y, walls)

        for shape in wg.bnode.getShapes():
            wg.bnode.removeShape(shape)
	
	for wall in wg.walls:
	    wall.rebuild(0, 0)

	wg.minMax()    
        newcog = Point2((wg.minX+wg.maxX) / 2.0, (wg.minY+wg.maxY) / 2.0)
	diff = newcog - self.cog
	print "old np: " + str(self.np.getPos())
	print "new np: " + str(wg.np.getPos())
	print "new wg cog: " + str(newcog)
	print "old wg cog: " + str(self.cog)
	print "X: " + str(wg.maxX) + " " + str(wg.minX)
	print "Y: " + str(wg.maxY) + " " + str(wg.minY)
	self.world.addEntity(wg)    

    	
def printFlatMatrix(matrix, xbound, ybound):
    astr = ""
    for i in range(0, xbound):
        tstr = ""
        for j in range(0, ybound):
            tstr = tstr +  str(matrix[i*xbound+ j]) + " "
        astr = tstr + '\n' + astr
    print astr	
