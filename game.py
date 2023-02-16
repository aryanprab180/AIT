	import pygame
import time

from pygame.locals import*
from time import sleep

from abc import ABC, abstractmethod

class Model():
	def __init__(self):
		self.sprites = []
		self.mario = Mario()
		self.sprites.append(self.mario)
		
		self.sprites.append(Pipe(3, 130))
		self.sprites.append(Pipe(324, 266))
		self.sprites.append(Pipe(563, 318))
		self.sprites.append(Pipe(780, 246))
		self.sprites.append(Pipe(837, 80))
		self.sprites.append(Pipe(960, 182))
		self.sprites.append(Pipe(1070, 236))
		self.sprites.append(Pipe(1291, 157))
		self.sprites.append(Pipe(1368, 157))
		self.sprites.append(Pipe(1584, 263))
		self.sprites.append(Pipe(1655, 193))
		self.sprites.append(Pipe(1755, 132))
		self.sprites.append(Pipe(1934, 263))
		self.sprites.append(Pipe(2203, 136))
		self.sprites.append(Pipe(2335, 257))

		self.sprites.append(Goomba(392, 300))
		self.sprites.append(Goomba(1140, 300))
		self.sprites.append(Goomba(1503, 300))
		self.sprites.append(Goomba(2264, 300))

	def update(self):
		for collidee in self.sprites:
			collidee.setPrevy()
			collidee.update()
			
			for collider in self.sprites:
				if collider.Collision(collidee):
					collider.endCollision(collidee)
		
		index = 0
		while (index < len(self.sprites)):
			if (self.sprites[index].removable):
				self.sprites.pop(index)
				index -= 1
			
			index += 1


class View():
	scrollPos = 0

	def __init__(self, model):
		screen_size = (750, 475)
		self.screen = pygame.display.set_mode(screen_size, 32)
		self.model = model

	def update(self):
		View.scrollPos = self.model.mario.x - 65

		self.screen.fill([100, 225, 255])
		self.screen.fill([65, 215, 0], (0, 350, self.screen.get_width(), 25))
		self.screen.fill([90, 120, 0], (0, 350, self.screen.get_width(), 1))
		self.screen.fill([200, 125, 50], (0, 375, self.screen.get_width(), self.screen.get_height() - 375))

		for sprite in self.model.sprites:
			sprite.draw(self.screen)
		pygame.display.flip()
        

class Controller():
	def __init__(self, model):
		self.model = model
		self.keep_going = True
		self.holdCtrl = False

	def update(self):
		for event in pygame.event.get():
			if event.type == QUIT:
				self.keep_going = False
			elif event.type == KEYDOWN:
				if event.key == K_ESCAPE:
					self.keep_going = False
			elif event.type == KEYUP:
				if (event.key == K_LCTRL or event.key == K_RCTRL):
					self.holdCtrl = False
		
		keys = pygame.key.get_pressed()
		if (not keys[K_LEFT] and not keys[K_RIGHT] and self.model.mario.vertSpeed == 0):
			self.model.mario.pose = 0
		if keys[K_LEFT]:
			self.model.mario.x -= 10
			self.model.mario.animate()
		if keys[K_RIGHT]:
			self.model.mario.x += 10
			self.model.mario.animate()
		if keys[K_SPACE]:
			if (self.model.mario.airFrames < 5):
				self.model.mario.vertSpeed = -16
			if (not keys[K_LEFT] and not keys[K_RIGHT]):
				self.model.mario.animate()
		if ((keys[K_LCTRL] or keys[K_RCTRL]) and not self.holdCtrl):
			self.holdCtrl = True
			self.model.sprites.append(self.model.mario.fireball())


class Sprite(ABC):
	def __init__(self, x, y, w, h):
		self.x = x
		self.y = y
		self.w = w
		self.h = h
		self.removable = False

	@abstractmethod
	def setPrevy(self):
		pass
	@abstractmethod
	def update(self):
		pass
	@abstractmethod
	def Collision(self, spr):
		pass
	@abstractmethod
	def endCollision(self, spr):
		pass
	@abstractmethod
	def draw(self, screen):
		pass

	def isPipe(self):
		return False
	def isFireball(self):
		return False
	def isGoomba(self):
		return False


