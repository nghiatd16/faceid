import pygame
from pygame.locals import *
import cv2
import time
import numpy as np
import _thread
from random import randint
from object_DL import Person
from TrackingFace import MultiTracker
import vision_config
import logging

class Thumbnail:
    PAD = 10
    SIZE_X = 50
    SIZE_Y = 50
    LIFE_TIME = 1
    SPEED_X = 20
    SPEED_Y = 10
    SPEED_ALPHA = 10

    def __init__(self, person, idx):
        self.person = person
        self.last_time = time.time()
        self.x = 0 - Thumbnail.SIZE_X - int((Thumbnail.PAD + Thumbnail.SIZE_Y)*Thumbnail.SPEED_X/Thumbnail.SPEED_Y)
        self.target_x = Thumbnail.PAD
        self.y = (Thumbnail.PAD + Thumbnail.SIZE_Y)*idx + Thumbnail.PAD
        self.target_y = (Thumbnail.PAD + Thumbnail.SIZE_Y)*idx + Thumbnail.PAD
        self.alpha = 255
        self.target_alpha = 255

    def set_position(self, idx):
        self.target_x = Thumbnail.PAD
        self.target_y = (Thumbnail.PAD + Thumbnail.SIZE_Y)*idx + Thumbnail.PAD

    def draw(self, screen):
        s = pygame.Surface((self.SIZE_X,self.SIZE_Y))
        s.set_alpha(self.alpha)
        s.fill(GraphicPyGame.COLOR_GREEN)
        screen.blit(s, (self.x, self.y))

class BBox:
    TEXT_FACTOR = 0.1
    MIN_TEXT = 15

    def __init__(self, bbox, person, matching):
        self.x, self.y, self.w, self.h = bbox
        self.thickness = max(1, int(min(self.w, self.h)/100))
        if self.thickness % 2 == 0:
            self.thickness += 1
        self.person = person
        self.matching = matching
    
    def draw(self, screen):
        info = None
        if self.person is None and self.matching:
            color = GraphicPyGame.COLOR_WHITE
        elif self.person is None and not self.matching:
            color = GraphicPyGame.COLOR_RED
            info = GraphicPyGame.FONT_VIETNAMESE.render('Unknown', False, GraphicPyGame.COLOR_RED)
        elif self.person is not None:
            color = GraphicPyGame.COLOR_GREEN
            info = GraphicPyGame.FONT_VIETNAMESE.render(self.person.name, False, GraphicPyGame.COLOR_WHITE)
            
        pygame.draw.lines(screen, color, True, [(self.x, self.y), (self.x+self.w, self.y), (self.x+self.w, self.y+self.h), (self.x, self.y+self.h)], self.thickness)
        pygame.draw.lines(screen, color, False, [(self.x + int(self.w/2), self.y), (self.x + int(self.w/2), self.y + 6*self.thickness)], self.thickness)
        pygame.draw.lines(screen, color, False, [(self.x + self.w, self.y + int(self.h/2)), (self.x + self.w - 6*self.thickness, self.y + int(self.h/2))], self.thickness)
        pygame.draw.lines(screen, color, False, [(self.x + int(self.w/2), self.y + self.h), (self.x + int(self.w/2), self.y + self.h - 6*self.thickness)], self.thickness)
        pygame.draw.lines(screen, color, False, [(self.x, self.y + int(self.h/2)), (self.x + 6*self.thickness, self.y + int(self.h/2))], self.thickness)

        pygame.draw.lines(screen, color, False, [(self.x, self.y + int(self.h/4)), (self.x, self.y - self.thickness)], 3*self.thickness)
        pygame.draw.lines(screen, color, False, [(self.x - self.thickness, self.y), (self.x + int(self.w/4), self.y)], 3*self.thickness)
        pygame.draw.lines(screen, color, False, [(self.x + int(self.w*3/4), self.y), (self.x + self.w + self.thickness, self.y)], 3*self.thickness)
        pygame.draw.lines(screen, color, False, [(self.x + self.w, self.y - self.thickness), (self.x + self.w, self.y + int(self.h/4))], 3*self.thickness)
        pygame.draw.lines(screen, color, False, [(self.x + self.w, self.y + int(self.h*3/4)), (self.x + self.w, self.y + self.h + self.thickness)], 3*self.thickness)
        pygame.draw.lines(screen, color, False, [(self.x + self.w + self.thickness, self.y + self.h), (self.x + int(self.w*3/4), self.y + self.h)], 3*self.thickness)
        pygame.draw.lines(screen, color, False, [(self.x + int(self.w/4), self.y + self.h), (self.x - self.thickness, self.y + self.h)], 3*self.thickness)
        pygame.draw.lines(screen, color, False, [(self.x, self.y + self.h + self.thickness), (self.x, self.y + int(self.h*3/4))], 3*self.thickness)
        
        if info is not None:
            # info = GraphicPyGame.FONT_JAPANESE.render(u'ダム・バ・クイーン', False, GraphicPyGame.COLOR_WHITE)
            info_w, info_h = info.get_size()
            min_h = max(int(BBox.TEXT_FACTOR*self.h), self.MIN_TEXT)
            info = pygame.transform.scale(info, (int(min_h*info_w/info_h), min_h))
            screen.blit(info, (self.x, self.y + self.h + 3*self.thickness))

