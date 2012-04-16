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

worldsize = Point2(2,3)

class World():
    CULLDISTANCE = 10
    def __init__(self, size):
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
        self.bw.doPhysics(dt, 10, 1.0/180.0)

	for entity in self.entities:
	    if entity.remove == True:
	        entity.destroy()
		self.entities.remove(entity)

        for entity in self.entities:
	    if isinstance(entity, Flame):
	        ctest = self.bw.contactTest(entity.bnode)
		if ctest.getNumContacts() > 0:
	            entity.remove = True
		    for contact in ctest.getContacts():
			mp =  contact.getManifoldPoint()
			contact.getNode0().getPythonTag("entity").hitby("flame", mp.getIndex0())


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
	self.testgroups = list()

	for wg in self.wgs:
	  self.entities.append(WallGroup(self, wg))
	
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
	self.obj.hide()

	self.shape = BulletBoxShape(Vec3(0.5, 1.0, 0.5))
	self.group = group
	group.bnode.addShape(self.shape, TransformState.makePos(Point3(posX, 0, posY)))

    def destroy(self):
        self.obj.remove()

    def rebuild(self, diffX, diffY):
        self.group.bnode.addShape(self.shape, TransformState.makePos(Point3(self.x - diffX, 0, self.y - diffY)))
	self.x -= diffX
	self.y -= diffY

    def __repr__(self):
        return "(" + str(self.x) + ", " + str(self.y) + ")"


# Probably want to convert the list of points to a graph to support
# cutting an object into two pieces
class WallGroup(Entity):
    wallmass = 500.0
    def __init__(self, world, wallpoints):
        super(WallGroup, self).__init__()

	self.mass = len(wallpoints)*WallGroup.wallmass
	self.wallpoints = wallpoints

	# find approximate centre 
        self.minX = wallpoints[0].x
        self.minY = wallpoints[0].y
        self.maxX = wallpoints[0].x
        self.maxY = wallpoints[0].y

        for point in wallpoints:
	    self.minX = min(point.x, self.minX)
	    self.minY = min(point.y, self.minY)
	    self.maxX = max(point.x, self.maxX)
	    self.maxY = max(point.y, self.maxY)

	self.cog = Point2((self.minX+self.maxX) / 2.0, (self.minY+self.maxY) / 2.0)

	self.walls = list()
        self.bnode = BulletRigidBodyNode()

        self.bnode.setMass(len(wallpoints))
	self.bnode.setAngularFactor(Vec3(0,1,0))
        self.np = utilities.app.render.attachNewNode(self.bnode)
        self.np.setPos(self.cog.x,20,self.cog.y)

	self.bnode.setPythonTag("entity", self)


	self.inScope = False

        for p in wallpoints:
            tile = "wall"
	    if randint(0, 10) < 8:
	        tile = "floor1"
	    else:
	        tile = "floor2"
	    self.walls.append(Wall(world, p.x-self.cog.x, p.y-self.cog.y, self, tile))

	world.bw.attachRigidBody(self.bnode)
	self.bnode.notifyCollisions(True)

	self.hitlist = dict()

    def update(self, timer):

	for index in self.hitlist:
	    # remove all the shapes
	    for shape in self.bnode.getShapes():
	        self.bnode.removeShape(shape)
	    
	    # remove the heinous wall
	    self.walls[index].destroy()
            self.walls.pop(index)
	    self.wallpoints.pop(index)

            self.minX = self.wallpoints[0].x
            self.minY = self.wallpoints[0].y
            self.maxX = self.wallpoints[0].x
            self.maxY = self.wallpoints[0].y

            # refresh our centre of gravity
            for point in self.wallpoints:
	        self.minX = min(point.x, self.minX)
	        self.minY = min(point.y, self.minY)
	        self.maxX = max(point.x, self.maxX)
	        self.maxY = max(point.y, self.maxY)

	    newcog = Point2((self.minX+self.maxX) / 2.0, (self.minY+self.maxY) / 2.0)

	    # The amount we need to shift every shape to compensate
	    # for moving our centre of gravity

	    diff = newcog - self.cog
	    self.cog = newcog
	    print diff
	    
	    # add back in all the walls
	    for wall in self.walls:
	        #print str(wall.x) + " " + str(wall.y)
	        wall.rebuild(diff.x, diff.y)
	    cp = self.np.getPos()
	    print cp

	    self.np.setPos(self.np, diff.x, 0, diff.y)	
	    print self.np.getPos() 

	self.hitlist.clear()    

    def hitby(self, projectile, index):
        self.hitlist[index] = projectile

class Pix():
    def __init__(self, x, y):
        self.x = int(x)
        self.y = int(y)
    def __repr__(self):
        return "(" + str(self.x) + "," + str(self.y) + ")"
    
