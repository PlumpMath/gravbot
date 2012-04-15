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

worldsize = Point2(20,20)

class World():
    CULLDISTANCE = 10
    def __init__(self, size):
        utilities.app.accept('bullet-contact-added', self.onContactAdded) 
        utilities.app.accept('bullet-contact-destroyed', self.onContactDestroyed) 
        self.bw = BulletWorld()
        self.bw.setGravity(0,0,0)
        self.size = size
        self.perlin = PerlinNoise2()

        self.player = Player(self)
        self.player.initialise()

        self.entities = list()
        self.bgs = list()
        self.makeChunk(Point2(0,0)) 

	self.culls = 0

    def update(self, timer):
        dt = globalClock.getDt()
        self.bw.doPhysics(dt)

        self.player.update(dt)

        for entity in self.entities:
            entity.update(dt)

    # Generate a $worldsize chunk of data with bottom left corner at $pos
    def makeChunk(self, pos):
        # store enemies, bits of terrain and projectiles in entities
        # so we can do some collision detection
        self.bgs.append(utilities.loadObject("stars", depth=100, scaleX=200, scaleY=200.0, pos=Point2(pos.x*worldsize.x,pos.y*worldsize.y)))

        for i in range(-10, 10):
            self.entities.append(Rail(self, i * 10, 0))
    
        self.pt = list()

        for i in range(0, int(worldsize.x)):
            self.pt.append(list())
            for j in range(0, int(worldsize.y)):
                if self.perlin.noise(i,j) > 0:
                    self.pt[i].append(1)
                else:
                    self.pt[i].append(0)  

	self.wgs = list()
	self.searchForWalls(self.pt)
	self.testgroups = list()

	for wg in self.wgs:
	  self.testgroups.append(WallGroup(self, Point2(0,0), wg))
	
    def searchForWalls(self, pt):
        for i in range(0, int(worldsize.x)):
            for j in range(0, int(worldsize.y)):
	        if self.pt[i][j] == 1:
		  points = list()
		  self.wgs.append(points)
		  self.makeWallGroup(self.pt, Pix(i,j), points)

    def makeWallGroup(self, pt, point, points):
        i = point.x
	j = point.y
	if self.pt[i][j] == 1:
	    self.pt[i][j] = 0
	    points.append(Pix(i,j))
	else: 
	    return    
        if i > 0:
	    self.makeWallGroup(self.pt, Pix(i-1,j), points)
        if i < worldsize.x-1:  
	    self.makeWallGroup(self.pt, Pix(i+1,j), points)
 	if j < worldsize.y-1:
	    self.makeWallGroup(self.pt, Pix(i,j+1), points)
	if j > 0:
	    self.makeWallGroup(self.pt, Pix(i,j-1), points)

    def printpt(self):
	astr = ""
        for i in range(0, int(worldsize.x)):
	    tstr = ""
            for j in range(0, int(worldsize.y)):
	        tstr = tstr +  str(self.pt[j][i]) + " "
	    astr = tstr + '\n' + astr
	print astr    
    
    def addEntity(self, entity):
        self.entities.append(entity)

    def onContactAdded(self, node1, node2):
	return

    def onContactDestroyed(self, node1, node2):
	return

class Rail(Entity):
    def __init__(self, world, posX, posY):
        super(Rail, self).__init__()
        self.obj = utilities.loadObject("rail", depth=20, scaleX=10.0, scaleY=1.0, pos=Point2(posX,posY))

    def update(self, timer):
        """
        Rails don't do much
        """
        return

def distance(p1, p2):
    return hypot(p1.x-p2.x, p1.y - p2.y) 

class Wall(Entity):
    def __init__(self, world, posX, posY, group, tile):
        super(Wall, self).__init__()

	self.x = posX
	self.y = posY

        self.health = 100
	self.world = world

	self.obj = utilities.loadObject(tile, depth=0, pos = Point2(posX, posY))
	self.obj.reparentTo(group.np)

	self.shape = BulletBoxShape(Vec3(0.5, 1.0, 0.5))
	group.bnode.addShape(self.shape, TransformState.makePos(Point3(posX, 0, posY)))


# Probably want to convert the list of points to a graph to support
# cutting an object into two pieces
class WallGroup(Entity):
    wallmass = 500.0
    def __init__(self, world, pos, wallpoints):
        super(WallGroup, self).__init__()

	self.mass = len(wallpoints)*WallGroup.wallmass
	# want to narrow this down to minimum set
	self.hullpoints = list()

	self.walls = list()
        self.bnode = BulletRigidBodyNode()

        self.bnode.setMass(len(wallpoints))
	self.bnode.setAngularFactor(Vec3(0,1,0))
        self.np = utilities.app.render.attachNewNode(self.bnode)
        self.np.setPos(wallpoints[0].x,20,wallpoints[0].y)

        for p in wallpoints:
            tile = "wall"
	    if randint(0, 10) < 8:
	        tile = "floor1"
	    else:
	        tile = "floor2"
	    self.walls.append(Wall(world, p.x, p.y, self, tile))

	world.bw.attachRigidBody(self.bnode)

    def update(self, timer):
	d = distance(self.pos, self.world.player.location)
	if d > World.CULLDISTANCE and self.inScope:
	    self.obj.hide()
	    self.world.bw.removeRigidBody(self.bnode)
	    self.inScope = False
	if d < World.CULLDISTANCE and not self.inScope:    
	    self.obj.show()    
	    self.world.bw.attachRigidBody(self.bnode)
	    self.inScope = True
        if self.health < 0:
            self.obj.remove()
class Pix():
    def __init__(self, x, y):
        self.x = int(x)
        self.y = int(y)
    def __repr__(self):
        return "(" + str(self.x) + "," + str(self.y) + ")"
    
