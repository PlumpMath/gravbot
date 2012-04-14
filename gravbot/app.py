from direct.showbase.ShowBase import ShowBase
from gravbot.mainmenu import MainMenu
from panda3d.core import loadPrcFileData
from gravbot.explorescreen import ExploreScreen

import utilities

class App(ShowBase):

    def __init__(self, args):
        ShowBase.__init__(self)

        loadPrcFileData('', 'bullet-enable-contact-events true') 

        self.screens = []

	if args == "test":
	    utilities.setDebug()
	    self.screens.append(ExploreScreen(self))
	else:    
            self.screens = []
            self.screens.append(MainMenu(self))

    def run(self):
        # start first screen
        self.screens[-1].enter()

        ShowBase.run(self)

