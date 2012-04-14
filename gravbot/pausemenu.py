from panda3d.rocket import LoadFontFace, RocketRegion, RocketInputHandler
from gamescreen import GameScreen

class PauseMenu(GameScreen):

    def __init__(self, app, parent):
        GameScreen.__init__(self, app)

        self.parent = parent

        LoadFontFace("menus/Delicious-Roman.otf")

        self.region = RocketRegion.make('pauseMenuRegion', self.app.win)
        self.region.setActive(1)
        context = self.region.getContext()

        self.menu = context.LoadDocument('menus/pause_menu.rml')
        self.menu.hook = self
        
    def enter(self):
        self.menu.Show()

        ih = RocketInputHandler()
        self.app.mouseWatcher.attachNewNode(ih)
        self.region.setInputHandler(ih)

    def exit(self):
        self.region.setActive(0)

        # remove input handler?

        self.parent.resume()

