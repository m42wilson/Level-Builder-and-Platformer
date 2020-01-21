_author_ = "Matthew Wilson"
_date_ = "Nov 28, 2018"
_version_ = 3.0
_filename_ = "PlatformerGame.py"
_description_ = """A platformer with the ability to design levels. The AI was
                   removed because deciding when to terminate a run was
                   incredibly complex."""

import pygame

#pretty much exclusively for finding distances
import math

#for a delay in a menu so that it doesn't leave ASAP
import time

#initializes a file that can be saved to.
try:
    newfile = open("saves.txt", 'r')
except:
    newfile = open("saves.txt", 'w')

newfile.close()

class Constants:
    """This class exlcusively stores constants and returns them. It does not
       allow changes to the values, and it can store all of the constants in
       one place. Idea, that I originally mocked, stolen from Emily Zhou.
       I realized it was a good idea and took it."""
    def __init__(self):
        self.__font = pygame.font.SysFont('arialblack', 25, True, False)
        self.__screen_size = (1024,768)
        self.__block_length = 64
        self.__fall_check = 2
        self.__print_loc = (200, 400)
        self.__in_range_val = 196
        self.__build_screen = (128, 32)
        self.__platform_colour = (0,0,0)
        self.__goal_colour = (0,255,0)
        self.__blade_colour = (255,0,0)
        self.__bounzy_colour = (0,0,255)
        self.__gravel_colour = (200,200,200)

    def get_screen_size(self):
        return self.__screen_size
    def get_screen_height(self):
        return self.__screen_size[1]
    def get_screen_width(self):
        return self.__screen_size[0]
    def block_length(self):
        return self.__block_length
    def fall_check(self):
        return self.__fall_check
    
    def get_print_loc(self):
        return self.__print_loc
    def get_in_range_val(self):
        return self.__in_range_val

    def get_build_screen(self):
        return self.__build_screen

    def get_font(self):
        return self.__font

class Platform(object):
    '''Contains the information on any platform type that the player
       can walk on; x and y coordinates, width and height, and is
       the parent class to all other types of platform.'''
    def __init__(self,x,y,w,h):
        self.__x = x
        self.__y = y
        self.__w = w
        self.__h = h
        self.__colour = (0,0,0)
        self.__type = 1

    def coords(self):
        return (self.__x,self.__y,self.__w,self.__h)
    def colour(self):
        return self.__colour
    def get_type(self):
        return self.__type

    def collide(self, player):
        #it works. A bit weird since the player character's height
        #is negative for few good reasons other than having my origin
        #in the bottom left. This is probably why my collision is off by one.

        #if the player's Y is greater than the platform's Y.
        if player.coords()[1] > self.__y:
            #and the player's Y minus its height is less than the platform's Y plus its height
            if player.coords()[1] + player.get_dimensions()[1] < self.__y + self.__h:
                #and the player's X plus its width is greater than the platform's X
                if player.coords()[0] + player.get_dimensions()[0] > self.__x:
                    #and the player's X is less than the platform's X minus its width.
                    if player.coords()[0] < self.__x + self.__w:
                        #then it finally returns true.
                        return True
        return False

    def distance(self, player):
        return math.sqrt(((self.__x - player.coords()[0] + player.get_dimensions()[0])**2)+((self.__y - player.coords()[1] - player.get_dimensions()[1])**2))

class Goal(Platform):
    '''A platform that must be reached to win any game'''
    def __init__(self,x,y,w,h):
        super(Goal, self).__init__(x,y,w,h)
        self.__colour = (0,255,0)
        self.__type = 2
    def get_type(self):
        return self.__type
    def colour(self):
        return self.__colour

class Blade(Platform):
    '''a platform that damages the player. Take too much damage and restart the level'''
    def __init__(self, x, y, w, h):
        super(Blade, self).__init__(x,y,w,h)
        self.__colour = (255,0,0)
        self.__type = 3
    def get_type(self):
        return self.__type
    def colour(self):
        return self.__colour

class Bounzy(Platform):
    '''a platform that forces the player into a jump'''
    def __init__(self, x, y, w, h):
        super(Bounzy, self).__init__(x,y,w,h)
        self.__colour = (0,0,255)
        self.__type = 4
    def get_type(self):
        return self.__type
    def colour(self):
        return self.__colour

class Gravel(Platform):
    '''a platform that falls after it is stepped on'''
    def __init__(self, x, y, w, h):
        super(Gravel, self).__init__(x,y,w,h)
        self.__startY = y
        self.__timer = 0
        self.__colour = (200,200,200)
        self.__type = 5
        
    def get_type(self):
        return self.__type
    def colour(self):
        return self.__colour
    def get_timer(self):
        return self.__timer

    def reset(self):
        self._Platform__y = self.__startY
        self.__timer = 0
        
    def fall(self):
        if self.__timer >= 100:
            #ok, this I had to google, but it's python for "ignore the
            #encapsulation"
            self._Platform__y += 2
        self.__timer += 1
        
class Gridline(Platform):
    '''not a platform that can be stood on, but it exists as a child of Platform
       because that makes it easier to draw.'''
    def __init__(self, x, y, w, h):
        super(Gridline,self).__init__(x, y, w, h)
        self.__colour = (200,200,200)

    def colour(self):
        return self.__colour

class Player:
    '''This class contains all information for the user's character, including
       coordinates and size of the player, and methods to change the x and y
       location of the player. An instance of the Player class is what the
       user moves around the screen.'''
    def __init__(self,x,y):
        self.__w = 48
        self.__h = -96
        self.__x = x
        self.__y = y

    def xmod(self,val):
        self.__x += val

    def ymod(self,val):
        self.__y += val

    def coords(self):
        return (self.__x, self.__y)

    def get_dimensions(self):
        return (self.__w, self.__h)

    def get_draw(self):
        return (self.__x, self.__y, self.__w, self.__h)

def save(locations):
    '''This allows the player to save a level that they created.'''
    new_save = ""
    for line in locations:
        for i in line:
            if i != None:
                new_save += "%s %s %s,"%(str(i.get_type()),str(i.coords()[0]),str(i.coords()[1]))
    new_save = new_save[:-1] + "\n" #newline character has to be added since .write() does not do a newline automatically
    save_file = open("saves.txt", 'a')
    save_file.write(new_save)
    save_file.close()
        
def load(C, index):
    '''This allows the player to load a saved level.'''
    save_file = open("saves.txt", 'r')

    platforms = []
    locations = []
    for i in range(C.get_build_screen()[1]):
        hold = []
        for j in range(C.get_build_screen()[0]):
            hold.append(None)
        locations.append(hold)
    try:
        for line in range(index):
            save_file.readline()
    except IndexError:
        return None
    data = save_file.readline().split(",")

    for block in data:
        block = block.split()
        if int(block[0]) == 1:
            new = Platform(int(block[1]), int(block[2]), C.block_length(), C.block_length())
        elif int(block[0]) == 2:
            new = Goal(int(block[1]), int(block[2]), C.block_length(), C.block_length())
        elif int(block[0]) == 3:
            new = Blade(int(block[1]), int(block[2]), C.block_length(), C.block_length())
        elif int(block[0]) == 4:
            new = Bounzy(int(block[1]), int(block[2]), C.block_length(), C.block_length())
        elif int(block[0]) == 5:
            new = Gravel(int(block[1]), int(block[2]), C.block_length(), C.block_length())
        locations[int(block[0])/C.block_length()][int(block[1])/C.block_length()] = new
        platforms.append(new)
    return (locations, platforms)
    
