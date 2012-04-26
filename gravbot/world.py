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
from chunks import Block, Chunk

worldsize = Point2(200,200)

class World():
    CULLDISTANCE = 10
    def __init__(self, size):
        self.bw = BulletWorld()
        self.bw.setGravity(0,0,0)
        self.size = size
        self.perlin = PerlinNoise2()

	#utilities.app.accept('bullet-contact-added', self.onContactAdded) 
	#utilities.app.accept('bullet-contact-destroyed', self.onContactDestroyed) 

        self.player = Player(self)
        self.player.initialise()

        self.entities = list()
        self.bgs = list()
        self.makeChunk(Point2(0,0), Point2(3.0, 3.0)) 

	self.mps = list()

	self.culls = 0

    def update(self, timer):
        dt = globalClock.getDt()
        self.bw.doPhysics(dt, 5, 1.0/180.0)
        
        for entity in self.entities:
	    if isinstance(entity, Flame):
	        ctest = self.bw.contactTest(entity.bnode)
		if ctest.getNumContacts() > 0:
	            entity.remove = True
	 	    mp =  ctest.getContacts()[0].getManifoldPoint()
		    ctest.getContacts()[0].getNode0().getPythonTag("entity").hitby(Flame, mp.getIndex0())

	for entity in self.entities:
	    if entity.remove == True:
	        entity.destroy()
		self.entities.remove(entity)

        self.player.update(dt)

        for entity in self.entities:
            entity.update(dt)

    def makeChunk(self, pos, size):
        self.bgs.append(utilities.loadObject("stars", depth=100, scaleX=200, scaleY=200.0, pos=Point2(pos.x*worldsize.x,pos.y*worldsize.y)))

	blocks = list()
        #world, pos, tile, edges
	blocks.append(Block(self, Point2(-0.5, -0.5), "floor1", list()))
	blocks.append(Block(self, Point2(0.5, -0.5), "floor1", list()))
	blocks.append(Block(self, Point2(1.5, -0.5), "floor1", list()))
	blocks.append(Block(self, Point2(2.5, -0.5), "floor1", list()))

	blocks[0].edges.append(blocks[1])
	blocks[1].edges.append(blocks[0])

	blocks[2].edges.append(blocks[1])
	blocks[1].edges.append(blocks[2])

	blocks[2].edges.append(blocks[3])
	blocks[3].edges.append(blocks[2])

	chunk = Chunk(self, blocks, Point2(2,2))
	self.addEntity(chunk)


    def addEntity(self, entity):
        self.entities.append(entity)

    def onContactAdded(self, node1, node2):
        e1 = node1.getPythonTag("entity")
        e2 = node2.getPythonTag("entity")

	if isinstance(e1, Flame):
	    e1.remove = True
	if isinstance(e2, Flame):
	    e2.remove = True


        print "contact"
	
    def onContactDestroyed(self, node1, node2):
        return

def distance(p1, p2):
    return hypot(p1.x-p2.x, p1.y - p2.y) 

def printMatrix(matrix):
    astr = ""
    for i in range(0, len(matrix)):
        tstr = ""
        for j in range(0, len(matrix[0])):
            tstr = tstr +  str(matrix[i][j]) + " "
        astr = tstr + '\n' + astr
    print astr    
