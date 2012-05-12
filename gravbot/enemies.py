# make some homies

from panda3d.core import Point2, Vec3
from entity import Entity

def Enemy(Entity):
    def __init__(self, pos, hpr=Vec3(0,0,0)):
        super(Enemy, self).__init__():
        self.pos = pos

    def update(self, time):
        #move

    def destroy(self):
        self.obj.hide()
	self.obj.destroy()

# melee.
def Catcher(Enemy):
    def __init__(self):
        super(Catcher, self).__init__()

    def update(self, time)	

