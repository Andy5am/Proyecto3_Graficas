import pygame
from math import pi, cos, sin, atan2


BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BACKGROUND = (0, 255, 255)


wall1 = pygame.image.load('./minecraftStone.png')
wall2 = pygame.image.load('./minecraftWood.png')
wall3 = pygame.image.load('./diamond.png')
wall4 = pygame.image.load('./lava.png')
wall5 = pygame.image.load('./water.png')

textures = {
  "1": wall1,
  "2": wall2,
  "3": wall3,
  "4": wall4,
  "5": wall5,
}

hand = pygame.image.load('./stevehand.png')

item = pygame.image.load('./player.png')

enemies = [
  {
    "x": 100,
    "y": 200,
    "texture": pygame.image.load('./enemy.png')
  },
  {
    "x": 280,
    "y": 190,
    "texture": pygame.image.load('./enemy.png')
  },
  {
    "x": 225,
    "y": 340,
    "texture": pygame.image.load('./enemy.png')
  },
  {
    "x": 220,
    "y": 425,
    "texture": pygame.image.load('./enemy.png')
  },
  {
    "x": 425,
    "y": 275,
    "texture": pygame.image.load('./diamante.png')
  }
]

class Raycaster(object):
  def __init__(self, screen):
    _, _, self.width, self.height = screen.get_rect()
    self.screen = screen
    self.blocksize = 50
    self.player = {
      "x": self.blocksize + 20,
      "y": self.blocksize + 20,
      "a": 0,
      "fov": pi/3
    }
    self.map = []
    self.zbuffer = [-float('inf') for z in range(0, 500)]
    # self.clear()

  def clear(self):
    for x in range(self.width):
      for y in range(self.height):
        r = int((x/self.width)*255) if x/self.width < 1 else 1
        g = int((y/self.height)*255) if y/self.height < 1 else 1
        b = 0
        color = (r, g, b)
        self.point(x, y, color)

  def point(self, x, y, c = None):
    screen.set_at((x, y), c)

  def draw_rectangle(self, x, y, texture):
    for cx in range(x, x + 50):
      for cy in range(y, y + 50):
        tx = int((cx - x)*173 / 50)
        ty = int((cy - y)*173 / 50)
        c = texture.get_at((tx, ty))
        self.point(cx, cy, c)

  def load_map(self, filename):
    with open(filename) as f:
      for line in f.readlines():
        self.map.append(list(line))

  def cast_ray(self, a):
    d = 0
    while True:
      x = self.player["x"] + d*cos(a)
      y = self.player["y"] + d*sin(a)

      i = int(x/50)
      j = int(y/50)

      if self.map[j][i] != ' ':
        hitx = x - i*50
        hity = y - j*50

        if 1 < hitx < 49:
          maxhit = hitx
        else:
          maxhit = hity

        tx = int(maxhit * 173 / 50)

        return d, self.map[j][i], tx

      self.point(int(x), int(y), (255, 255, 255))

      d += 1

  def draw_stake(self, x, h, texture, tx):
    start = int(250 - h/2)
    end = int(250 + h/2)
    for y in range(start, end):
      ty = int(((y - start)*173)/(end - start))
      c = texture.get_at((tx, ty))
      self.point(x, y, c)

  def draw_sprite(self, sprite):
    sprite_a = atan2(sprite["y"] - self.player["y"], sprite["x"] - self.player["x"])

    sprite_d = ((self.player["x"] - sprite["x"])**2 + (self.player["y"] - sprite["y"])**2)**0.5
    sprite_size = (500/sprite_d) * 70

    sprite_x = 500 + (sprite_a - self.player["a"])*500/self.player["fov"] + 250 - sprite_size/2
    sprite_y = 250 - sprite_size/2

    sprite_x = int(sprite_x)
    sprite_y = int(sprite_y)
    sprite_size = int(sprite_size)

    for x in range(sprite_x, sprite_x + sprite_size):
      for y in range(sprite_y, sprite_y + sprite_size):
        if 500 < x < 1000 and self.zbuffer[x - 500] >= sprite_d:
          tx = int((x - sprite_x) * 128/sprite_size)
          ty = int((y - sprite_y) * 128/sprite_size)
          c = sprite["texture"].get_at((tx, ty))
          if c != (152, 0, 136, 255):
            self.point(x, y, c)
            self.zbuffer[x - 500] = sprite_d

  def draw_player(self, xi, yi, w = 100, h = 100):
    for x in range(xi, xi + w):
      for y in range(yi, yi + h):
        tx = int((x - xi) * 32/w)
        ty = int((y - yi) * 32/h)
        c = hand.get_at((tx, ty))
        if c != (152, 0, 136, 255):
          self.point(x, y, c)

  def draw_item(self, xi, yi, w = 200, h = 200):
    for x in range(xi, xi + w):
      for y in range(yi, yi + h):
        tx = int((x - xi) * 32/w)
        ty = int((y - yi) * 32/h)
        c = item.get_at((tx, ty))
        if c != (152, 0, 136, 255):
          self.point(x, y, c)

  def render(self):
    for x in range(0, 500, 50):
      for y in range(0, 500, 50):
        i = int(x/50)
        j = int(y/50)
        if self.map[j][i] != ' ':
          self.draw_rectangle(x, y, textures[self.map[j][i]])

    self.point(self.player["x"], self.player["y"], (255, 255, 255))

    for i in range(0, 500):
      self.point(500, i, (0, 0, 0))
      self.point(501, i, (0, 0, 0))
      self.point(499, i, (0, 0, 0))

    for i in range(0, 500):
      a =  self.player["a"] - self.player["fov"]/2 + self.player["fov"]*i/500
      d, c, tx = self.cast_ray(a)
      x = 500 + i
      h = 500/(d*cos(a-self.player["a"])) * 70
      self.draw_stake(x, h, textures[c], tx)
      self.zbuffer[i] = d

    for enemy in enemies:
      self.point(enemy["x"], enemy["y"], (0, 0, 0))
      self.draw_sprite(enemy)

    self.draw_player(1000
     - 50 - 128, 500 - 100)
    self.draw_item(1000-300-128,500-200)