def load_screen(screen, clock, C):
    '''admittedly not the best load screen. I couldn't think of
       an easy way to identify which level is which, so that is
       the number one thing that is missing. Had I allowed the
       player to name a file, the code to recognise the inputs
       for that and print those inputs to the screen in real time
       would be massive and tedious with what I know of pygame.'''
    save_file = open("saves.txt", 'r')
    num_saves = 0
    page = 0
    for line in save_file:
        num_saves += 1
    save_file.close()

    mouse_loc = (0,0)
    bouse_button = (0,0,0)
    
    
    button1 = (C.get_screen_size()[0]*1/16, C.get_screen_size()[1]*2/16, C.get_screen_size()[0]*4/16, C.get_screen_size()[1]*5/16)
    button2 = (C.get_screen_size()[0]*1/16, C.get_screen_size()[1]*9/16, C.get_screen_size()[0]*4/16, C.get_screen_size()[1]*5/16)
    button3 = (C.get_screen_size()[0]*6/16, C.get_screen_size()[1]*2/16, C.get_screen_size()[0]*4/16, C.get_screen_size()[1]*5/16)
    button4 = (C.get_screen_size()[0]*6/16, C.get_screen_size()[1]*9/16, C.get_screen_size()[0]*4/16, C.get_screen_size()[1]*5/16)
    button5 = (C.get_screen_size()[0]*11/16, C.get_screen_size()[1]*2/16, C.get_screen_size()[0]*4/16, C.get_screen_size()[1]*5/16)
    button6 = (C.get_screen_size()[0]*11/16, C.get_screen_size()[1]*9/16, C.get_screen_size()[0]*4/16, C.get_screen_size()[1]*5/16)
    back_button = (0, 0, (C.get_screen_size()[0] * 1)/8,  (C.get_screen_size()[1] * 1)/16)
    prev_button = (C.get_screen_size()[0]*4/16, C.get_screen_size()[1]*29/32, C.get_screen_size()[0]*2/16, C.get_screen_size()[1]*1/16)
    next_button = (C.get_screen_size()[0]*10/16, C.get_screen_size()[1]*29/32, C.get_screen_size()[0]*3/16, C.get_screen_size()[1]*1/16)


    back_text = C.get_font().render("Back",True,(150,150,150))
    next_text = C.get_font().render("Next",True,(150,150,150))
    prev_text = C.get_font().render("Prev",True,(150,150,150))

    #I need to render these every time a next/prev button is clicked
    saves = map(str,range(6*page+1, 6*page+7))
    text1 = C.get_font().render(saves[0],True,(150,150,150))
    text2 = C.get_font().render(saves[1],True,(150,150,150))
    text3 = C.get_font().render(saves[2],True,(150,150,150))
    text4 = C.get_font().render(saves[3],True,(150,150,150))
    text5 = C.get_font().render(saves[4],True,(150,150,150))
    text6 = C.get_font().render(saves[5],True,(150,150,150))

    time.sleep(0.25)
    while True:
        #define colours
        colour1 = (0,0,0)
        colour2 = (0,0,0)
        colour3 = (0,0,0)
        colour4 = (0,0,0)
        colour5 = (0,0,0)
        colour6 = (0,0,0)
        colour7 = (0,0,0)
        colour8 = (0,0,0)
        colour9 = (0,0,0)
        
        #event loop
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_button = pygame.mouse.get_pressed()
        mouse_loc = pygame.mouse.get_pos()

        #mouse locations and colour changes and returns. all the fun stuff.
        #yup. should have put them in a function. Oh well, that's for when
        #I actually finish this game, long past the due date.
        if mouse_loc[0] > button1[0] and mouse_loc[0] < button1[0] + button1[2]:
            if mouse_loc[1] > button1[1] and mouse_loc[1] < button1[1] + button1[3]:
                colour1 = (255,255,255)
                if pygame.mouse.get_pressed()[0]:
                    try:
                        return load(C, 6*page+5)
                    except:
                        return None
        
            elif mouse_loc[1] > button2[1] and mouse_loc[1] < button2[1] + button2[3]:
                colour2 = (255,255,255)
                if pygame.mouse.get_pressed()[0]:
                    try:
                        return load(C, 6*page+6)
                    except:
                        return None

        if mouse_loc[0] > button3[0] and mouse_loc[0] < button3[0] + button3[2]:
            if mouse_loc[1] > button3[1] and mouse_loc[1] < button3[1] + button3[3]:
                colour3 = (255,255,255)
                if pygame.mouse.get_pressed()[0]:
                    try:
                        return load(C, 6*page+7)
                    except:
                        return None
                
            elif mouse_loc[1] > button4[1] and mouse_loc[1] < button4[1] + button4[3]:
                colour4 = (255,255,255)
                if pygame.mouse.get_pressed()[0]:
                    try:
                        return load(C, 6*page+8)
                    except:
                        return None
                
        if mouse_loc[0] > button5[0] and mouse_loc[0] < button5[0] + button5[2]:
            if mouse_loc[1] > button5[1] and mouse_loc[1] < button5[1] + button5[3]:
                colour5 = (255,255,255)
                if pygame.mouse.get_pressed()[0]:
                    try:
                        return load(C, 6*page+9)
                    except:
                        return None
                
            elif mouse_loc[1] > button6[1] and mouse_loc[1] < button6[1] + button6[3]:
                colour6 = (255,255,255)
                if pygame.mouse.get_pressed()[0]:
                    try:
                        return load(C, 6*page+10)
                    except:
                        return None

        if mouse_loc[0] > back_button[0] and mouse_loc[0] < back_button[0] + back_button[2]:
            if mouse_loc[1] > back_button[1] and mouse_loc[1] < back_button[1] + back_button[3]:
                colour7 = (255,255,255)
                if pygame.mouse.get_pressed()[0]:
                    return None
        #here we allow the user to go to a next or previous page when loading saved games
        if mouse_loc[0] > next_button[0] and mouse_loc[0] < next_button[0] + next_button[2]:
            if mouse_loc[1] > next_button[1] and mouse_loc[1] < next_button[1] + next_button[3]:
                colour8 = (255,255,255)
                if pygame.mouse.get_pressed()[0]:
                    if page < (num_saves+5/6):
                        page += 1
                        saves = map(str,range(6*page+1, 6*page+6))
                        text1 = C.get_font.render(saves[0],True,(150,150,150))
                        text2 = C.get_font.render(saves[1],True,(150,150,150))
                        text3 = C.get_font.render(saves[2],True,(150,150,150))
                        text4 = C.get_font.render(saves[3],True,(150,150,150))
                        text5 = C.get_font.render(saves[4],True,(150,150,150))
                        text6 = C.get_font.render(saves[5],True,(150,150,150))
                    
        if mouse_loc[0] > prev_button[0] and mouse_loc[0] < prev_button[0] + prev_button[2]:
            if mouse_loc[1] > prev_button[1] and mouse_loc[1] < prev_button[1] + prev_button[3]:
                colour9 = (255,255,255)
                if pygame.mouse.get_pressed()[0]:
                    if page > 0:
                        page -= 1
                        saves = map(str,range(6*page+1, 6*page+6))
                        text1 = C.get_font.render(saves[0],True,(150,150,150))
                        text2 = C.get_font.render(saves[1],True,(150,150,150))
                        text3 = C.get_font.render(saves[2],True,(150,150,150))
                        text4 = C.get_font.render(saves[3],True,(150,150,150))
                        text5 = C.get_font.render(saves[4],True,(150,150,150))
                        text6 = C.get_font.render(saves[5],True,(150,150,150))
    
        #Draw
        #change colour
        screen.fill((150,150,150))
        pygame.draw.rect(screen, colour1 ,button1,0)
        pygame.draw.rect(screen, colour2 ,button2,0)
        pygame.draw.rect(screen, colour3 ,button3,0)
        pygame.draw.rect(screen, colour4 ,button4,0)
        pygame.draw.rect(screen, colour5 ,button5,0)
        pygame.draw.rect(screen, colour6 ,button6,0)
        pygame.draw.rect(screen, colour7 ,back_button,0)
        pygame.draw.rect(screen, colour8 ,next_button,0)
        pygame.draw.rect(screen, colour9 ,prev_button,0)
        screen.blit(text1, (button1[0],button1[1]))
        screen.blit(text2, (button2[0],button2[1]))
        screen.blit(text3, (button3[0],button3[1]))
        screen.blit(text4, (button4[0],button4[1]))
        screen.blit(text5, (button5[0],button5[1]))
        screen.blit(text6, (button6[0],button6[1]))
        screen.blit(back_text, (back_button[0],back_button[1]))
        screen.blit(next_text, (next_button[0],next_button[1]))
        screen.blit(prev_text, (prev_button[0],prev_button[1]))
        #draw buttons, including exit button4
        pygame.display.flip()
        clock.tick(60)