class Mario(Sprite):
	def __init__(self):
		Sprite.__init__(self, 65, 256, 60, 95)
		self.prevy = self.y
		self.pose = 0
		self.vertSpeed = 0
		self.airFrames = 0

		self.images = []
		for i in range(0, 8):
			self.images.append(pygame.image.load("mario" + str(i) + ".png"))

	def setPrevy(self):
		self.prevy = self.y

	def animate(self):
		if (self.pose == 7):
			self.pose = 1
		else:
			self.pose += 1

	def update(self):
		self.airFrames += 1
		self.vertSpeed += 0.98
		self.y += self.vertSpeed
		if (self.y >= 351 - self.h):
			self.airFrames = 0
			self.vertSpeed = 0
			self.y = 351 - self.h

	def Collision(self, pipe):
		if (pipe.isPipe()):
			if (self.x + self.w <= pipe.x + 5):
				return False
			if (self.x >= pipe.x + pipe.w - 5):
				return False
			if (self.y + self.h + 1 < pipe.y):
				return False
			if (self.y >= pipe.y + pipe.h):
				return False
			
			return True

		else:
			return False

	def endCollision(self, pipe):
		if (self.prevy > pipe.y + pipe.h):
			if (self.vertSpeed < 0.0):
				self.airFrames = 5
				self.vertSpeed = 0.0
			self.y = pipe.y + pipe.h

		elif (self.prevy + self.h - 1 > pipe.y):
			if (self.x < pipe.x):
				self.x = pipe.x - self.w + 5
			if (self.x + self.w > pipe.x + pipe.w):
				self.x = pipe.x + pipe.w - 5

		elif (self.y + self.h - 1 >= pipe.y):
			self.airFrames = 0
			self.vertSpeed = 0.0
			self.y = pipe.y - self.h + 1

	def fireball(self):
		fball = Fireball(self.x + self.w - 25, self.y + 10)
		return fball

	def draw(self, screen):
		screen.blit(self.images[self.pose], (self.x - View.scrollPos, self.y))


class Pipe(Sprite):
	def __init__(self, x, y):
		Sprite.__init__(self, x, y, 55, 400)

		self.image = pygame.image.load("pipe.png")

	def setPrevy(self):
		[]
	def update(self):
		[]

	def Collision(self, spr):
		return False

	def endCollision(self, spr):
		[]

	def draw(self, screen):
		screen.blit(self.image, (self.x - View.scrollPos, self.y))

	def isPipe(self):
		return True


class Goomba(Sprite):
	def __init__(self, x, y):
		Sprite.__init__(self, x, y, 41, 50)
		self.prevy = self.y
		self.vertSpeed = 0
		self.landed = False
		self.goingRight = False
		self.onFire = False
		self.fireFrames = 0

		self.images = []
		self.images.append(pygame.image.load("goomba.png"))
		self.images.append(pygame.image.load("goombaFire.png"))

	def setPrevy(self):
		self.prevy = self.y

	def update(self):
		if (self.landed and not self.onFire):
			if (self.goingRight):
				self.x += 5
			else:
				self.x -= 5

		self.vertSpeed += 0.98
		self.y += self.vertSpeed
		if (self.y >= 350 - self.h):
			self.vertSpeed = 0.0
			self.landed = True
			self.y = 350 - self.h

		if (self.onFire):
			self.fireFrames += 1
		if (self.fireFrames == 40):
			self.removable = True

	def Collision(self, spr):
		if (spr.isPipe() or spr.isFireball()):
			if (self.x + self.w <= spr.x):
				return False
			if (self.x >= spr.x + spr.w):
				return False
			if (self.y + self.h < spr.y):
				return False
			if (self.y >= spr.y + spr.h):
				return False

			return True

		else:
			return False

	def endCollision(self, spr):
		if (spr.isPipe()):
			if (self.prevy > spr.y + spr.h):
				if (self.vertSpeed < 0.0):
					self.vertSpeed = 0.0
				
				self.y = spr.y + spr.h
			
			elif (self.prevy + self.h > spr.y):
				self.goingRight = not self.goingRight
				if (self.x < spr.x):
					self.x = spr.x - self.w
				
				if (self.x + self.w > spr.x + spr.w):
					self.x = spr.x + spr.w	
			
			elif (self.y + self.h >= spr.y):
				self.vertSpeed = 0.0
				self.y = spr.y - self.h
				self.landed = True

		if (spr.isFireball()):
			self.onFire = True

	def draw(self, screen):
		if (not self.onFire):
			screen.blit(self.images[0], (self.x - View.scrollPos, self.y))
		else:
			screen.blit(self.images[1], (self.x - View.scrollPos, self.y))

	def isGoomba(self):
		return True


class Fireball(Sprite):
	def __init__(self, x, y):
		Sprite.__init__(self, x, y, 47, 47)
		self.horSpeed = 15
		self.vertSpeed = -5
		self.screenFrames = 0

		self.image = pygame.image.load("fireball.png")

	def setPrevy(self):
		[]

	def update(self):
		self.vertSpeed += 0.98
		self.y += self.vertSpeed
		if (self.y >= 350 - self.h):
			self.vertSpeed = -0.75*self.vertSpeed
			self.y = 350 - self.h

		self.x += self.horSpeed
		if (self.screenFrames == 75):
			self.removable = True
		
		self.screenFrames += 1

	def Collision(self, goom):
		if (goom.isGoomba()):
			if (self.x + self.w <= goom.x):
				return False
			
			if (self.x >= goom.x + goom.w):
				return False
			
			if (self.y + self.h < goom.y):
				return False
			
			if (self.y >= goom.y + goom.h):
				return False
			
			return True
		
		else:
			return False

	def endCollision(self, goom):
		self.removable = True

	def draw(self, screen):
		screen.blit(self.image, (self.x - View.scrollPos, self.y))

	def isFireball(self):
		return True


print("Use the left and right keys to run, space to jump, and control to throw fireballs. " +
		"Press Esc to quit.")
pygame.init()
m = Model()
v = View(m)
c = Controller(m)
while c.keep_going:
	c.update()
	m.update()
	v.update()
	sleep(0.04)
print("Goodbye")