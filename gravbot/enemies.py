# make some homies

from panda3d.core import Point2
from entity import Entity

def Enemy(Entity):
    def __init__(self):
        super(Enemy, self).__init__():


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