def arc(time):
    return (-0.02*(time**2) + 6*time) - (-0.02*(time-1)**2 + 6*(time-1))

def fallArc(time):
    return (-0.02*(time**2) - (-0.02*(time-1)**2))

#Now, a bubble sort is usually fairly slow, but where it shines is with
#nearly-sorted lists. Since the platforms' distances don't change too
#much between 2 sorts, especially not compared to each other, the list
#will always be nearly-sorted. This means that a bubble sort is going
#to be incredibly efficient.
def platformSort(array, anchor):
    for top in range(len(array)-1, 0, -1):
        done = True
        for i in range(top):
            if array[i].distance(anchor) > array[i+1].distance(anchor):
                done = False
                hold = array[i]
                array[i] = array[i+1]
                array[i+1] = hold
        if done:
            break
    return array

#similarly, since we know the value will always be relatively early in the
#list, a squential sort becomes more efficient if there are upwards of 200
#platforms in a level.
def platformSearch(array, anchor, range_val):
    #this is not returning the index value of the item, but the number of items
    #that fit the conditions.
    count = 0
    for i in range(len(array)):
        if array[i].distance(anchor) > range_val:
            break
        count += 1
    return count


def menu(screen, clock, C):
    '''The menu just holds the values for where to click to activate certain other
       functions, like the level selection menu or level builder.'''
    #define locations, all relative to the screen size if I want to scale it.
    header = ((C.get_screen_size()[0] * 1)/4, (C.get_screen_size()[1] * 1)/16, (C.get_screen_size()[0] * 1)/2,  (C.get_screen_size()[1] * 1)/4)
    button1 = ((C.get_screen_size()[0] * 1)/4, (C.get_screen_size()[1] * 6)/16, (C.get_screen_size()[0] * 1)/2,  (C.get_screen_size()[1] * 1)/8)
    button2 = ((C.get_screen_size()[0] * 1)/4, (C.get_screen_size()[1] * 9)/16, (C.get_screen_size()[0] * 1)/2,  (C.get_screen_size()[1] * 1)/8)
    button3 = ((C.get_screen_size()[0] * 1)/4, (C.get_screen_size()[1] * 12)/16, (C.get_screen_size()[0] * 1)/2,  (C.get_screen_size()[1] * 1)/8)
    button4 = (0, 0, (C.get_screen_size()[0] * 1)/8,  (C.get_screen_size()[1] * 1)/16)
    text1 = C.get_font().render("Level Select", True, (150,150,150))
    text2 = C.get_font().render("Level Creator", True, (150,150,150))
    text3 = C.get_font().render("Options", True, (150,150,150))
    text4 = C.get_font().render("Quit", True, (150,150,150))
    output = None
    
    #to prevent errors
    mouse_loc = (0,0)
    mouse_button = (0,0,0)
    time.sleep(0.5)
    while not output:
        #just to make it look more polished we change colours as we scroll over
        #the buttons
        colour1 = (0,0,0)
        colour2 = (0,0,0)
        colour3 = (0,0,0)
        colour4 = (0,0,0)
        
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_button = pygame.mouse.get_pressed()
        mouse_loc = pygame.mouse.get_pos()

        if mouse_loc[0] > button1[0] and mouse_loc[0] < button1[0] + button1[2]:
            if mouse_loc[1] > button1[1] and mouse_loc[1] < button1[1] + button1[3]:
                colour1 = (255,255,255)
                #if someone pressed the left click button
                if pygame.mouse.get_pressed()[0]:
                    output = 1 
        
            elif mouse_loc[1] > button2[1] and mouse_loc[1] < button2[1] + button2[3]:
                colour2 = (255,255,255)
                #if someone pressed the left click button
                if pygame.mouse.get_pressed()[0]:
                    output = 2 

            #not implemented
            elif mouse_loc[1] > button3[1] and mouse_loc[1] < button3[1] + button3[3]:
                colour3 = (255,255,255)
                #if someone pressed the left click button
                if pygame.mouse.get_pressed()[0]:
                    pass
                    
        if mouse_loc[0] > button4[0] and mouse_loc[0] < button4[0] + button4[2]:
            if mouse_loc[1] > button4[1] and mouse_loc[1] < button4[1] + button4[3]:
                colour4 = (255,255,255)
                #if someone pressed the left click button
                if pygame.mouse.get_pressed()[0]:
                    output = 3

        screen.fill((10,150,250))
        #draw button locations; removed button 3 (options) until I have the
        #AI functioning
        pygame.draw.rect(screen, (0,0,0) ,header,0)
        pygame.draw.rect(screen, colour1 ,button1,0)
        pygame.draw.rect(screen, colour2 ,button2,0)
        #pygame.draw.rect(screen, colour3 ,button3,0)
        pygame.draw.rect(screen, colour4 ,button4,0)
        screen.blit(text1, (button1[0],button1[1]))
        screen.blit(text2, (button2[0],button2[1]))
        #screen.blit(text3, (button3[0],button3[1]))
        screen.blit(text4, (button4[0],button4[1]))
        pygame.display.flip()
        clock.tick(60)

    return output

