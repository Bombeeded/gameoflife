import numpy as np
import pygame, pygame.freetype, sys, random
from pygame.locals import *

#initialize board
pygame.init()
pygame.freetype.init()
clock = pygame.time.Clock()
programFont = pygame.freetype.Font(file="Arial Unicode.ttf", size=12)
pygame.freetype.set_default_resolution(200)
cell_num = 50

#initialize graphics
FPS = 60

background_color = (92, 36, 115)
cell_color = (222, 235, 40)
white = (255,255,255)
black = (0,0,0)
red = (255,60,0)

width = 500
menu_buffer = 150
height = 500
cell_width = int(width/cell_num)

DISPLAYSURF = pygame.display.set_mode((width+menu_buffer,height))
DISPLAYSURF.fill(background_color)
pygame.display.set_caption("The Game of Life")

class board(np.ndarray):
    def draw(self,point):      
        pygame.draw.rect(DISPLAYSURF, cell_color, (point[1]*cell_width,point[0]*cell_width,cell_width,cell_width))
        self[point] = 1

    def erase(self,point):
        pygame.draw.rect(DISPLAYSURF, background_color, (point[1]*cell_width,point[0]*cell_width,cell_width,cell_width))
        self[point] = 0

    def __init__(self,dim):
        #dim is a tuple, like (20,30)
        self.shape = [dim[0],dim[1]]
        self.fill(0)
        self.dtype = int
        self.x_list = np.arange(0,dim[0])
        self.y_list = np.arange(0,dim[1])
        self.tallyarray = np.zeros(self.shape)
        self.frameCount = 0

    def board_initalize(self):
        #establish menu
        pygame.draw.rect(DISPLAYSURF, white, (width,0,menu_buffer,height))

        #establish board
        for x in self.x_list:
            for y in self.y_list:
                if self[x,y] == 1:
                    self.draw((x,y))
                else:
                    self.erase((x,y))
    
    def periodicmap(self, inputpoint):
        #map a point that lies outside of the array onto the array, such that the array is periodic/toroidal
        dim0 = self.shape[0]
        dim1 = self.shape[1]
        input0 = inputpoint[0]
        input1 = inputpoint[1]
        if input0 >= dim0:
            output0 = np.mod(input0,dim0)
        else:
            output0 = input0
        if input1 >= dim1:
            output1 = np.mod(input1,dim1)
        else:
            output1 = input1
        return (output0,output1)

    def evaluate(self, point):
        i = point[0]
        j = point[1]

        aa = self.periodicmap((i-1,j-1))
        ab = self.periodicmap((i,j-1))
        ac = self.periodicmap((i+1,j-1))
        ba = self.periodicmap((i-1,j))
        #bb = self.periodicmap((i,j))     #Unnecesssary: that is the point in question
        bc = self.periodicmap((i+1,j))
        ca = self.periodicmap((i-1,j+1))
        cb = self.periodicmap((i,j+1))
        cc = self.periodicmap((i+1,j+1))

        '''
        aa ba ca
        ab bb cb       layout
        ac bc cc
        '''
        
        tally = 0
        if self[aa] == 1:
            tally += 1
        if self[ab] == 1:
            tally += 1
        if self[ac] == 1:
            tally += 1
        if self[ba] == 1:
            tally += 1    
        if self[bc] == 1:
            tally += 1
        if self[ca] == 1:
            tally += 1
        if self[cb] == 1:
            tally += 1
        if self[cc] == 1:
            tally += 1

        self.tallyarray[point] = tally

    def modify(self,point):
        tally = self.tallyarray[point]
        if self[point] == 1:
            if tally < 2:
                self.erase(point)
            if tally == 2 or tally == 3:
                pass
            if tally > 3:
                self[point] = 0
                self.erase(point)

        if self[point] == 0:
            if tally == 3:
                self[point] = 1
                self.draw(point)
            else:
                pass
                
    def iterate(self):
        for x in self.x_list:
            for y in self.y_list:
                self.evaluate((x,y))
        for x in self.x_list:
            for y in self.y_list:
                self.modify((x,y))
    
    def randomize_board(self):
        for x in self.x_list:
            for y in self.y_list:
                self[x,y] = random.choice((0,1))

#initial board conditions
playground = board((cell_num,cell_num))
playground.randomize_board()
playground.board_initalize()

#create menu
pause_state = 0 #0 is unpaused, 1 is paused
def pause(x):
    if x == 1:
        x = 0
        return x

    if x == 0:
        x = 1
        return x

def changeFPS(x,key):
    if ((key == K_DOWN)):
        x += -5
        if x <=0:
            x = 1
            return x
    if ((key == K_UP)):
        if x == 1:
            x = 5
            return x
        else:
            x += 5
            return x
    else:
        return x
        
        
def render_framecount():
    frameCount_text = "Frame count: " + str(playground.frameCount)
    programFont.render_to(DISPLAYSURF, (505,5), frameCount_text, black)

def render_FPS():
    FPS_text = "FPS: " + str(round(clock.get_fps(),ndigits=2))
    programFont.render_to(DISPLAYSURF, (505,25), FPS_text, black)

def render_instructions():
    programFont.render_to(DISPLAYSURF, (505,465), "Arrows key limit fps.", red)
    programFont.render_to(DISPLAYSURF, (505,485), "Press space to pause.", red)

def render_setFPS():
    setFPS_text = "FPS limiter: " + str(FPS)
    programFont.render_to(DISPLAYSURF, (505,45), setFPS_text, black)

if __name__ == "__main__":
    while True:
        while pause_state == 0: #general event handling
            #update game
            pygame.display.update()
            clock.tick(FPS)
            playground.iterate()

            playground.frameCount += 1

            #update menu
            pygame.draw.rect(DISPLAYSURF, white, (width,0,menu_buffer,height)) #redraw menu
            render_framecount()
            render_FPS()
            render_instructions()
            render_setFPS()

            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                
                if event.type == KEYDOWN:
                    FPS = changeFPS(FPS,event.key)
                    if ((event.key == K_SPACE)):
                        pause_state = pause(pause_state)

        while pause_state == 1:  #event handling in paused state
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                
                if event.type == KEYDOWN:
                    if ((event.key == K_SPACE)):
                        pause_state = pause(pause_state)