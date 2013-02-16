'''
Created on 16.02.2013

@author: student
'''

#!/usr/bin/env python
# -*- coding:utf8 -*-
# Copyright (C) 2011 Maxim Kovalev
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# @version $Id$
# maxim.kovalev@2012.auditory.ru

import pygame
import sys
import math
import argparse
import random

class Sputnik:
    def __init__(self, start_point, g_point, v, planet_r):
        self.point = float(start_point[0]), float(start_point[1])
        self.vx, self.vy = float(v[0]), float(v[1])
        self.g_point = g_point
        self.enginex = self.enginey = 0.0
        self.speed = 0.0
        self.past = []
        self.future = []
        self.zoom = 1.0
        self.planet_r = planet_r
        self.center_shift = 0, 0
        self.willfail = False


    def render(self, surface, color=(0,0,255)):
        to_render = int(self.point[0]*self.zoom + self.center_shift[0]), int(self.point[1]*self.zoom + self.center_shift[1])
        pygame.draw.circle(surface, (255,0,255), to_render, 5)
        pygame.draw.line(surface, (255,0,0), to_render, (to_render[0]-self.enginex*10, to_render[1]-self.enginey*10), 3)
        if len(self.future) >= 2: pygame.draw.lines(surface, (127, 127, 0), False, map( (lambda (x, y, xv, xy): (x*self.zoom + self.center_shift[0], y*self.zoom + self.center_shift[1])), self.future))
        if len(self.past) >= 2: pygame.draw.aalines(surface, color, False, map( (lambda (x, y): (x*self.zoom+self.center_shift[0], y*self.zoom+self.center_shift[1])) , self.past))


    def step(self, fps=25, prediction_distance=10000, history_depth=500, ep=0.01):
        timestep = 25.0/fps
        if self.g_point == self.point:
            ax = ay = 0
        else:
            vx, vy = self.vx, self.vy
            x, y = self.point
            if len(self.future) < 3 or (x, y, vx, vy) != self.future[0]:
                self.future = []
                distance = 0
                while distance < prediction_distance:
                    ax, ay = gravity(self.g_point, (x, y))
                    vx += ax * 5 
                    vy += ay * 5
                    new_x = x + vx*5
                    new_y = y + vy*5 
                    distance += dist((x,y), (new_x, new_y))
                    x, y = new_x, new_y 
                    self.future.append( (x, y, vx, vy) )
                    if dist((x, y), self.g_point) <= self.planet_r:
                        self.willfail = True
                        break
                    else:
                        self.willfail = False
            else:
                x, y, vx, vy = self.future[-1]
                del self.future[0]
                ax, ay = gravity(self.g_point, (x, y))
                vx += 25*ax/fps
                vy += 25*ay/fps
                x += 25*vx/fps
                y += 25*vy/fps
                self.future.append( (x, y, vx, vy) )
            ax, ay = gravity(self.g_point, self.point)
        ax += self.enginex*ep
        ay += self.enginey*ep
        self.vx += ax * timestep
        self.vy += ay *timestep
        x, y = self.point
        x += self.vx * timestep
        y += self.vy * timestep
        self.point = x, y
        self.speed = math.sqrt(self.vx*self.vx+self.vy*self.vy)
        self.past.append(self.point)
        if len(self.past) >= history_depth:
            del self.past[0]

    def process_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.enginey = -1
            elif event.key == pygame.K_DOWN:
                self.enginey = 1
            elif event.key == pygame.K_LEFT:
                self.enginex = -1
            elif event.key == pygame.K_RIGHT:
                self.enginex = 1
        elif event.type == pygame.KEYUP:
            if event.key in [pygame.K_UP, pygame.K_DOWN]:
                self.enginey = 0
            elif event.key in [pygame.K_LEFT, pygame.K_RIGHT]:
                self.enginex = 0

def gravity(g_point, sputnik):
    gx, gy = g_point
    sx, sy = sputnik
    dx = float(gx - sx)
    dy = float(gy - sy)
    dst = math.sqrt(dx*dx + dy*dy)
    force = 200/(dst*dst)
    fx = dx*force/dst
    fy = dy*force/dst
    return fx, fy

class Label(object):
    def __init__(self, text, form, **kwargs):
        """ self, text, form, color=(0,0,0), font="Arial", fontsize=24, align="left" """
        self.text = text
        self.form = form
        self.color = kwargs.get("color", (32,255,32))
        self.align = kwargs.get("align", "left")
        self.font = pygame.font.Font(pygame.font.match_font(kwargs.get("font", "Arial")), kwargs.get("fontsize", 24))
        self.label = self.font.render(unicode(self.text), True, self.color)
        self.rect = self.label.get_rect()
    
    def set_value(self, value):
        self.val = self.font.render(unicode(self.form) % value, True, self.color)
        valrect = self.val.get_rect()
        labrect = self.label.get_rect()
        self.surface = pygame.Surface( (valrect.width + labrect.width, valrect.height + labrect.height) )
        self.rect = self.surface.get_rect()
        if self.align == "left":
            labrect.topleft = 0,0
            valrect.topleft = labrect.bottomleft
        else:
            labrect.topright = self.rect.topright
            valrect.topright = labrect.bottomright
        self.surface.fill((255,255,255))
        self.surface.set_colorkey((255,255,255))
        self.surface.blit(self.label, labrect)
        self.surface.blit(self.val, valrect)

    
    def render(self, surface):
        surface.blit(self.surface, self.rect)



def dist(a, b):
    xa, ya = a
    xb, yb = b
    return math.sqrt( (xa-xb)**2 + (ya-yb)**2 )