def level_select(screen, clock, C):
    '''a level similar to the main menu that allows the user to access the 4 premade levels'''
    mouse_loc = (0,0)
    mouse_button = (0,0,0)
    #define level button location
    back_button = (0, 0, (C.get_screen_size()[0] * 1)/8,  (C.get_screen_size()[1] * 1)/16)
    button1 = (C.get_screen_size()[0]*1/8, C.get_screen_size()[1]*1/16, C.get_screen_size()[0]*3/4, C.get_screen_size()[1]*1/8)
    button2 = (C.get_screen_size()[0]*1/8, C.get_screen_size()[1]*4/16, C.get_screen_size()[0]*3/4, C.get_screen_size()[1]*1/8)
    button3 = (C.get_screen_size()[0]*1/8, C.get_screen_size()[1]*7/16, C.get_screen_size()[0]*3/4, C.get_screen_size()[1]*1/8)
    button4 = (C.get_screen_size()[0]*1/8, C.get_screen_size()[1]*10/16, C.get_screen_size()[0]*3/4, C.get_screen_size()[1]*1/8)
    button5 = (C.get_screen_size()[0]*1/8, C.get_screen_size()[1]*13/16, C.get_screen_size()[0]*3/4, C.get_screen_size()[1]*1/8)
    back_text = C.get_font().render("Back", True, (150,150,150))
    text1 = C.get_font().render("1", True, (150,150,150))
    text2 = C.get_font().render("2", True, (150,150,150))
    text3 = C.get_font().render("3", True, (150,150,150))
    text4 = C.get_font().render("4", True, (150,150,150))
    text5 = C.get_font().render("5", True, (150,150,150))
    
    output = None
    time.sleep(0.25)
    while True:
        #define colours
        colour1 = (0,0,0)
        colour2 = (0,0,0)
        colour3 = (0,0,0)
        colour4 = (0,0,0)
        colour5 = (0,0,0)
        colour6 = (0,0,0)
                
        #event loop
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_button = pygame.mouse.get_pressed()
        mouse_loc = pygame.mouse.get_pos()

        #All mouse locations here share their x values, so no need to have elifs
        #because that cuts off all buttons but the first, and ifs are slower when
        #we only need to do it once.
        if mouse_loc[0] > button1[0] and mouse_loc[0] < button1[0] + button1[2]:
            if mouse_loc[1] > button1[1] and mouse_loc[1] < button1[1] + button1[3]:
                colour1 = (255,255,255)
                if pygame.mouse.get_pressed()[0]:
                    play(screen,clock,C, (0,1920), False, load(C,0)[1])
        
            elif mouse_loc[1] > button2[1] and mouse_loc[1] < button2[1] + button2[3]:
                colour2 = (255,255,255)
                if pygame.mouse.get_pressed()[0]:
                    play(screen,clock,C, (0,1920), False, load(C,1)[1])

            elif mouse_loc[1] > button3[1] and mouse_loc[1] < button3[1] + button3[3]:
                colour3 = (255,255,255)
                if pygame.mouse.get_pressed()[0]:
                    play(screen,clock,C, (0,1920), False, load(C,2)[1])
                
            elif mouse_loc[1] > button4[1] and mouse_loc[1] < button4[1] + button4[3]:
                colour4 = (255,255,255)
                if pygame.mouse.get_pressed()[0]:
                    play(screen,clock,C, (0,448), False, load(C,3)[1])
                    
            #didn't have an idea for the fifth level, so there isn't one
            #elif mouse_loc[1] > button5[1] and mouse_loc[1] < button5[1] + button5[3]:
             #   colour5 = (255,255,255)
              #  if pygame.mouse.get_pressed()[0]:
               #     output = 5

        if mouse_loc[0] > back_button[0] and mouse_loc[0] < back_button[0] + back_button[2]:
            if mouse_loc[1] > back_button[1] and mouse_loc[1] < back_button[1] + back_button[3]:
                colour6 = (255,255,255)
                if pygame.mouse.get_pressed()[0]:
                    return None
        #I realize now that this should have been put in a function, because
        #boy do I have it copied and pasted a lot in my 4 different selection
        #screens.

        #Draw
        #change colour
        screen.fill((50,50,50))
        
        pygame.draw.rect(screen, colour1, button1,0)
        pygame.draw.rect(screen, colour2, button2,0)
        pygame.draw.rect(screen, colour3, button3,0)
        pygame.draw.rect(screen, colour4, button4,0)
        #pygame.draw.rect(screen, colour5, button5,0)
        pygame.draw.rect(screen, colour6, back_button,0)

        screen.blit(text1, (button1[0], button1[1]))
        screen.blit(text2, (button2[0], button2[1]))
        screen.blit(text3, (button3[0], button3[1]))
        screen.blit(text4, (button4[0], button4[1]))
        #screen.blit(text5, (button5[0], button5[1]))
        screen.blit(back_text, (back_button[0], back_button[1]))
        pygame.display.flip()
        clock.tick(60)
    
