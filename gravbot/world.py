# World is an ordered list of chunks.
# current chunk is where the current player is
# simulate the current, previous and next chunks

from entity import Entity
from panda3d.core import Point2, Point3, BoundingBox, BoundingSphere, Vec3
from panda3d.core import PerlinNoise2
from player import Player
from panda3d.bullet import BulletWorld
from panda3d.bullet import BulletPlaneShape
from panda3d.bullet import BulletBoxShape
from panda3d.bullet import BulletConvexHullShape 
from panda3d.bullet import BulletRigidBodyNode

from math import hypot 
import utilities

worldsize = Point2(10,10)

class World():
    CULLDISTANCE = 10
    def __init__(self, size):
        self.bw = BulletWorld()
        self.bw.setGravity(0,0,-9.8)
        self.size = size
        self.perlin = PerlinNoise2()

        self.player = Player(self)
        self.player.initialise()

        self.entities = list()
        self.bgs = list()
        self.makeChunk(Point2(0,0)) 

        # the lower rail
        shape = BulletPlaneShape(Vec3(0, 0, 1), 1)
        self.groundNode = BulletRigidBodyNode('Ground')
        self.groundNode.addShape(shape)
        self.groundnp = render.attachNewNode(self.groundNode)
        self.groundnp.setPos(0, 0, 0)
        self.bw.attachRigidBody(self.groundNode)

	self.culls = 0

	self.chtest = BulletConvexHullShape()
	h = 0.5

	self.chtest.addArray([
	    Point3(h,h,h),
	    Point3(-h,h,h),
	    Point3(h,-h,h),
	    Point3(-h,-h,h),
	    Point3(h,h,-h),
	    Point3(-h,h,-h),
	    Point3(h,-h,-h),
	    Point3(-h,-h,-h),
	    ])
	self.chbn = BulletRigidBodyNode()    
        self.chbn.addShape(self.chtest)
	self.chnp = render.attachNewNode(self.chbn)
	self.chnp.setPos(0,20,30)
	self.bw.attachRigidBody(self.chbn)

    def update(self, timer):
        dt = globalClock.getDt()
        self.bw.doPhysics(dt)

        self.player.update(timer)

        for entity in self.entities:
            entity.update(timer)

    # Generate a $worldsize chunk of data with bottom left corner at $pos
    def makeChunk(self, pos):
        # store enemies, bits of terrain and projectiles in entities
        # so we can do some collision detection
        self.bgs.append(utilities.loadObject("stars", depth=100, scaleX=200, scaleY=200.0, pos=Point2(pos.x*worldsize.x,pos.y*worldsize.y)))
        # also need to put these around any other "edge" nodes
        #self.bgs.append(utilities.loadObject("stars", depth=100, scaleX=200, scaleY=200.0, pos=Point2(pos.x*-200,0)))

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

        #pt[0][0] = 0	
        #pt[1][0] = 0	
        #pt[0][1] = 0	
        #pt[1][1] = 0	
        #pt[2][2] = 0
        #pt[2][1] = 0
        #pt[1][2] = 0
        #pt[2][2] = 0 

        for i in range(2, int(worldsize.x)):
            for j in range(2, int(worldsize.y)):
                if self.pt[i][j] == 1:
		    pass
                    #self.entities.append(Wall(self, Point2(i,j)))

        self.printpt()
	self.wgs = list()
	self.searchForWalls(self.pt)

	for wallblock in self.wgs:
	    print "block"
	    for block in wallblock:
	        print block
                self.entities.append(Wall(self, Point2(block.x+5,block.y+5)))

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
    def __init__(self, world, pos, grouped = False):
        super(Wall, self).__init__()
        self.health = 100
	self.world = world

	if not grouped:
            shape = BulletBoxShape(Vec3(0.5,2.0,0.5))
            self.bnode = BulletRigidBodyNode()
            self.bnode.addShape(shape)
            self.np = utilities.app.render.attachNewNode(self.bnode)
            self.np.setPos(pos.x,20,pos.y)
            #world.bw.attachRigidBody(self.bnode)

            self.obj = utilities.loadObject("wall", depth = 0)
            self.obj.reparentTo(self.np)
            self.obj.setScale(1)
	    self.obj.hide()

	    #for storing state if we are far from the camera
	    self.inScope = False
	    self.hpr = Point3(0,0,0) 
	    self.pos = pos 
	else:
	    return
	    

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

# Probably want to convert the list of points to a graph to support
# cutting an object into two pieces
class WallGroup(Entity):
    def __init__(self, world, pos, wallpoints):
        super(WallGroup, self).__init__()

	self.mass = len(wallpoints)
	# TODO  want to narrow this down to minimum set
	self.hullpoints = list()

        # the starting wall has all vertices
	# subsequent ones will just add another face
	self.hullpoints.append(Point3(0.5, 0.5, 0.5))
	self.hullpoints.append(Point3(0.5, 0.5, -0.5))
	self.hullpoints.append(Point3(-0.5, 0.5, 0.5))
	self.hullpoints.append(Point3(-0.5, 0.5, -0.5))

	self.hullpoints.append(Point3(0.5, -0.5, 0.5))
	self.hullpoints.append(Point3(0.5, -0.5, -0.5))
	self.hullpoints.append(Point3(-0.5, -0.5, 0.5))
	self.hullpoints.append(Point3(-0.5, -0.5, -0.5))
	#self.walls.append(Wall())
	self.walls = list()

        self.prevwall = wallpoints[0]
	self.prevwall.x -= pos.x
	self.prevwall.y -= pos.z
	for wall in wallpoints[1:]:
	    # set the wall positions relative to the first node
	    # this shouldn't really be a problem even if the first node disappears
	    # though it does mean we need to be careful about getting the NodePath
	    # position because it's essentially meaningless
	    wall.x -= pos.x
	    wall.y -= pos.z

            xmod = 0
	    ymod = 0
	    # figure out which direction we're heading in

	    self.hullpoints.append(wall.x, 0, wall.y)
	    self.hullpoints.append(wall.x, 0, wall.y)
	    self.hullpoints.append(wall.x, 0, wall.y)
	    self.hullpoints.append(wall.x, 0, wall.y)

	    self.prevwall = wall
	    #self.walls.append(Wall())
	  
        shape = BulletConvexHullShape()

        for p in self.hullpoints:
	    shape.addPoint(p)

        self.bnode = BulletRigidBodyNode()
        self.bnode.addShape(shape)
        self.np = utilities.app.render.attachNewNode(self.bnode)
        self.np.setPos(pos.x,20,pos.y)



class Pix():
    def __init__(self, x, y):
        self.x = int(x)
        self.y = int(y)
    def __repr__(self):
        return "(" + str(self.x) + "," + str(self.y) + ")"
    
