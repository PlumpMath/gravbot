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
from chunks import Wall, ChunkGroup

worldsize = Point2(3,3)

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
        self.makeChunk(Point2(0,0)) 

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

    # Generate a $worldsize chunk of data with bottom left corner at $pos
    def makeChunk(self, pos):
        # store enemies, bits of terrain and projectiles in entities
        # so we can do some collision detection
        self.bgs.append(utilities.loadObject("stars", depth=100, scaleX=200, scaleY=200.0, pos=Point2(pos.x*worldsize.x,pos.y*worldsize.y)))

        self.pt = list()

        for i in range(0, int(worldsize.x)):
            self.pt.append(list())
            for j in range(0, int(worldsize.y)):
                if self.perlin.noise(i,j) > 0:
                    self.pt[i].append(1)
                else:
                    self.pt[i].append(1) #TESTING  
                    #self.pt[i].append(0) #TESTING  

	self.wgs = list()
	self.searchForWalls(self.pt)

	for wg in self.wgs:
	  self.entities.append(ChunkGroup(self, wg, 1,1))
	
    def searchForWalls(self, pt):
        for i in range(0, int(worldsize.x)):
            for j in range(0, int(worldsize.y)):
	        if self.pt[i][j] == 1:
		  points = list()
		  self.wgs.append(points)
		  self.makeWallGroup(self.pt, utilities.Pix(i,j), points)

    def makeWallGroup(self, pt, point, points):
        i = point.x
	j = point.y
	if self.pt[i][j] == 1:
	    self.pt[i][j] = 0
	    points.append(utilities.Pix(i,j))
	else: 
	    return    
        if i > 0:
	    self.makeWallGroup(self.pt, utilities.Pix(i-1,j), points)
        if i < worldsize.x-1:  
	    self.makeWallGroup(self.pt, utilities.Pix(i+1,j), points)
 	if j < worldsize.y-1:
	    self.makeWallGroup(self.pt, utilities.Pix(i,j+1), points)
	if j > 0:
	    self.makeWallGroup(self.pt, utilities.Pix(i,j-1), points)

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