pygame.init()
sound = pygame.mixer.Sound("./footsteps.wav")


def text_objects(text, font):
  textSurface = font.render(text, True, (0,0,0))
  return textSurface, textSurface.get_rect()

def button(msg,x,y,w,h,ic,ac, action=None):
  mouse = pygame.mouse.get_pos()
  click = pygame.mouse.get_pressed()
  print(click)
  if x+w > mouse[0] > x and y+h > mouse[1] > y:
      pygame.draw.rect(screen, ac,(x,y,w,h))

      if click[0] == 1 and action != None:
        if action == 'play':
          game()
        elif action == 'quit':
          pygame.quit()
          quit()

  else:
      pygame.draw.rect(screen, ic,(x,y,w,h))

  smallText = pygame.font.Font("freesansbold.ttf",20)
  textSurf, textRect = text_objects(msg, smallText)
  textRect.center = ( (x+(w/2)), (y+(h/2)) )
  screen.blit(textSurf, textRect)
    

screen = pygame.display.set_mode((1000, 500))
screen.set_alpha(None)
r = Raycaster(screen)
r.load_map('./map.txt')

def gameWin():
  intro = True

  while intro:
    for event in pygame.event.get():
      if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
        pygame.quit()
        quit()

    screen.fill((0,0,255))
    largeText = pygame.font.Font('freesansbold.ttf', 115)
    TextSurf, TextRect = text_objects('Ganaste', largeText)
    TextRect.center = ((1000/2),(500/2))
    screen.blit(TextSurf, TextRect)

    button('Quit',450,400,100,50,(255,0,0),(200,0,0),'quit')

    pygame.display.update()

def gameIntro():
  intro = True

  while intro:
    for event in pygame.event.get():
      if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
        pygame.quit()
        quit()

    screen.fill((0,0,255))
    largeText = pygame.font.Font('freesansbold.ttf', 115)
    TextSurf, TextRect = text_objects('Wolfencraft', largeText)
    TextRect.center = ((1000/2),(100))
    screen.blit(TextSurf, TextRect)

    largeText = pygame.font.Font('freesansbold.ttf', 60)
    TextSurf, TextRect = text_objects('Encuentra el diamante', largeText)
    TextRect.center = ((1000/2),(250))
    screen.blit(TextSurf, TextRect)

    button('Start',450,400,100,50,(0,255,0),(0,200,0),'play')

    pygame.display.update()

def game():
  c = 0
  jugar = True
  pygame.mixer.music.load('./minecraftMusic.mp3')
  pygame.mixer.music.play(-1)
  while jugar:
    
    print(pygame.mouse.get_pos())
    screen.fill((113, 113, 113))
    r.render()

    for e in pygame.event.get():
      if e.type == pygame.QUIT or (e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE):
        exit(0)
      if e.type == pygame.KEYDOWN:
        if e.key == pygame.K_a:
          r.player["a"] -= pi/10
        elif e.key == pygame.K_d:
          r.player["a"] += pi/10

        elif e.key == pygame.K_RIGHT:
          r.player["x"] += 10
          pygame.mixer.Sound.play(sound)
        elif e.key == pygame.K_LEFT:
          r.player["x"] -= 10
          pygame.mixer.Sound.play(sound)
        elif e.key == pygame.K_UP:
          r.player["y"] -= 10
          pygame.mixer.Sound.play(sound)
        elif e.key == pygame.K_DOWN:
          r.player["y"] += 10
          pygame.mixer.Sound.play(sound)

        if e.key == pygame.K_f:
          if screen.get_flags() and pygame.FULLSCREEN:
              pygame.display.set_mode((1000, 500))
          else:
              pygame.display.set_mode((1000, 500),  pygame.DOUBLEBUF|pygame.HWACCEL|pygame.FULLSCREEN)
      if r.player['x'] > 398 and r.player['x'] < 451 and r.player['y'] > 252 and r.player['y'] < 298:
        print('ganaste')
        gameWin()

    pygame.display.flip()

gameIntro()
