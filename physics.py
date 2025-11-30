import math as m
import pygame as pg
import numpy as np
import random as rndm # No, the collissions aren't random. It's for defaults.
import time
pg.init()
s_s = (400, 300)
screen = pg.display.set_mode(s_s, pg.RESIZABLE, pg.SRCALPHA)
pg.display.set_caption("Physics Simulation")
run = True

# classes
class ball: # for all ball objects
  """
  A ball! What else is there to say?

  Attributes
  ----------
  `pos`: a `pygame.Vector2` of the world position of the ball

  `vel`: a `pygame.Vector2` of the world velocity of the ball

  `r`: the radius of the ball in the world

  `fmass`: how heavy the ball is _(NOTE: This is fake mass. The real mass is the attribute `mass`.)_

  `rot`: the rotation of the ball

  `rotv`: the rotational velocity of the all

  `fric`: the ball's friction

  `color`: a length 3 `tuple` with values within the range `[0 ... 255]`. Is the color.

  Hidden Attributes
  -----------------
  `mass`: the true mass of the ball, calculated with `fmass * ((r ** 2) * m.pi)`.

  Flags
  -----
  `isvisible`: determines if the ball is rendered]

  `cancollideball`: determines if the ball collides with other balls

  `cancollideplane`: determines if the ball collide with planes

  `hasgravity`: is influenced by gravity
  """
  def __init__ (self,
    pos = None, vel = None, r = None, fmass = None,
    rot = 0, rotv = 0, fric = None, color = None,
    isvisible = True, cancollideball = True, cancollideplane = True, hasgravity = True):
    self.pos = pg.Vector2(rndm.uniform(-20, 20), rndm.uniform(-20, 20)) if pos == None else pg.Vector2(pos)
    self.vel = pg.Vector2(rndm.uniform(-20, 20), rndm.uniform(-20, 20)) if vel == None else pg.Vector2(vel)
    self.r = rndm.uniform(1.0, 20.0) if r == None else r
    self.rot = rot
    self.rotv = rotv
    self.fric = rndm.uniform(0.2, 5.0) if fric == None else fric
    self.color = pg.Color(rndm.randint(0, 255), rndm.randint(0, 255), rndm.randint(0, 255), a = 255) if color == None else color
    self.fmass = rndm.uniform(0.1, 20) if fmass == None else fmass
    self.mass = ((self.r ** 2) * m.pi) * self.fmass
    self.cancollideball = cancollideball
    self.cancollideplane = cancollideplane
    self.isvisible = isvisible
    self.hasgravity = hasgravity

  def __str__ (self):
    return("".join((
      "pos=(", str(self.pos),
      "), vel=(", str(self.vel),
      "), r=(", str(self.r),
      "), rot=(", str(self.rot),
      "), fmass=(", str(self.fmass),
      "), rotv=(", str(self.rotv),
      "), fric=(", str(self.fric),
      "), mass=(", str(self.mass),
      "),- color=(", str(self.color), ")")))

class plane: # for all plane objects
  """
  A plane for balls to collide with!

  Attributes
  ----------
  `pos`: a `pygame.Vetor2` representing the position of the plane relative to the world.

  `rot`: the angle in which the plane extends from (90° to the left is empty, and 90° to the right is filled.)

  `fric`: the friction of the plane, for collision.
  
  `color`: a length 3 `tuple` with values within the range `[0 ... 255]`. Is the color. 
  """
  def __init__ (self, pos, rot, fric, color,
  isvisible = True):
    self.pos = pg.Vector2(pos)
    self.rot = rot
    self.fric = fric
    self.color = color
    self.isvisible = isvisible
  def __str__(self):
    return("".join((
      "pos=(", str(self.pos),
      "), rot=(", str(self.rot),
      "), fric=(", str(self.fric),
      "),- color=(", str(self.color), ")")))

class spring: # for all spring objects
  def __init__ (self, ball_1, ball_2, length, stiff, damp, color):
    self.ball_1 = ball_1
    self.ball_2 = ball_2
    self.length = length
    self.stiff = stiff
    self.damp = damp
    self.color = color
  def __str__(self):
    return("".join((
      "ball_1=(", str(self.ball_1),
      "), ball_2=(", str(self.ball_2),
      "), length=(", str(self.length),
      "), stiff=(", str(self.stiff),
      "), damp=(", str(self.damp),
      "),- color=(", str(self.color), ")")))


