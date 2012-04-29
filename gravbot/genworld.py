# Generate various different shapes with appropriate edges and stuff
#                 float, float,  float,     string,  int
from panda3d.core import Point2
from chunks import Chunk, Block
from random import randint

def picktile(tileset='metalwalls'):
    if tileset == 'metalwalls':
        if randint(0,10) < 8:
	    return 'floor1'
	else:
	    return 'floor2'
        

def genBox(world, pos, width, height, tileset):
    blocks = list()

    #closest fit, but in practical terms blocksize will mostly be 1
    outerX = int(width)
    outerY = int(height)

    for x in range(0,outerX):
        blocks.append(Block(world, Point2(float(x), 0), picktile(tileset), list()))
    for y in range(1,outerY-1):
        blocks.append(Block(world, Point2(float(outerX-1), float(y)), picktile(tileset), list()))
    for x in range(0,outerX):
        blocks.append(Block(world, Point2(float(outerX-1 - x), float(outerY-1)), picktile(tileset), list()))
    for y in range(1,outerY-1):
        blocks.append(Block(world, Point2(float(0), float(outerY - 1 - y)), picktile(tileset), list()))

    #for i in range(0, len(blocks) - 1):
    #    blocks[i].edges.append(blocks[i+1])
    #    blocks[i+1].edges.append(blocks[i])

    #blocks[0].edges.append(blocks[len(blocks) - 1])
    #blocks[len(blocks)-1].edges.append(blocks[0])
    # connect all the horizontals
    for block1 in blocks:
        for block2 in blocks:
	    if(block1 != block2):
                blockdis(block1, block2)


    chunk = Chunk(world, blocks, pos)
    world.addEntity(chunk)     

def genFillBox(world, pos, width, height, tileset):
    blocks = list()
    outerX = int(width)
    outerY = int(height)

    for x in range(0, outerX):
        for y in range(0, outerY):
	    blocks.append(Block(world, Point2(float(x), float(y)), picktile(tileset), list()))

    for block1 in blocks:
        for block2 in blocks:
	    if(block1 != block2):
                blockdis(block1, block2)

    chunk = Chunk(world, blocks, pos)
    world.addEntity(chunk)     


def blockdis(block1, block2):
    if (block1.pos.x - block2.pos.x)**2 + (block1.pos.y - block2.pos.y)**2 == 1.0:
        block1.edges.append(block2)















