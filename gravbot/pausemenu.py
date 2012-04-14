from panda3d.rocket import LoadFontFace, RocketRegion, RocketInputHandler
from gamescreen import GameScreen

class PauseMenu(GameScreen):

    def __init__(self, app, parent):
        GameScreen.__init__(self, app)

        self.parent = parent

        LoadFontFace("menus/Delicious-Roman.otf")

        self.region = RocketRegion.make('pauseMenuRegion', self.app.win)
        print self.region.__doc__
        self.region.setActive(1)
        self.context = self.region.getContext()

        self.menu = self.context.LoadDocument('menus/pause_menu.rml')
        self.menu.hook = self
        
    def enter(self):
        self.menu.Show()

        ih = RocketInputHandler()
        self.app.mouseWatcher.attachNewNode(ih)
        self.region.setInputHandler(ih)

    def exit(self):
        self.region.setActive(0)
        self.menu.Close()

        ih = self.region.getInputHandler()
        del(ih)
        del(self.context)
        del(self.region)

        self.parent.resume()