def vec_rot(rot):
  return(pg.Vector2(m.cos(m.radians(rot)), m.sin(m.radians(rot))))

def my_dot(pos, rot):
  return(pos.dot(vec_rot(rot)))

def divinf(a, b):
  try:
    return(a / b)
  except:
    return(m.inf)

def scr_to_wrld(pos):
    global c_p, c_z, s_s2
    pos -= s_s2
    pos = pg.Vector2(pos.x, -pos.y) / c_z
    return(pos + c_p)

def wrld_to_scr(pos):
    global c_p, c_z, s_s2
    pos = (pos - c_p) * c_z
    pos = pg.Vector2(pos.x, -pos.y)
    return(pos + s_s2)

def draw_half_plane(display, plane):
  normal_x, normal_y = vec_rot(plane.rot)
  normal_vector = pg.Vector2(normal_x, normal_y)
  screen_width = display.get_width()
  screen_height = display.get_height()
  screen_corners = [pg.Vector2(0, 0), pg.Vector2(screen_width, 0), pg.Vector2(screen_width, screen_height), pg.Vector2(0, screen_height)]
  world_corners = [scr_to_wrld(corner) for corner in screen_corners]
  intersections = []
  solid_corners = []
  for i in range(4):
    p1 = world_corners[i]
    p2 = world_corners[(i + 1) % 4]
    side_p1 = (p1 - plane.pos).dot(normal_vector)
    side_p2 = (p2 - plane.pos).dot(normal_vector)
    if (side_p1 * side_p2) < 0:
      ratio = side_p1 / (side_p1 - side_p2)
      intersections.append(p1.lerp(p2, ratio))
    if side_p1 <= 0:
      if p1 not in solid_corners: solid_corners.append(p1)
  polygon_world = []
  if len(intersections) == 2:
    polygon_world.append(intersections[0])
    polygon_world.extend(solid_corners)
    polygon_world.append(intersections[1])
  if len(polygon_world) >= 3:
    polygon_screen = [wrld_to_scr(point) for point in polygon_world]
    pg.draw.polygon(display, plane.color, polygon_screen)
  corner_sides = [(corner - plane.pos).dot(normal_vector) for corner in world_corners]
  if all(side <= 0 for side in corner_sides):
    display.fill(plane.color)

def flip_y(pos):
  return(pg.Vector2(pos.x, -pos.y))

def spring_ball(spring = 0, mouse=False, target=-1, damp=0.1):
  global precision, balls, m_pos, c_p, c_z, gravity
  if mouse:
    ball_t = balls[target]
    L = ((ball_t.pos + (ball_t.vel / damp)) - (gravity)) - ((m_pos / c_z) + c_p)
    ball_t.vel -= ((L * damp) / precision)
  else:
    ball_1 = balls[spring.ball_1]
    ball_2 = balls[spring.ball_2]
    L = ball_1.pos - ball_2.pos
    if L.length() != 0:
      n = L.normalize()
      force = (-spring.stiff * (L.length() - spring.length)) + (-spring.damp * (ball_1.vel - ball_2.vel).dot(n))
      force *=  n
      ball_1.vel += (force / ball_1.mass) / precision
      ball_2.vel -= (force / ball_2.mass) / precision

# initialization

scroll = 0 # scroll. is event.y 
runtime = pg.time.Clock()

precision = 10 # ticks per second. does not influence gametime. (turning this up will make it laggier, though.)

# self explanatory physics stuff
air_res = 0.99
gravity = pg.Vector2(0, -1)
enrg_loss = 0.8

# set the stage
c_p = pg.Vector2(0, 0) # camera position
c_zr = 1 # real camera zoom

c_zp = m.sqrt(2) # zoom exponential value
c_zs = 0.01 # zoom scroll speed
c_ps = 0.95 # dragoff velocity slowdown
c_z = c_zp ** c_zr # real zoom
c_vel = pg.Vector2(0) # camera dragoff velocity
drag = 0 # dragging? (for drag)

stage_color = (100, 200, 255)
balls = []
planes = []
springs = []

# add elements HERE
balls.append(ball((5, 20), (0, 100), 5, 0.5, 0, 0, 0.5, (255, 128, 0)))
balls.append(ball((10, 100), (0, 0), 20, 1, 0, 0, 0.5, (0, 128, 255)))
balls.append(ball((100, 100), (0, 0), 5, 1, 0, 0, 0.5, (0, 128, 255)))
for i in range(0):
  time.sleep(0.01)
  balls.append(ball())
