# make some homies

import utilities
from panda3d.core import Point2, Vec3, BitMask32
from entity import Entity
from path import findPath
from panda3d.bullet import BulletBoxShape
from panda3d.bullet import BulletRigidBodyNode

class Enemy(Entity):
    def __init__(self, pos, hpr=Vec3(0,0,0)):
        super(Enemy, self).__init__()
        self.pos = pos

    def update(self, time):
        pass
        #move

    def destroy(self):
        self.obj.hide()
	self.obj.destroy()

# melee.
class Catcher(Enemy):
    def __init__(self, location, player, cmap, world):
        super(Catcher, self).__init__(location)
        self.player = player
        self.cmap = cmap

        self.obj = utilities.loadObject("robot", depth=20)

        self.world = world 
        self.health = 100

        self.depth = self.obj.getPos().y

        self.location = location 
        self.velocity = Vec3(0)

        self.shape = BulletBoxShape(Vec3(0.5, 1.0, 0.5))
        self.bnode = BulletRigidBodyNode('Box')
        self.bnode.setMass(0.1)
        self.bnode.setAngularVelocity(Vec3(0))
        self.bnode.setAngularFactor(Vec3(0))
        self.bnode.addShape(self.shape)
        self.bnode.setLinearDamping(0.75)
        self.bnode.setLinearSleepThreshold(0)

        world.bw.attachRigidBody(self.bnode)
        self.bnode.setPythonTag("Entity", self)
        self.bnode.setIntoCollideMask(BitMask32.bit(0))

        self.node = utilities.app.render.attachNewNode(self.bnode)
        self.node.setPos(self.obj.getPos())

        self.obj.setPos(0,0,0)
        self.obj.setScale(1)
        self.obj.reparentTo(self.node)
        self.node.setPos(self.location.x, self.depth, self.location.y)

    def update(self, time):
         self.location = Point2(self.node.getPos().x - self.player.location.x, self.node.getPos().z - self.player.location.y)

         if self.location.x > 20 or self.location.x < -20:
             return
         if self.location.y > 20 or self.location.y < -20:
             return
         #path = findPath(self.location, self.player.location, self.cmap)
         path = findPath(Point2(self.location + Point2(20,20)), Point2(20,20), self.world.cmap)
         if len(path) > 1:
            move = path[1] - self.location
            self.bnode.applyCentralForce(Vec3(move.x-20,0,move.y-20))

