from entity import Entity
from panda3d.core import Point2, Point3, NodePath, BoundingBox, Vec3, BitMask32
from items import Blowtorch, LightLaser, Grenade
from math import atan2, degrees, sin
import utilities

from panda3d.bullet import BulletBoxShape, BulletRigidBodyNode

class Player(Entity):

    walkspeed = 5
    damping = 0.9
    topspeed = 15

    leftMove = False
    rightMove = False
    jumpToggle = False
    crouchToggle = False

    def __init__(self, world):
        super(Player, self).__init__()

        self.obj = utilities.loadObject("tdplayer", depth=20)

        self.world = world 
        self.health = 100
        self.inventory = list()

        self.depth = self.obj.getPos().y

        self.location = Point2(10,0)
        self.velocity = Vec3(0)

        self.shape = BulletBoxShape(Vec3(0.3, 1.0, 0.49))
        self.bnode = BulletRigidBodyNode('Box')
        self.bnode.setMass(0.1)
        self.bnode.setAngularVelocity(Vec3(0))
        self.bnode.setAngularFactor(Vec3(0))
        self.bnode.addShape(self.shape)
        self.bnode.setLinearDamping(0.95)
        self.bnode.setLinearSleepThreshold(0)

        world.bw.attachRigidBody(self.bnode)
        self.bnode.setPythonTag("entity", self)
        self.bnode.setIntoCollideMask(BitMask32.bit(0))

        self.node = utilities.app.render.attachNewNode(self.bnode)
        self.node.setPos(self.obj.getPos())

        self.obj.setPos(0,0,0)
        self.obj.setScale(1)
        self.obj.reparentTo(self.node)
        self.node.setPos(self.location.x, self.depth, self.location.y)

    def initialise(self):
        self.inventory.append(LightLaser(self.world, self))
        self.inventory.append(Blowtorch(self.world, self))
        #self.inventory["Grenade"] = Grenade(self.world, self)

        for item in self.inventory:
            item.initialise()

        self.currentItemIndex = 1
        self.currentItem = self.inventory[self.currentItemIndex]
        self.currentItem.equip()

    def activate(self):
        self.currentItem.activate()

    def update(self, timer):
        self.velocity = self.bnode.getLinearVelocity()

        if (self.leftMove):
            self.bnode.applyCentralForce(Vec3(-Player.walkspeed,0,0))
        if (self.rightMove):
            self.bnode.applyCentralForce(Vec3(Player.walkspeed,0,0))
        if (self.jumpToggle):
            self.bnode.applyCentralForce(Vec3(0,0,Player.walkspeed))
        if (self.crouchToggle):
            self.bnode.applyCentralForce(Vec3(0,0,-Player.walkspeed))
        
        if (self.velocity.x < -self.topspeed):
            self.velocity.x = -self.topspeed
        if (self.velocity.x > self.topspeed):
            self.velocity.x = self.topspeed

        mouse = utilities.app.mousePos
        # extrude test
        near = Point3()
        far = Point3()
        utilities.app.camLens.extrude(mouse, near, far)
        camp = utilities.app.camera.getPos()
        near *= 20 # player depth

        if near.x != 0:
            angle = atan2(near.z + camp.z - self.node.getPos().z, near.x + camp.x - self.node.getPos().x)
            #angle = atan2(near.z, near.x)
        else:
            angle = 90  

        self.angle = angle

        # set current item to point at cursor   
        self.currentItem.update(timer)

        # move the camera so the player is centred horizontally,
        # but keep the camera steady vertically
        utilities.app.camera.setPos(self.node.getPos().x, 0, self.node.getPos().z)

        self.obj.setHpr(0, 0, -1 * degrees(angle))
        self.location.x = self.node.getPos().x
        self.location.y = self.node.getPos().z

    def moveLeft(self, switch):
        self.leftMove = switch 

    def moveRight(self, switch):
        self.rightMove = switch 

    def jump(self, switch):
        self.jumpToggle = switch

    def crouch(self, switch):
        self.crouchToggle = switch

    def scrollItem(self, number):
        self.currentItem.unequip()
        self.currentItemIndex = self.currentItemIndex + number
        if self.currentItemIndex < 0:
            self.currentItemIndex = len(self.inventory) - 1 
        if self.currentItemIndex > len(self.inventory) - 1:
            self.currentItemIndex = 0

        self.currentItem = self.inventory[self.currentItemIndex]
        self.currentItem.equip()

    def selectItem(self, number):
        if (number - 1 < len(self.inventory) and number - 1 >= 0):
            self.currentItem.unequip()
            self.currentItemIndex = number - 1
            self.currentItem = self.inventory[self.currentItemIndex]
            self.currentItem.equip()

    def hitby(self, projectile, index):
        self.health -= projectile.damage 
        if (self.health < 0):
            self.obj.setColor(1,0,0,1)
            return True
        greyscale  = 0.3 + (0.01 * self.health)
        self.obj.setColor(greyscale, greyscale,greyscale,greyscale)
        return False