def mini_menu(C, clock, screen, platforms, player, printLocation, from_game = True):
    ''' a menu that is accessed from the game to allow restarting, saving,
        exiting to the menu, and other functions that make life easier for
        the player'''
    selection_screen = ((C.get_screen_size()[0] * 5)/16, (C.get_screen_size()[1] * 1)/4, (C.get_screen_size()[0] * 6)/16,  (C.get_screen_size()[1] * 1)/2)
    title = ((C.get_screen_size()[0] * 12)/32, (C.get_screen_size()[1] * 1)/4, (C.get_screen_size()[0] * 4)/16,  (C.get_screen_size()[1] * 3)/32)
    button1 = ((C.get_screen_size()[0] * 12)/32, (C.get_screen_size()[1] * 12)/32, (C.get_screen_size()[0] * 1)/4,  (C.get_screen_size()[1] * 1)/16)
    button2 = ((C.get_screen_size()[0] * 12)/32, (C.get_screen_size()[1] * 15)/32, (C.get_screen_size()[0] * 1)/4,  (C.get_screen_size()[1] * 1)/16)
    button3 = ((C.get_screen_size()[0] * 12)/32, (C.get_screen_size()[1] * 18)/32, (C.get_screen_size()[0] * 1)/4,  (C.get_screen_size()[1] * 1)/16)
    button4 = ((C.get_screen_size()[0] * 12)/32, (C.get_screen_size()[1] * 21)/32, (C.get_screen_size()[0] * 1)/4,  (C.get_screen_size()[1] * 1)/16)
    #text rendering
    text1 = C.get_font().render("Return", True, (150,150,150))
    if from_game:
        text2 = C.get_font().render("Restart", True, (150,150,150))
        text3 = C.get_font().render("", True, (150,150,150))
    else:
        text2 = C.get_font().render("Save", True, (150,150,150))
        text3 = C.get_font().render("Load", True, (150,150,150))
    text4 = C.get_font().render("Exit", True, (150,150,150))

    mouse_loc = (0,0)
    mouse_button = None
    #I wanted any action to return us to the game screen, not to this screen,
    #so 
    output = None
    while not output:
        #define colours
        colour1 = (0,0,0)
        colour2 = (0,0,0)
        colour3 = (0,0,0)
        colour4 = (0,0,0)
        #We want to draw the main screen beneath the menu to give a sense of
        #the game being paused in the background, se we call our level_draw.
        level_draw(screen, platforms, player, printLocation, from_game)

        #and again we draw our menu on top of it.
        if not from_game:
            pygame.draw.rect(screen, (0,0,0),(0,(C.get_screen_height()*24)/32, C.get_screen_width(), (C.get_screen_height()*8)/32), 0)
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_button = pygame.mouse.get_pressed()
        mouse_loc = pygame.mouse.get_pos()

        #again, they share x values, so this always activates
        if mouse_loc[0] > button1[0] and mouse_loc[0] < button1[0] + button1[2]:
            if mouse_loc[1] > button1[1] and mouse_loc[1] < button1[1] + button1[3]:
                colour1 = (255,255,255)
                if pygame.mouse.get_pressed()[0]:
                    output = 1
            if mouse_loc[1] > button2[1] and mouse_loc[1] < button2[1] + button2[3]:
                colour2 = (255,255,255)
                if pygame.mouse.get_pressed()[0]:
                    output = 2 
            if mouse_loc[1] > button3[1] and mouse_loc[1] < button3[1] + button3[3]:
                colour3 = (255,255,255)
                if pygame.mouse.get_pressed()[0]:
                    output = 3
                
            if mouse_loc[1] > button4[1] and mouse_loc[1] < button4[1] + button4[3]:
                colour4 = (255,255,255)
                if pygame.mouse.get_pressed()[0]:
                    output = 4

        pygame.draw.rect(screen, (60,60,60), selection_screen, 0)
        pygame.draw.rect(screen, (0,0,0), title, 0)
        pygame.draw.rect(screen, colour1, button1, 0)
        pygame.draw.rect(screen, colour2, button2, 0)
        if not from_game:
            pygame.draw.rect(screen, colour3, button3, 0)
            screen.blit(text3, (button3[0], button3[1]))
        pygame.draw.rect(screen, colour4, button4, 0)
        screen.blit(text1, (button1[0], button1[1]))
        screen.blit(text2, (button2[0], button2[1]))
        
        screen.blit(text4, (button4[0], button4[1]))
        pygame.display.flip()
        clock.tick(60)
    return output

def level_draw(screen, platforms, player, printLocation, visible= True):
    '''Draw the player and blocks to the screen'''
    #I never got around to optimizing this one function, which slows down
    #everything. This is probably why it's slow, if it is.
    screen.fill((10,150,250))
    #draw player in constant or near-constant location, so long as we are
    #playing a level. If it is from the builder, this looks bad.
    if visible:
        pygame.draw.rect(screen,(0,0,0),(printLocation[0],printLocation[1],player.get_dimensions()[0], player.get_dimensions()[1]),0)
    for square in platforms:
        n = square.coords()
        pygame.draw.rect(screen,square.colour(),(n[0] - player.coords()[0] + printLocation[0], n[1] - player.coords()[1] + printLocation[1], n[2], n[3]),0)

