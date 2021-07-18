import numpy as np
import matplotlib.image as img
import random

"""
This is a zero-graphics variant of the board class in main.py, being potentially useful for high speed
applications of the game of life. Numba or multiprocessing may be used to improve performance.

The general workflow for the board is such:
-create board object with appropriate dimensions
-import a board preset or utilize a random boardspace
    -if a random setup was chosen, run the board_initialize() function, which prints the random x_list 
    and y_list variables onto the np.array object.
-create a loop that repeatedly runs iterate()

done!!
"""


class Board(np.ndarray):
    def draw(self,point):      
        self[point] = 1

    def erase(self,point):
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
        self.frameCount += 1
        for x in self.x_list:
            for y in self.y_list:
                self.evaluate((x,y))
        for x in self.x_list:
            for y in self.y_list:
                self.modify((x,y))
    
    """
    Below are board initialization methods. 
    
    randomize_board() creates a random board, from which so called "ash objects" will appear.
    Ash objects are objects that are randomly generated via cellular automation from a randomized board.

    import_board_image() will take a black (dead) and white (alive) image with appropriate pixel dimensions 
    for the board and import it as the initial board. Depending on the specific file type, modifications
    may be required in order for the import process to work properly. Common issues are the image
    being imported as a 3 dimensional array, in which case slices would have to be taken. It may also 
    potentially result that the array will need to be organized such that the maximum value within the
    array is 1, the minimum 0, and clasify the entire board as an integer (i.e. binary board configuration).

    read_config() reads a file titled config.txt. Config.txt should be in .rle format and can optionally
    contain a #X and #Y tag that define the position on the board of the object. paste() is used for pasting
    such an object into any specific location.
    """

    def randomize_board(self):
        for x in self.x_list:
            for y in self.y_list:
                self[x,y] = random.choice((0,1))
    
    def import_board_image(self,file):
        np.copyto(self, np.ascontiguousarray(img.imread(file),dtype=int))
    
    def read_config(self):
        config = open('config.txt')
        for line in config:
            if line[0] == '#':
                if line[1] == 'X':
                    wordlist = line.split()
                    imported_xpos = int(wordlist[1])
                if line[1] == 'Y':
                    wordlist = line.split()
                    imported_ypos = int(wordlist[1])
            elif line[0] == 'x':
                wordlist = line.split()
                imported_height = wordlist[5]
                imported_height = int(imported_height[:-1])
                imported_width = wordlist[2]
                imported_width = int(imported_width[:-1])
            else:
                imported_array = np.zeros((imported_height,imported_width))
                i = 0 #across coordinates i.e. x
                j = 0 #up/down coordinates i.e. y
                charcount = 0 #character counter
                #logic handling code decrypting below
                howmanytimes = -1 #essentially turns off the howmanytimes variable for the character
                def magic(numList):
                    s = ''.join(map(str, numList))
                    return int(s)
                def recursive_number_checker(digit):
                    nonlocal charcount
                    digit.append(int(char))
                    if line[charcount+1].isnumeric():
                        charcount += 1
                        recursive_number_checker(digit)
                for char in line:
                    print(char + str((i,j)))
                    #essentially turns off the howmanytimes variable for the character
                    #check if char is a number. if so, iterate the next non-number more times 
                    if char.isnumeric():
                        digit = []
                        recursive_number_checker(digit)
                        howmanytimes = magic(digit)
                    if char == 'b':
                        if howmanytimes == -1:
                            imported_array[j,i] = 0
                            i += 1
                        else:
                            s = 0
                            while s < howmanytimes:
                                imported_array[j,i] = 0
                                s += 1
                                i += 1
                            howmanytimes = -1
                    if char == 'o':
                        if howmanytimes == -1:
                            imported_array[j,i] = 1
                            i += 1
                        else:
                            s = 0
                            while s < howmanytimes:
                                imported_array[j,i] = 1
                                s += 1
                                i += 1
                            howmanytimes = -1
                    if char == '$':
                        if howmanytimes == -1:
                            j += 1
                        else:
                            j += howmanytimes
                            howmanytimes = -1
                        i = 0
                    if char == '!':
                        break
                    charcount += 1
        config.close()
        return imported_array,imported_xpos,imported_ypos,imported_height,imported_width

    def paste(self,block,xpos,ypos): #paste array into section of self
        self[xpos:xpos+block.shape[0], ypos:ypos+block.shape[1]] = block