class GraphicPyGame:
    FPS = 24
    WIDTH = 0
    HEIGHT = 0
    COLOR_GREEN = (40,190,80)
    COLOR_WHITE = (255,255,255)
    COLOR_RED = (190,40,40)
    FONT_VIETNAMESE = None
    FONT_JAPANESE = None

    def __init__(self, width, height):
        self.frame = None
        self.running = True
        GraphicPyGame.WIDTH = width
        GraphicPyGame.HEIGHT = height
        self.list_thumbnail = []
        self.list_bbox = []
        
        pygame.init()
        self.mask = pygame.Surface((self.WIDTH, self.HEIGHT))
        self.mask.set_alpha(20)
        # self.mask.fill((0,128,128))
        for i in range(0, self.HEIGHT, 5):
            pygame.draw.line(self.mask, (255,255,255), (0,i), (self.WIDTH,i))
        GraphicPyGame.FONT_VIETNAMESE = pygame.font.Font('font/Montserrat-Medium.otf', 100)
        GraphicPyGame.FONT_JAPANESE = pygame.font.Font('font/NotoSansMonoCJKjp-Regular.otf', 100)
    
    def set_frame(self, frame):
        self.frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    def put_update(self, frame, multi_tracker):
        self.frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        self.list_bbox = []
        for tracker in multi_tracker.get_multitracker():
            if tracker.person is None and tracker.receive < vision_config.NUM_TRIED:
                bbox = BBox(tracker.bounding_box, None, True)
            elif tracker.person is None:
                bbox = BBox(tracker.bounding_box, None, False)
            else:
                bbox = BBox(tracker.bounding_box, tracker.person, False)
                self.add_thumbnail(tracker.person)
            self.list_bbox.append(bbox)

    def add_thumbnail(self, person):
        for tn in self.list_thumbnail:
            if tn.person.id == person.id:
                tn.last_time = time.time()
                return
        tn = Thumbnail(person, 0)
        self.list_thumbnail.insert(0, tn)
        for i in range(1, len(self.list_thumbnail)):
            self.list_thumbnail[i].set_position(i)
        print(len(self.list_thumbnail))

    def del_thumnnail(self):
        del self.list_thumbnail[randint(0, len(self.list_thumbnail)-1)]
        for i in range(len(self.list_thumbnail)):
            self.list_thumbnail[i].set_position(i)

    def update_thumbnail(self):
        tmp = []
        for tn in self.list_thumbnail:
            if tn.x < tn.target_x:
                tn.x = min(tn.target_x, tn.x + Thumbnail.SPEED_X)
            elif tn.x > tn.target_x:
                tn.x = max(tn.target_x, tn.x - Thumbnail.SPEED_X)
            if tn.y < tn.target_y:
                tn.y = min(tn.target_y, tn.y + Thumbnail.SPEED_Y)
            elif tn.y > tn.target_y:
                tn.y = max(tn.target_y, tn.y - Thumbnail.SPEED_Y)
            if tn.alpha < tn.target_alpha:
                tn.alpha = min(tn.target_alpha, tn.alpha + Thumbnail.SPEED_ALPHA)
            elif tn.alpha > tn.target_alpha:
                tn.alpha = max(tn.target_alpha, tn.alpha - Thumbnail.SPEED_ALPHA)

            if tn.last_time + Thumbnail.LIFE_TIME < time.time():
                tmp.append(tn)
        self.list_thumbnail = tmp
        for i in range(len(self.list_thumbnail)):
            self.list_thumbnail[i].set_position(i)

    def draw(self):
        self.screen.fill(0)
        player = pygame.image.frombuffer(self.frame.tostring(), self.frame.shape[1::-1], 'RGB',)
        self.screen.blit(player, (0, 0))
        for tn in self.list_thumbnail:
            tn.draw(self.screen)
        for bbox in self.list_bbox:
            bbox.draw(self.screen)
        self.screen.blit(self.mask, (0,0))

    def run(self):
        clock = pygame.time.Clock()
        # self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT), pygame.FULLSCREEN )
        self.screen = pygame.display.set_mode((GraphicPyGame.WIDTH, GraphicPyGame.HEIGHT))
        id = 0
        while self.running:
            try:
                start_time = time.time()
                if self.frame is not None:
                    self.update_thumbnail()
                    self.draw()
                    pygame.display.flip()

                for event in pygame.event.get():
                    if event.type==pygame.QUIT:
                        self.running = False
                        pygame.quit() 
                        exit(0)
                clock.tick(self.FPS)
            except Exception as e:
                logging.error(e)
                self.running = False
                break

def run_video(graphic):
    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()
        if ret:
            graphic.set_frame(frame)

if __name__ == '__main__':
    # img = cv2.imread('image.jpg')
    graphic = GraphicPyGame(640, 480)
    _thread.start_new_thread(run_video, (graphic,))
    graphic.run()
        