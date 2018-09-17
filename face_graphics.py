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
import base64
import sys
import os
from io import BytesIO
from PIL import Image

class Thumbnail:
    PAD = 10
    SIZE_X = 50
    SIZE_Y = 50
    LIFE_TIME = 1
    SPEED_X = 20
    SPEED_Y = 10
    SPEED_ALPHA = 10
    THICK = 1

    def __init__(self, person, idx):
        self.person = person
        self.face = np.frombuffer(base64.decodestring(self.person.b64image.encode()), dtype=np.uint8)
        self.face = cv2.imdecode(self.face, cv2.IMREAD_COLOR)
        self.face = cv2.cvtColor(self.face, cv2.COLOR_BGR2RGB)

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
        player = pygame.image.frombuffer(self.face.tostring(), self.face.shape[1::-1], 'RGB',)
        player = pygame.transform.scale(player, (self.SIZE_Y-2*self.THICK, self.SIZE_Y-2*self.THICK))
        s = pygame.Surface((self.SIZE_X,self.SIZE_Y))
        s.set_alpha(self.alpha)
        pygame.draw.rect(s, GraphicPyGame.COLOR_GREEN, (0, 0, self.SIZE_Y, self.SIZE_Y))
        s.blit(player, (self.THICK, self.THICK))
        screen.blit(s, (self.x, self.y))

