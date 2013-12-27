from direct.showbase.ShowBase import ShowBase
from panda3d.core import loadPrcFileData
from gravbot.explorescreen import ExploreScreen
import utilities

class App(ShowBase):
    def __init__(self, args):
        ShowBase.__init__(self)
        loadPrcFileData('', 'bullet-enable-contact-events true') 
        self.explore = None

        if args == "test":
            utilities.setDebug()
            self.explore = ExploreScreen(self)
        else:
            self.explore = ExploreScreen(self)

    def run(self):
        # start first screen
        ShowBase.run(self)