def play(screen, clock, C, player_loc, AI_enabled, platforms = []):
    '''Once a game is started, this function loops. This simulates all the
       physics and collisions and the functions of each block, it is the
       actual game part of this program.'''
    
    #at some point, I should rename the variables out of camelCase.
    #I didn't and that is just terrible naming convention. I was using
    #camelCase for the first, like, 2 days, but I did a lot of physics
    #framework that I didn't get around to fixing up.
    #please don't be disappointed?
    PlayerChar = Player(player_loc[0], player_loc[1])
    
    #sort the platforms immediately for speed
    platforms = platformSort(platforms, PlayerChar)
    platforms_in_range = platformSearch(platforms, PlayerChar, C.get_in_range_val())
    falling_gravel = []
    gone_gravel = []
    #I want the player to start , always, at the leftmost side of one block. 
    #Therefore, the x and y values will always start at a multiple of 64. The 
    #sort should reset halfway through a block, so x = 8 + the block's x, once 
    #we've accounted for the size of the player. 
    re_sort_coords = (-8,-8)

    #booleans take up less space than integers for directional movement
    #and they allow more robust inputs, since I can do a combination of 2.
    #sure, they cancel out, but it still allows for more nuanced inputs
    #when one doesn't immediately change direction
    leftMovement = False
    rightMovement = False

    #not in constants becuase I might want to change it to accelerating
    #speed, rather than constant at a later point.
    speed = 4
    

    jumping = False
    jumpTimer = 0
    falling = False
    fallTimer = 0
    
    died = False
    death_tick = 0
    lives = 3
    win = False
    end = False
            
    #exterior loop; the game runs until it doesn't.
    while not (win or end):
        
        if died:
            if death_tick == 0:
                lives -= 1
                death_tick = 60
                #if you fall to your death, it's an insta-kill and lives are
                #set to 0, then -1.
                if lives <= 0:
                    #3 lives in a level and when you die, you restart.
                    #that's acceptable, and I can scale up/down for difficulty's
                    #sake.
                    #need to resort the platforms again here for efficeincy
                    platforms += gone_gravel
                    gone_gravel = []
                    for platform in platforms:
                        if platform.get_type() == 5:
                            platform.reset()
                    del PlayerChar
                    PlayerChar = Player(player_loc[0], player_loc[1])
                    falling_gravel = []
                    death_tick = 0
                    fall_timer = 0
                    jump_timer = 0
                    jumping = False
                    falling = False
                    lives = 3
            died = False
        #to prevent me dying repeatedly
        if death_tick > 0:
            death_tick -= 1


        #event loops are just terrible; if you use pygame.KEYDOWN,
        #it will only actvate when the key is pressed down, not if it's
        #held down. This solution incorporates boolean variables that turn
        #on when the key is pressed down, and turn off when the key is
        #let up, essentialy checking if the key is being held down, but
        #it uses a lot of resources compared to pygame,key.get_pressed().
        #The advantage is, it actually works, rather than not works.
        #If I find a way to get keypressed to work, I will replace the current
        #method. It will probably need a tick counter to slow it down.
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    leftMovement = True
                if event.key == pygame.K_d:
                    rightMovement = True
                    
                if event.key == pygame.K_SPACE:
                    if jumping == False:
                        PlayerChar.ymod(C.fall_check())
                        #switch to checking the nearest ones
                        for block in platforms:
                            if block.collide(PlayerChar):
                                PlayerChar.ymod(-C.fall_check())
                                jumping = True
                                falling = False
                                fall_timer = 0
                                
                if event.key == pygame.K_ESCAPE:
                    hold = mini_menu(C, clock, screen, platforms, PlayerChar, C.get_print_loc())
                    if hold == 1:
                        pass
                    elif hold == 4:
                        end = True
                        #automatically goes to a level screen, if I code it right
                    elif hold == 2:
                        #restart, but nothing for now.
                        
                        platforms += gone_gravel
                        gone_gravel = []
                        for platform in platforms:
                            if platform.get_type() == 5:
                                platform.reset()
                        del PlayerChar
                        PlayerChar = Player(player_loc[0], player_loc[1])
                        falling_gravel = []
                        death_tick = 0
                        fall_timer = 0
                        jump_timer = 0
                        jumping = False
                        falling = False
                        lives = 3
                    
                #if key is escape, allow the player to access
                #a dropdown menu to leave the game, restart, etc.
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_a:
                    leftMovement = False
                if event.key == pygame.K_d:
                    rightMovement = False


        #after getting input, but before checking the movement,
        #I need to re-sort my platform list to be in order.
        #I want to do it every few dozen x values for the player
                    
        #solution: store the player coords when it is activated.
        #if the current value is far enough from the new value, then sort
        #again. This avoids the problem of doing the sort every few ticks,
        #and the problem of doing it every few integer x-coord changes.
        #one is too frequent and slows down the game, and the second is too
        #infrequent and causes the player to fall through some blocks
        #on the y-coord.

        #performing a bubble sort because the list is always going to be
        #nearly sorted, but on large maps with lots of blocks it still slows
        #down every 64 x or y coordinates. still better than checking all
        #of them I'm sure.
        if (abs(PlayerChar.coords()[0] - re_sort_coords[0]) > 64 or
            abs(PlayerChar.coords()[1] - re_sort_coords[1]) > 64):
            platforms = platformSort(platforms, PlayerChar)
        #I have calculated the number of platforms in a 128-pixel range from
        #the player character. This will be used when checking all of the
        #platform blocks to significantly cut down on collision checks.
        #I'll be checking no more than half a dozen blocks at any point,
        #rather than the possibly hundreds on the screen. I thought of
        #putting this check inside the sort to improve efficeincy, but
        #doing it in the sort does not solve our problems. The advantage
        #though, is I get to do a search algorithm. I know that the value
        #will be between 1 and not even 20 at the edge case, so if there
        #are hundreds of platforms, then a binary search has diminishing
        #returns. In fact, the more platforms there are, the less efficient
        #binary search becomes. Sequential search, then, is probably best,
        #even though the list is already sorted. 
            platforms_in_range = platformSearch(platforms, PlayerChar, C.get_in_range_val())
            re_sort_coords = PlayerChar.coords()

        #I feel like I could cut down the comparisons on both here
        #with the right structure. It only has to collide once.
        #anywy, these are my left and right collisions.
        if leftMovement:
            PlayerChar.xmod(-speed)
            collide = True
            for block in range(platforms_in_range):
                if platforms[block].collide(PlayerChar):
                    collide = False
                    hold = platforms[block].get_type()
                    if hold == 2:
                        win = True
                    elif hold == 3:
                        died = True
                    #do nothing on 4 and 5; I only want those to
                    #act if hit from a jump / walking above.
            PlayerChar.xmod(speed)
            if collide:
                PlayerChar.xmod(-speed)
                
        
        if rightMovement:
            PlayerChar.xmod(speed)
            collide = True
            for block in range(platforms_in_range):
                if platforms[block].collide(PlayerChar):
                    collide = False
                    hold = platforms[block].get_type()
                    if hold == 2:
                        win = True
                    elif hold == 3:
                        died = True
                    #do nothing on 4 and 5; I only want those to
                    #act if hit from a jump / walking above.
            PlayerChar.xmod(-speed)
            if collide:
                PlayerChar.xmod(speed)

    #when space is hit, jump turns on and fall turns off .
    #when we land on a block, both falling and jumping reset. but we can't reach
    #a block from just a jump, so just falling resets .
    #when we have no ground below us and are not jumping, falling turns on.

        #If I am jumping (starting from the ground), change the y variable
        #by the difference between arc(jumpTimer) and arc(jumpTimer-1)
        if jumping:
            jumpTimer += 1
            PlayerChar.ymod(-arc(jumpTimer))
            
            #if I collide while jumping:
            for block in range(platforms_in_range):
                if platforms[block].collide(PlayerChar):
                    #this is exclusively the y-directional momentum.
                    #as it should be, since the x-directional momentum is
                    #already dealt with above.
                    PlayerChar.ymod(platforms[block].coords()[1] + C.block_length() - PlayerChar.coords()[1] - PlayerChar.get_dimensions()[1])
                    jumping = False
                    falling = True
                    jumpTimer = 0
                    
                    hold = platforms[block].get_type()
                    if hold == 2:
                        win = True
                    elif hold == 3:
                        died = True
                    elif hold == 5:
                        #to prevent it appending one block per tick I stood on it.
                        #good lord did that lag.
                        if not falling_gravel.count(platforms[block]):
                            falling_gravel.append(platforms[block])

            #if the jump arc function changes, modify this value specifically
            if jumpTimer == 75:
                jumping = False
                falling = True
                jumpTimer = 0
            

        #falling physics. To turn it back on, I need to be always checking
        #that there is no ground beneath me. this is a pain. otherwise, I can
        #assume that there is no ground and check for collision, but this
        #makes it harder to deal with exponential falling distances. First
        #is probably easier.
        elif falling:  
            fallTimer += 1
            fallspeed = -fallArc(fallTimer)
            #a max speed less than the size of a block, because I'm
            #anticipating glitchy behavior.
            #This is also enough to not break the platform sorting. I think.
            #I have yet to see it break, but it could.
            if fallspeed > 48:
                fallspeed = 48
            PlayerChar.ymod(fallspeed)
            
            #if I collide while falling:
            for block in range(platforms_in_range):
                #I want to make the player, should it collide with a block,
                #get the Y value of the block + 1. This works since
                #The origin of the block is in the upper left corner, but
                #the origin of my player is in the bottom left. see? useful.
                if platforms[block].collide(PlayerChar):
                    PlayerChar.ymod(platforms[block].coords()[1] - PlayerChar.coords()[1])
                    falling = False
                    hold = platforms[block].get_type()
                    if hold == 2:
                        win = True
                    elif hold == 3:
                        died = True
                    elif hold == 4:
                        jumping = True
                        falling = False
                        fallTimer = 0
                    elif hold == 5:
                        if not falling_gravel.count(platforms[block]):
                            falling_gravel.append(platforms[block])

        #check if there is ground that I am walking on
        else:
            fallTimer = 0
            PlayerChar.ymod(C.fall_check())
            collide = False
            for block in range(platforms_in_range):
                if platforms[block].collide(PlayerChar):
                    collide = True
                    hold = platforms[block].get_type()
                    if hold == 2:
                        win_game()
                        break
                    elif hold == 3:
                        died = True
                    elif hold == 4:
                        jumping = True
                        falling = False
                        fallTimer = 0
                    elif hold == 5:
                        if not falling_gravel.count(platforms[block]):
                            falling_gravel.append(platforms[block])
            PlayerChar.ymod(-C.fall_check())
            #if I did not collide, start falling
            if not collide:
                falling = True

        #If I drop below the screen, instant death.
        if PlayerChar.coords()[1] + PlayerChar.get_dimensions()[1] > 64*C.get_build_screen()[1]:
            lives = 0
            died = True

        #The easiest way to get the gravel to fall is just to keep track of
        #what's falling. In this, falling_gravel acts as a FIFO queue. gravel
        #disappears after falling 2 blocks, so the first dropped will be the
        #first removed from the queue.
        hold = 0
        for block in falling_gravel:
            block.fall()
            if block.get_timer() >= 164:
                hold += 1
        
        for i in range(hold):
            gone_gravel.append(platforms[platforms.index(falling_gravel[0])])
            #This only works because each pointer is unique
            platforms.remove(falling_gravel[0])
            falling_gravel.pop(0)
        
                
        #draw code
        level_draw(screen, platforms, PlayerChar, C.get_print_loc())
        pygame.display.flip()
        clock.tick(60)

    #if a platform is falling and you return to the builder screen, the blocks
    #don't return to their usual positions. This is outside the main code
    #because if it were inside, the gravel would fall a slight bit before being
    #sent back
    platforms = platforms + gone_gravel
    for platform in platforms:
        if platform.get_type() == 5:
            platform.reset()