class BBox:
    TEXT_FACTOR = 0.1
    MIN_TEXT = 15
    MARGIN_POS = 0.05
    MARGIN_SIZE = 0.05
    SPEED_POS = 25
    SPEED_SIZE = 50

    def __init__(self, id, bbox, person, matching):
        self.id = id
        self.x, self.y, self.w, self.h = bbox
        self.x -= int(self.w * self.MARGIN_POS)
        self.y -= int(self.w * self.MARGIN_POS)
        self.w += int(2 * self.w * self.MARGIN_POS)
        self.h += int(2 * self.h * self.MARGIN_POS)
        self.target_x, self.target_y, self.target_w, self.target_h = self.x, self.y, self.w, self.h
        self.x = int(self.target_x + self.target_w/2)
        self.y = int(self.target_y + self.target_h/2)
        self.w = 1
        self.h = 1
        self.thickness = max(1, int(min(self.w, self.h)/100))
        if self.thickness % 2 == 0:
            self.thickness += 1
        self.person = person
        self.matching = matching
    
    def update_bbox(self, bbox, person, matching):
        self.person = person
        self.matching = matching
        x, y, w, h = bbox
        x -= int(w * self.MARGIN_POS)
        y -= int(w * self.MARGIN_POS)
        w += int(2 * w * self.MARGIN_POS)
        h += int(2 * h * self.MARGIN_POS)
        if abs(w - self.w) > self.w * self.MARGIN_SIZE:
            self.target_w = w
            self.target_h = h
        if abs(x - self.x) > self.w * self.MARGIN_POS:
            self.target_x = x
        if abs(y - self.y) > self.w * self.MARGIN_POS:
            self.target_y = y

    def update(self):
        if self.x < self.target_x:
            self.x = min(self.x + self.SPEED_POS, self.target_x)
        elif self.x > self.target_x:
            self.x = max(self.x - self.SPEED_POS, self.target_x)
        if self.y < self.target_y:
            self.y = min(self.y + self.SPEED_POS, self.target_y)
        elif self.y > self.target_y:
            self.y = max(self.y - self.SPEED_POS, self.target_y)
        if self.w < self.target_w:
            self.w = min(self.w + self.SPEED_SIZE, self.target_w)
        elif self.w > self.target_w:
            self.w = max(self.w - self.SPEED_SIZE, self.target_w)
        if self.h < self.target_h:
            self.h = min(self.h + self.SPEED_SIZE, self.target_h)
        elif self.h > self.target_h:
            self.h = max(self.h - self.SPEED_SIZE, self.target_h)


    def draw(self, screen, list_thumbnail):
        info = None
        sf_bbox = None
        if self.person is None and self.matching:
            color = GraphicPyGame.COLOR_WHITE
            sf_bbox = GraphicPyGame.BBOX_WHITE
        elif self.person is None and not self.matching:
            color = GraphicPyGame.COLOR_RED
            sf_bbox = GraphicPyGame.BBOX_RED
            info = GraphicPyGame.FONT_VIETNAMESE.render('Unknown', False, GraphicPyGame.COLOR_RED)
        elif self.person is not None:
            color = GraphicPyGame.COLOR_GREEN
            sf_bbox = GraphicPyGame.BBOX_GREEN
            info = GraphicPyGame.FONT_VIETNAMESE.render(self.person.name, False, GraphicPyGame.COLOR_WHITE)
            for tn in list_thumbnail:
                if tn.person.id == self.person.id:
                    pygame.draw.lines(screen, color, False, [(self.x - self.thickness, self.y-self.thickness), (tn.x + Thumbnail.SIZE_X, tn.y)])
                    break
        sf_bbox = pygame.transform.scale(sf_bbox, (self.w, self.h))
        screen.blit(sf_bbox, (self.x, self.y))

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
    BBOX_GREEN = None
    BBOX_RED = None
    BBOX_WHITE = None

    def __init__(self, width, height, queue=None):
        self.frame = None
        self.running = True
        GraphicPyGame.WIDTH = width
        GraphicPyGame.HEIGHT = height
        self.list_thumbnail = []
        self.list_bbox = []
        self.queue = queue
        
        pygame.init()
        self.mask = pygame.Surface((self.WIDTH, self.HEIGHT))
        self.mask.set_alpha(20)
        # self.mask.fill((0,128,128))
        for i in range(0, self.HEIGHT, 5):
            pygame.draw.line(self.mask, (255,255,255), (0,i), (self.WIDTH,i))
        GraphicPyGame.FONT_VIETNAMESE = pygame.font.Font('font/Montserrat-Medium.otf', 100)
        GraphicPyGame.FONT_JAPANESE = pygame.font.Font('font/NotoSansMonoCJKjp-Regular.otf', 100)
        self.screen = pygame.display.set_mode((GraphicPyGame.WIDTH, GraphicPyGame.HEIGHT))
        GraphicPyGame.BBOX_GREEN = self.create_bbox_template(GraphicPyGame.COLOR_GREEN)
        GraphicPyGame.BBOX_RED = self.create_bbox_template(GraphicPyGame.COLOR_RED)
        GraphicPyGame.BBOX_WHITE = self.create_bbox_template(GraphicPyGame.COLOR_WHITE)
    
    def set_frame(self, frame):
        self.frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    def put_update(self, frame, multi_tracker):
        self.frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # self.list_bbox = []
        tmp = []
        for tracker in multi_tracker.get_multitracker():
            bbox = None
            for item in self.list_bbox:
                if item.id == tracker.id:
                    bbox = item
                    break
            if tracker.person is None and tracker.receive < vision_config.NUM_TRIED:
                if bbox is None:
                    bbox = BBox(tracker.id, tracker.bounding_box, None, True)
                else:
                    bbox.update_bbox(tracker.bounding_box, None, True)
            elif tracker.person is None:
                if bbox is None:
                    bbox = BBox(tracker.id, tracker.bounding_box, None, False)
                else:
                    bbox.update_bbox(tracker.bounding_box, None, False)
            else:
                if bbox is None:
                    bbox = BBox(tracker.id, tracker.bounding_box, tracker.person, False)
                else:
                    bbox.update_bbox(tracker.bounding_box, tracker.person, False)
                self.add_thumbnail(tracker.person)
            tmp.append(bbox)
        self.list_bbox = tmp

    def add_thumbnail(self, person):
        for tn in self.list_thumbnail:
            if tn.person.id == person.id:
                tn.last_time = time.time()
                return
        tn = Thumbnail(person, 0)
        self.list_thumbnail.insert(0, tn)
        for i in range(1, len(self.list_thumbnail)):
            self.list_thumbnail[i].set_position(i)

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
            if tn.last_time + Thumbnail.LIFE_TIME > time.time():
                tmp.append(tn)
        self.list_thumbnail = tmp
        for i in range(len(self.list_thumbnail)):
            self.list_thumbnail[i].set_position(i)

    def create_bbox_template(self, color):
        x = 1601
        xx = (x-1)/4
        d = 12
        m = (3*d-1)/2
        sf_bbox = pygame.Surface((x, x)).convert_alpha()
        sf_bbox.fill((0, 0, 0, 0))
        pygame.draw.lines(sf_bbox, color, True, [(m,m), (x-m,m), (x-m,x-m), (m,x-m)], d)
        pygame.draw.lines(sf_bbox, color, False, [((x-1)/2,m), ((x-1)/2,7*m)], d)
        pygame.draw.lines(sf_bbox, color, False, [((x-1)/2,x-m), ((x-1)/2,x-7*m)], d)
        pygame.draw.lines(sf_bbox, color, False, [(m,(x-1)/2), (7*m,(x-1)/2)], d)
        pygame.draw.lines(sf_bbox, color, False, [(x-m,(x-1)/2), (x-7*m,(x-1)/2)], d)

        pygame.draw.polygon(sf_bbox, color, [(0,0), (xx,0), (xx,3*d), (3*d,3*d), (3*d,xx), (0,xx)], 0)
        pygame.draw.polygon(sf_bbox, color, [(x,0), (x,xx), (x-3*d,xx), (x-3*d,3*d), (x-xx,3*d), (x-xx,0)], 0)
        pygame.draw.polygon(sf_bbox, color, [(x,x), (x-xx,x), (x-xx,x-3*d), (x-3*d,x-3*d), (x-3*d,x-xx), (x,x-xx)], 0)
        pygame.draw.polygon(sf_bbox, color, [(0,x), (0,x-xx), (3*d,x-xx), (3*d,x-3*d), (xx,x-3*d), (xx,x)], 0)
        return sf_bbox

    def draw(self):
        self.screen.fill(0)
        player = pygame.image.frombuffer(self.frame.tostring(), self.frame.shape[1::-1], 'RGB',)
        self.screen.blit(player, (0, 0))
        for tn in self.list_thumbnail:
            tn.draw(self.screen)
        for bbox in self.list_bbox:
            bbox.update()
            bbox.draw(self.screen, self.list_thumbnail)
        # self.screen.blit(self.mask, (0,0))

    def convert_jpeg(self):
        data = pygame.image.tostring(self.screen, 'RGB')
        img = Image.frombytes('RGB', (GraphicPyGame.WIDTH, GraphicPyGame.HEIGHT), data)
        zdata = BytesIO()
        img.save(zdata, 'JPEG')
        return zdata.getvalue()

    def run(self):
        clock = pygame.time.Clock()
        # self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT), pygame.FULLSCREEN )
        id = 0
        while self.running:
            # try:
            start_time = time.time()
            if self.frame is not None:
                self.update_thumbnail()
                self.draw()
                pygame.display.flip()
            if self.queue is not None:
                self.queue.put(self.convert_jpeg())
            for event in pygame.event.get():
                if event.type==pygame.QUIT:
                    self.running = False
                    pygame.quit() 
                    exit(0)
            print(time.time() - start_time)
            clock.tick(self.FPS)
            # except Exception as e:
            #     exc_type, exc_obj, exc_tb = sys.exc_info()
            #     fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            #     print(exc_type, fname, exc_tb.tb_lineno)
            #     self.running = False
            #     break

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
        