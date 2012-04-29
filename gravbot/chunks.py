# World is an ordered list of chunks.
# current chunk is where the current player is
# simulate the current, previous and next chunks

from entity import Entity
from panda3d.core import Point2, Point3, Vec3, NodePath
from panda3d.core import TransformState
from player import Player
from panda3d.bullet import BulletWorld
from panda3d.bullet import BulletBoxShape
from panda3d.bullet import BulletRigidBodyNode

import utilities
from items import Flame
from copy import copy
from utilities import Pix

def compareBlock(block1, block2):
    x = block1.pos.x - block2.pos.x
    if x != 0:
        return int(x)
    y = block1.pos.y - block2.pos.y
    if y != 0: 
        return int(y)
    #bad
    print "bad"
    return 0

class Block(Entity):
    def __init__(self, world, pos, tile, edges, shape=BulletBoxShape(Vec3(0.5, 1.0, 0.5))):
        super(Block, self).__init__()

        self.health = 100
	self.world = world
	self.edges = edges
	self.pos = pos
	self.obj = utilities.loadObject(tile, depth=0, pos = self.pos)
	self.shape = shape 

    def destroy(self):
        self.obj.hide()
        self.obj.remove()
    
    def hitby(self, projectile):
        self.health -= projectile.damage 
        if (self.health < 0):
            return True
        greyscale  = 0.3 + (0.01 * self.health)
        self.obj.setColor(greyscale, greyscale,greyscale,greyscale)
        return False

    def rebuild(self, chunk, diff=Point2(0.0, 0.0)):
        self.pos -= diff
	self.chunk = chunk
        self.chunk.bnode.addShape(self.shape, TransformState.makePos(Point3(self.pos.x, 0, self.pos.y)))
	self.obj.reparentTo(self.chunk.np)
	self.obj.setPos(self.pos.x, 0, self.pos.y)

    def __repr__(self):
        return "(" + str(self.pos.x) + ", " + str(self.pos.y) + ")"

    def __eq__(self, other):
        if isinstance(other, int):
	    return False
        return self.pos.x == other.pos.x and self.pos.y == other.pos.y and self.chunk == other.chunk


class Chunk(Entity):
    chunkmass = 5.0
    def __init__(self, world, blocks, pos, hpr=Point3(0,0,0), diff = Vec3(0,0,0)):
        super(Chunk, self).__init__()

	self.mass = len(blocks)*Chunk.chunkmass
	self.world = world
	self.blocks = blocks

        self.bnode = BulletRigidBodyNode()

        self.bnode.setMass(self.mass)
	self.bnode.setAngularFactor(Vec3(0,1,0))
        self.np = utilities.app.render.attachNewNode(self.bnode)
        self.np.setPos(pos.x,20,pos.y)
	self.np.setHpr(hpr)
	self.np.setPos(self.np, diff)

	self.bnode.setPythonTag("entity", self)

	self.inScope = False # culling not done yet

	# centre the blocks around the np and add their shapes in.
	self.minMax()
	cog = Point2((self.minX+self.maxX) / 2.0, (self.minY+self.maxY) / 2.0)
	for block in blocks:
	    block.rebuild(self, cog)

	world.bw.attachRigidBody(self.bnode)
	self.hitlist = dict()

    def update(self, timer):
	for index in self.hitlist:
            # returns true if the wall is destroyed by the hit
            if self.blocks[index].hitby(self.hitlist[index]):
	        self.blocks[index].destroy()
                self.rebuild(index)
	self.hitlist.clear()    

    # remove an element and rebuild
    def rebuild(self, index):
	deadblock = self.blocks[index]
	out = list()

	for block in self.blocks:
	    for edge in block.edges:
	        if edge == deadblock:
		    block.edges.remove(edge)

	for block in deadblock.edges:
	    chunk = list()
	    self.searchBlock(block, chunk, deadblock)
	    out.append(chunk)

	#out is a list of lists of populated blocks
	#remove duplicate chunks
        results = list()
	for chunk in out:
	    chunk.sort(compareBlock)
	    if not chunk in results and len(chunk) > 0:
	        results.append(chunk)
	
	for result in results:
	    self.minMax(result)
	    #diff = Point2((self.minX+self.maxX) / 2.0, (self.minY+self.maxY) / 2.0)
	    diff = Vec3((self.minX+self.maxX) / 2.0, 0, (self.minY+self.maxY) / 2.0)
	    p = self.np.getPos()
	    pos = Point2(p.x, p.z)
	    h = self.np.getHpr()
	    self.world.entities.append(Chunk(self.world, result, pos, h, diff))

        self.destroy()
	self.remove = True
	    
    def searchBlock(self, block, lst, deleted):
        if block in lst:
	    return
	else:
	    lst.append(block)
	    for newblock in block.edges:
	        self.searchBlock(newblock, lst, deleted)

    def minMax(self, blocks=None):
        if blocks == None:
	    blocks = self.blocks

        self.minX = blocks[0].pos.x
        self.minY = blocks[0].pos.y
        self.maxX = blocks[0].pos.x
        self.maxY = blocks[0].pos.y

        for point in blocks:
            self.minX = min(point.pos.x, self.minX)
            self.minY = min(point.pos.y, self.minY)
            self.maxX = max(point.pos.x, self.maxX)
            self.maxY = max(point.pos.y, self.maxY)

    def destroy(self):
        #for shape in self.bnode.getShapes():
        #    self.bnode.removeShape(shape)
        self.world.bw.removeRigidBody(self.bnode)
	    
        return

    def hitby(self, projectile, index):
        self.hitlist[index] = projectile

def printFlatMatrix(matrix, xbound, ybound):
    astr = ""
    for i in range(0, xbound):
        tstr = ""
        for j in range(0, ybound):
            tstr = tstr +  str(matrix[i*xbound+ j]) + " "
        astr = tstr + '\n' + astr
    print astr	
