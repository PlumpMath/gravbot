# basic pathfinding

from panda3d.core import Mat4, Point3, Vec3
from panda3d.bullet import BulletBodyNode

# Build a voxel based representation
# For the next n steps with delta d
def buildMap(collidableEntities, steps=1, delta=1.0, debug=False):
    cmap = [[0 for i in range(40)] for j in range(40)]
    for entity in collidableEntities:
        pos = entity.np.getPos()
        tfm = entity.np.getMat()
        if debug: print tfm
        for i in range(entity.bnode.getNumShapes()):
            stfm = entity.bnode.getShapeMat(i)
            spos = entity.bnode.getShapePos(i)
            if debug: print "nodepath matrix \n" + str(tfm)
            if debug: print "shape matrix \n " + str(stfm)
            stfm = tfm * stfm
            if debug: print "new matrix \n" + str(stfm)
            if debug: print "point " + str(spos)
            tfp = stfm.xformPoint(spos)
            tfp -= spos
            if debug: print "transformed point " + str(tfp)
            # might be out of range    
            try:     
                cmap[int(tfp.z)][int(tfp.x)] = 1
            except:
                pass
    return cmap

def printMap(cmap):
    s = ""
    for i in range(20):
        line = ""
        for j in range(20):
            line = line + str(cmap[i][j])
        s = line + '\n' + s
    print s