def build(screen, clock, C):
    '''this mode allows the player to build their own level to play through'''
    #first, I want either a constant size to build in, or one I can change with
    #a menu. If I initialize it with a for loop, either is fairly easy.

    grid = []
    #build the grid that is just a visual help
    for i in range(C.get_build_screen()[0]+1):
        grid.append(Gridline((i*C.block_length()-1), 0, 2, (C.get_build_screen()[1]*C.block_length())))
    for i in range(C.get_build_screen()[1]+1):
        grid.append(Gridline(0, (i*C.block_length()-1), (C.get_build_screen()[0]*C.block_length()), 2))

    platforms = []
    hold = []
    locations = []

    #here is my list of empty locations that blocks can be placed in.
    #Each element, if filled, is filled with an instance of the correct class.
    for i in range(C.get_build_screen()[1]):
        hold = []
        for j in range(C.get_build_screen()[0]):
            hold.append(None)
        locations.append(hold)

    
    mouse_loc = (0,0)
    mouse_button = (0,0,0)
    type_held = 0
    drop_type = 'all'
    followblock = None

    #creates the class that follows the player around
    camera = Player(0, C.get_build_screen()[1]*C.block_length()- ((C.get_screen_height()*24)/32))

    #button locations
    trashbutton = (C.get_screen_width()*1/32,(C.get_screen_height()*49)/64, (C.get_screen_width()*7)/32, (C.get_screen_height()*7/32))
    playbutton = (C.get_screen_width()*24/32,(C.get_screen_height()*49)/64, (C.get_screen_width()*7)/32, (C.get_screen_height()*7)/32)
    block1 = (C.get_screen_width()*9/32,(C.get_screen_height()*49)/64, C.block_length()*3/4, C.block_length()*3/4)
    block2 = (C.get_screen_width()*9/32,(C.get_screen_height()*56)/64, C.block_length()*3/4, C.block_length()*3/4)
    block3 = (C.get_screen_width()*11/32,(C.get_screen_height()*49)/64, C.block_length()*3/4, C.block_length()*3/4)
    block4 = (C.get_screen_width()*11/32,(C.get_screen_height()*56)/64, C.block_length()*3/4, C.block_length()*3/4)
    block5 = (C.get_screen_width()*13/32,(C.get_screen_height()*49)/64, C.block_length()*3/4, C.block_length()*3/4)
    #text
    trash_text = C.get_font().render("Trash", True, (150,150,150))
    play_text = C.get_font().render("Play", True, (150,150,150))

    #make block colour more organized; they're hardcoded in some places, but not
    #others, and there's no easy way to access all of them in the same place
    #I want colour_array[type_held] to give me the colour I need.
    colour_array = [(0,0,0),(0,0,0),(0,255,0),(255,0,0),(0,0,255),(200,200,200) ]

    end = False
    while not end:
        #event loop
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_button = pygame.mouse.get_pressed()
            if event.type == pygame.MOUSEBUTTONUP:
                mouse_button = pygame.mouse.get_pressed()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    hold = mini_menu(C, clock, screen, platforms + grid, camera, (0,0), False)
                    #access to the mini menu; return to game, save, load, and exit.
                    if hold == 2:
                        save(locations)
                    elif hold == 3:
                        hold = load_screen(screen, clock, C)
                        if hold != None:
                            locations = hold[0]
                            platforms = hold[1]
                    elif hold == 4:
                        #break while loop
                        end = True
                        
                
        mouse_loc = pygame.mouse.get_pos()
        #to save time, I only want to update my platforms and locations lists in
        #this code below. Updating it constantly is slow.

        if mouse_loc[0] > 0 and mouse_loc[0] < C.get_screen_width() and mouse_loc[1] > 0 and mouse_loc[1] < (C.get_screen_height()*24)/32:
            #These are the location values, adjusted for the size of the blocks,
            #the location of the camera, and then the mouse position.
            x = ((mouse_loc[0] + camera.coords()[0]) / C.block_length())
            y = ((mouse_loc[1] + camera.coords()[1]) / C.block_length())

            #if mouse is not held down, it's fun to have the block follow you.
            #This is the data for that.
            if type_held:
                followblock = (x,y,colour_array[type_held])
            #if the mouse is held down / pressed down:
            if mouse_button[0]:                
                #just this is enough for moving blocks from one spot to another.
                #That's kind of impressive, actually.
                if type_held == None:
                    if locations[y][x] != None:
                        type_held = locations[y][x].get_type()
                        platforms.pop(platforms.index(locations[y][x]))
                        locations[y][x] = None
                        drop_type = 'one'
                        mouse_button = (0,0,0)
                #yeah, ends here.
                    
                #The only change in here is what value 'new' gets, but this way I know it will have no errors.
                elif type_held == 1:
                    #platform locations are guaranteed to be unique because of this check.
                    #this means that I can remove them by using their coords, not their
                    #location in the list. No need to store extra variables.
                    if locations[y][x] == None:
                        #create the block once since it returns a pointer to it and I actually want
                        #the same block in both locations. Mostly to save space, but also prevents what
                        #might be weird errors. It also lets me remove the block much more easily.
                        new = Platform(x*C.block_length(), y*C.block_length(), C.block_length(), C.block_length())
                        locations[y][x] = new
                        platforms.append(new)
                        if drop_type == 'one':
                            mouse_button = (0,0,0)
                            type_held = None
                            follow_block = None
                #repeated becuase the only change is what class instance is
                #being made
                elif type_held == 2:
                    if locations[y][x] == None:
                        new = Goal(x*C.block_length(), y*C.block_length(), C.block_length(), C.block_length())
                        locations[y][x] = new
                        platforms.append(new)
                        if drop_type == 'one':
                            mouse_button = (0,0,0)
                            type_held = None
                            follow_block = None
                elif type_held == 3:
                    if locations[y][x] == None:
                        new = Blade(x*C.block_length(), y*C.block_length(), C.block_length(), C.block_length())
                        locations[y][x] = new
                        platforms.append(new)
                        if drop_type == 'one':
                            mouse_button = (0,0,0)
                            type_held = None
                            follow_block = None
                elif type_held == 4:
                    if locations[y][x] == None:
                        new = Bounzy(x*C.block_length(), y*C.block_length(), C.block_length(), C.block_length())
                        locations[y][x] = new
                        platforms.append(new)
                        if drop_type == 'one':
                            mouse_button = (0,0,0)
                            type_held = None
                            follow_block = None
                elif type_held == 5:
                    if locations[y][x] == None:
                        new = Gravel(x*C.block_length(), y*C.block_length(), C.block_length(), C.block_length())
                        locations[y][x] = new
                        platforms.append(new)
                        if drop_type == 'one':
                            mouse_button = (0,0,0)
                            type_held = None
                            follow_block = None
                
                #elif type_held == 6: when that type of platform is made. Just copy and paste
                #only change the type, since it's so general.
        
        else:
            #mouse is in block select screen, below the grid.

            #if the mouse is below the grids, remove the followblock.
            followblock = None
            #trash button deletes your hand
            if mouse_loc[0] > trashbutton[0] and mouse_loc[0] < trashbutton[0] + trashbutton[2] and mouse_loc[1] > trashbutton[1] and mouse_loc[1] < trashbutton[1] + trashbutton[3]:
                if mouse_button[0]:
                    #no disadvantage to having mouse_button stay as it is in here. yet.
                    type_held = None
                    drop_type = None
            #play button calls play()
            elif mouse_loc[0] > playbutton[0] and mouse_loc[0] < playbutton[0] + playbutton[2] and mouse_loc[1] > playbutton[1] and mouse_loc[1] < playbutton[1] + playbutton[3]:
                if mouse_button[0]:
                    mouse_button = (0,0,0)
                    play(screen,clock, C, (0,0), False, platforms)
            #everything below selects a block type to place.
            if mouse_loc[0] > block1[0] and mouse_loc[0] < block1[0] + block1[2] and mouse_loc[1] > block1[1] and mouse_loc[1] < block1[1] + block1[3]:
                if mouse_button[0]:
                    type_held = 1
                    #should probably be a boolean (to save space) but the name is not clear enough
                    drop_type = 'all'
            if mouse_loc[0] > block2[0] and mouse_loc[0] < block2[0] + block2[2] and mouse_loc[1] > block2[1] and mouse_loc[1] < block2[1] + block2[3]:
                if mouse_button[0]:
                    type_held = 2
                    drop_type = 'all'

            if mouse_loc[0] > block3[0] and mouse_loc[0] < block3[0] + block3[2] and mouse_loc[1] > block3[1] and mouse_loc[1] < block3[1] + block3[3]:
                if mouse_button[0]:
                    type_held = 3
                    drop_type = 'all'

            if mouse_loc[0] > block4[0] and mouse_loc[0] < block4[0] + block4[2] and mouse_loc[1] > block4[1] and mouse_loc[1] < block4[1] + block4[3]:
                if mouse_button[0]:
                    type_held = 4
                    drop_type = 'all'

            if mouse_loc[0] > block5[0] and mouse_loc[0] < block5[0] + block5[2] and mouse_loc[1] > block5[1] and mouse_loc[1] < block5[1] + block5[3]:
                if mouse_button[0]:
                    type_held = 5
                    drop_type = 'all'

            #and repeat the copied if statement for all block types. easy.
                    

        #Ok, this just allows us to scroll through the level we are designing.
        #If the mouse is in the farthest 1/32nd of the screen in any direction,
        #and the camera is not out of bounds, then it moves the camera.
                    
        #these are not the best boundaries, but they do the job.
        if mouse_loc[0] < (C.get_screen_size()[0])/32 and camera.coords()[0] > 0:
            camera.xmod(-8)
        elif mouse_loc[0] > (C.get_screen_size()[0]*31)/32 and camera.coords()[0] < C.get_build_screen()[0]*C.block_length() - C.get_screen_width():
            camera.xmod(8)

        if mouse_loc[1] < (C.get_screen_size()[1])/32 and camera.coords()[1] > 0:
            camera.ymod(-8)
        elif (mouse_loc[1] > (C.get_screen_size()[1]*23)/32 and mouse_loc[1] < (C.get_screen_size()[1]*24)/32 and
              camera.coords()[1] < (C.get_build_screen()[1])*C.block_length() - ((C.get_screen_height()*24)/32)):
            camera.ymod(8)

        #I modified the draw so that the camera is invisible. Otherwise,
        #the player is drawn, which does not look good.
        level_draw(screen, platforms + grid, camera, (0,0), False)

        if followblock:
            #if the follow block is on, print it on the tile the mouse is. This works
            #thanks to integer division truncating the decimal place.
            pygame.draw.rect(screen, followblock[2],(followblock[0]*C.block_length()- camera.coords()[0], followblock[1]*C.block_length() - camera.coords()[1], C.block_length(), C.block_length()), 0)

        #big box at the bottom
        pygame.draw.rect(screen, (50,50,50),(0,(C.get_screen_height()*3)/4, C.get_screen_width(), (C.get_screen_height()*8)/32), 0)
        #draw the selection options; trash, play, blocks, etc.
        pygame.draw.rect(screen, (255,255,255), trashbutton, 0)
        pygame.draw.rect(screen, (255,255,255), playbutton, 0)
        pygame.draw.rect(screen, colour_array[1], block1, 0)
        pygame.draw.rect(screen, colour_array[2], block2, 0)
        pygame.draw.rect(screen, colour_array[3], block3, 0)
        pygame.draw.rect(screen, colour_array[4], block4, 0)
        pygame.draw.rect(screen, colour_array[5], block5, 0)
        #play and trash texts
        screen.blit(play_text, (playbutton[0],playbutton[1]))
        screen.blit(trash_text, (trashbutton[0],trashbutton[1]))
        pygame.display.flip()
        clock.tick(60)

def main():
    '''the function that describes the flow of the program overall.
       it initializes pygame, my constants, the clock, and the screen.'''
    pygame.init()
    clock = pygame.time.Clock()
    C = Constants()

    screen = pygame.display.set_mode(C.get_screen_size())
    pygame.display.set_caption("levelmaker")
    while True:
        next_screen = menu(screen, clock, C)
        #Then, depending on the value recieved from menu, use if statements
        #go into different gamemodes.
        if next_screen == 1:
            #call play from level select. The level selection will
            #load the level data from saves.txt.
            level_select(screen,clock,C)
        elif next_screen == 2:
            build(screen, clock, C)
            #create gamemode
        else:
            #end the game.
            pygame.quit()

#call to main
main()