def scaleblit(dst, src, zoom, center_shift = (0, 0) ):
    w, h = src.get_rect().size
    w, h = int(w*zoom), int(h*zoom)
    rect = src.get_rect()
    rect.centerx += center_shift[0]
    rect.centery += center_shift[1]
    
    dst.blit(pygame.transform.scale(src, (w, h)), rect ) 

def main():
    size = 500, 500
    g_point = size[0]/2, size[0]/2
    bgcolor = 255, 255, 255
    planet_r = 50
    star_count = 100
    air_alt = 10

    parser = argparse.ArgumentParser(description=u"Simple sputnik emulator. Keys: UP, DOWN, LEFT, RIGHT -- start engine to corresponding direction; \"-\" -- zoom out; \"+\" -- zoom in")
    parser.add_argument("-p", "--prediction-depth", action="store", default=1000, type=int, help="Number of steps calculated while predicting the orbit. 1000 by default.") 

    parser.add_argument("-t", "--trace-depth", action="store", default=1000, type=int, help="Number of steps stored in orbit history. 1000 by default")

    parser.add_argument("-e", "--engine-power", action="store", default=0.01, type=float, help="Force of sputnik's engine. 0.01 by default")

    parser.add_argument("--tangent-speed", action="store", default=1.6, type=float, help="Initial tangent speed of sputnik. 1.6 by defaut")

    parser.add_argument("--normal-speed", action="store", default=0, type=float, help="Initial normal speed of sputnik. 0 by default.")

    parser.add_argument("-a", "--altitude", action="store", default=30, type=int, help="Initial altitude of sputnik. 30 by default")

    args = parser.parse_args()

    prediction_depth = args.prediction_depth

    history_depth = args.trace_depth

    ep = args.engine_power

    vx = args.tangent_speed
    vy = args.normal_speed
    alt = args.altitude

    pygame.init()

    alt_label = Label("Altitude:", "%.2f")
    speed_label = Label("Speed:", "%.2f", align="right")
    fps_label = Label("FPS:", "%.2f")

    screen = pygame.display.set_mode(size, pygame.DOUBLEBUF | pygame.HWSURFACE)
    pygame.display.set_caption(u"Sputnik")
    clock = pygame.time.Clock()

    sputnik1 = Sputnik((g_point[0],g_point[1]-planet_r-alt), g_point, (vx, vy), planet_r)

    sputnik2 = Sputnik((g_point[0], g_point[1]-planet_r-120), g_point, (1.1, 0), planet_r)

    trace = pygame.Surface(size)
    trace.fill((255,255,255))
    trace.set_colorkey((255,255,255))


    failfont = pygame.font.Font(pygame.font.match_font("Arial"), 24)
    faillabel = failfont.render(unicode("You will fail!"), True, (255, 0, 0))
    failrect = faillabel.get_rect()
    failrect.midbottom = screen.get_rect().midbottom

    pygame.draw.circle(trace, (0,0,255), g_point, planet_r)
    for _ in xrange(70):
        r = random.randrange(2, planet_r/4)
        dr = random.randrange(1, planet_r - r)
        vect = random.random()*2*math.pi
        x = int(g_point[0] + dr*math.cos(vect))
        y = int(g_point[1] + dr*math.sin(vect))
        pygame.draw.circle(trace, (0,255,0), (x, y), r)

    for i in xrange(air_alt):
        c = int(255/float(i+1))
        pygame.draw.circle(trace, (0,c,c), g_point, planet_r + i, 1)


    stars = pygame.Surface(size)
    stars.fill((0,0,0))
    for _ in xrange(star_count):
        center = random.randrange(1, size[0]), random.randrange(1, size[1])
        pygame.draw.circle(stars, (255,255,255), center, 1)


    sputniks = pygame.Surface(size)
    sputniks.set_colorkey((0,0,0))

    running = True
    zoom = 1.0
    d_zoom = 0.0

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit(0)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_MINUS:
                    d_zoom = -0.02
                elif event.key in [pygame.K_PLUS, pygame.K_EQUALS]:
                    d_zoom = 0.02
            elif event.type == pygame.KEYUP:
                if event.key in [pygame.K_PLUS, pygame.K_EQUALS, pygame.K_MINUS]:
                    d_zoom = 0.0
            sputnik1.process_event(event)
            
        fps = clock.get_fps()
        if not fps: fps = 100
        if running:
            sputnik1.step(50, prediction_depth, history_depth, ep)
            sputnik2.step(50, prediction_depth, history_depth, ep)
            if dist(sputnik1.point, g_point) <= planet_r:
                running = False
        if zoom > 0:
            zoom += d_zoom
        else:
            zoom = 0.02

        center = screen.get_rect().center
        fake_center = center[0]*float(zoom), center[1]*float(zoom)
        center_shift = center[0] - fake_center[0], center[1] - fake_center[1]

        sputnik1.center_shift = center_shift
        sputnik2.center_shift = center_shift
        sputnik1.zoom = zoom
        sputnik2.zoom = zoom

        screen.blit(stars, (0, 0))

        sputniks.fill((0,0,0))
        sputnik2.render(sputniks, (0,255,0))
        sputnik1.render(sputniks)
        scaleblit(screen, trace, zoom, center_shift)
        scaleblit(screen, sputniks, 1)

        if sputnik1.willfail:
            screen.blit(faillabel, failrect)


        alt_label.set_value(dist(sputnik1.point, g_point)-planet_r)
        alt_label.rect.topleft = 10,10
        alt_label.render(screen)
        
        speed_label.set_value(sputnik1.speed)
        speed_label.rect.topright = size[0] - 10, 10
        speed_label.render(screen)

        fps_label.set_value(fps)
        fps_label.rect.bottomleft = 10, size[1] - 10
        fps_label.render(screen)

        pygame.display.flip()
    #    clock.tick(1)

if __name__ == "__main__":
    main()