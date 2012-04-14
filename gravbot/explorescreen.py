from gamescreen import GameScreen
from pausemenu import PauseMenu

from math import pi, sin, cos
from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from direct.actor.Actor import Actor
from direct.interval.IntervalGlobal import Sequence
from panda3d.core import Point3, Point2, Texture, NodePath, CollisionRay, Vec3

from panda3d.bullet import BulletWorld
from panda3d.bullet import BulletPlaneShape
from panda3d.bullet import BulletRigidBodyNode
from panda3d.bullet import BulletDebugNode


from entity import Entity
from player import Player
from world import World

import utilities
import sys

from pandac.PandaModules import loadPrcFileData 


class ExploreScreen(GameScreen):

    def __init__(self, app):

        GameScreen.__init__(self, app)

        utilities.setApp(self.app)

        self.world = World(10)

        self.app.taskMgr.add(self.update, "update")

        self.app.accept("a", self.world.player.moveLeft, [True])
        self.app.accept("a-up", self.world.player.moveLeft, [False])

        self.app.accept("d", self.world.player.moveRight, [True])
        self.app.accept("d-up", self.world.player.moveRight, [False])

        self.app.accept("w", self.world.player.jump, [True])
        self.app.accept("w-up", self.world.player.jump, [False])

        self.app.accept("s", self.world.player.crouch, [True])
        self.app.accept("s-up", self.world.player.crouch, [False])

        self.app.accept("mouse1", self.world.player.activate, [])

        self.app.accept("escape", sys.exit, [])

        self.app.accept("p", self.pause, []) 

        self.app.mousePos = Point2()
        self.app.disableMouse()

        self.app.rl = base.camLens.makeCopy()

        if utilities.debug:
          self.app.accept("h", self.showDBG, [True])
          self.app.accept("h-up", self.showDBG, [False])

          #bullet debug rendering 
          debugNode = BulletDebugNode('Debug')
          debugNode.showWireframe(True)
          debugNode.showConstraints(True)
          debugNode.showBoundingBoxes(False)
          debugNode.showNormals(False)
          self.debugNP = render.attachNewNode(debugNode)
          self.debugNP.show()
          self.world.bw.setDebugNode(self.debugNP.node())

    def showDBG(self, b):
        if b:
	    self.debugNP.show()
	else:
	    self.debugNP.hide()    

    def pause(self):
        self.app.taskMgr.remove("update")
        self.pausemenu = PauseMenu(self.app, self)

        self.pausemenu.enter()

    def resume(self):

        self.app.taskMgr.add(self.update, "update")

    def update(self, task):

        if(self.app.mouseWatcherNode.hasMouse()):
            self.app.mousePos.x = self.app.mouseWatcherNode.getMouseX()
            self.app.mousePos.y = self.app.mouseWatcherNode.getMouseY()
            self.world.update(task.time)  

        return Task.cont