planes.append(plane((0, 0), 95, 0, (255, 0, 128)))
planes.append(plane((-100, 0), 0, 0, (255, 0, 0)))
springs.append(spring(0, 1, 200, 0.8, 0.8, (0, 0, 0)))
springs.append(spring(1, 2, 0, 0.99, 0.99, (0, 0, 0)))

while run:
  # initialize stuff
  delta = runtime.tick(60)
  s_s = pg.Vector2(screen.get_size())
  s_s2 = s_s/2
  screen.fill(stage_color)
  m_pos = flip_y(pg.Vector2(pg.mouse.get_pos()) - s_s2)

  # zoom
  opr = c_p + (m_pos / c_z)
  c_z = pg.math.lerp(c_z, (c_zp ** c_zr), min(c_zs * delta, 1))
  c_p = opr - (m_pos / c_z)

  for plane in planes:
    if plane.isvisible == True:
      draw_half_plane(screen, plane)
  
  # ball render
  for ball in balls:
    ball.mass = ((ball.r ** 2) * m.pi) * ball.fmass
    bfp = 1 + ball.fric

    for i in range(precision):
      ball.pos += ball.vel / precision
      if ball.cancollideplane:
        for plane in planes:
          plane_vec = vec_rot(plane.rot)
          dot = (ball.pos - plane.pos).dot(plane_vec) - ball.r
          if dot <= 0:
            ball.vel -= (bfp + plane.fric) * ball.vel.dot(plane_vec) * plane_vec
            ball.pos -= plane_vec * dot

      for hit_ball in balls:
        if ball == hit_ball or ball.cancollideball == False or hit_ball.cancollideball == False:
          continue
        d_vect = ball.pos - hit_ball.pos
        dist = d_vect.length() 
        radii_sum = ball.r + hit_ball.r
        overlap = radii_sum - dist
        if overlap > 0:
          if dist == 0:
            normal = pg.Vector2(0, 1) 
          else:
            normal = d_vect.normalize()
          ball.pos += normal * (overlap / 2) 
          hit_ball.pos -= normal * (overlap / 2)
          v_n = (ball.vel - hit_ball.vel).dot(normal)
          j = ((-(1 + enrg_loss) * v_n) / ((1 / ball.mass) + (1 / hit_ball.mass)))
          J = j * normal
          ball.vel += J / ball.mass 
          hit_ball.vel -= J / hit_ball.mass

      for spring in springs:
        spring_ball(spring)
      if drag > 0:
        spring_ball(mouse = True, target = drag, damp=0.1)
      if ball.hasgravity:
        ball.vel += gravity / precision
      ball.vel *= air_res ** (1 / precision)
    if ball.isvisible == True:
      pg.draw.circle(screen, ball.color, wrld_to_scr(ball.pos), ball.r * c_z)

  for spring in springs:
    pg.draw.line(screen, spring.color, wrld_to_scr(balls[spring.ball_1].pos), wrld_to_scr(balls[spring.ball_2].pos), 5)
  if drag > 0:
    t_screen = pg.Surface(s_s, pg.SRCALPHA)
    pg.draw.line(t_screen, pg.Color(255, 255, 255, 128), wrld_to_scr(balls[drag].pos), pg.mouse.get_pos(), 5)
    screen.blit(t_screen, (0, 0))

  pg.display.update()

  scroll = 0
  # events
  for event in pg.event.get():
    if event.type == pg.QUIT:
      run = False
    elif event.type == pg.MOUSEWHEEL:
      scroll = event.y
      c_zr += scroll

  # zoom drag
  if pg.mouse.get_pressed()[0]:
    if drag == 0:
      drag = -1
      for i, ball in enumerate(balls):
        if ((((m_pos / c_z) + c_p) - ball.pos).length()) - ball.r <= 0:
          drag = i
      pg.mouse.get_rel()
    else:
      if drag == -1:
        c_vel = flip_y(pg.Vector2(pg.mouse.get_rel()))
        c_p -= (c_vel / c_z)
  else:
    c_vel *= c_ps ** delta 
    c_p -= c_vel / c_z
    drag = 0
pg.quit()