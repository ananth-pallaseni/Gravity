""" Gravity """

import tkinter as tk
import sys
import random
import math

#GRAV_CONSTANT = 500000
GRAV_CONSTANT = 1
BH_CONSTANT = 10
PARTICLE_CONSTANT = 2

MAX_NUM_BH = 10
MAX_NUM_PARTICLES = 100

FRAMES_PER_SECOND = 30
MILLISECONDS_PER_FRAME = 33

DEFAULT_WINDOW_WIDTH = 1000
DEFAULT_WINDOW_HEIGHT = 600

REAL_BG_COLOR = "#003d3d"
COLOR_CYCLE_VALUE = 0
COLOR_CHOICES = ["green",
				 "blue",
				 "cyan",
				 "yellow",
				 "rosy brown",
				 "dark orange",
				 "hot pink",
				 "magenta",
				 "dark violet",
				 "medium purple",
				 "bisque2"]

"""
TODO:
- Fix distance scaling in force function
- Ability to have black holes interfere with each other (black holes are movable and can devour each other)
"""



class Gravity(object):
	"""Main game obect. Manages state, calculations and drawing"""
	def __init__(self):
		# Object Tracking
		self.particles = []
		self.blackHoles = []
		self.bhArtId = []
		self.particleId = []
		self.arrowId = []
		self.canvas = Canvas(self)
		self.arrows = False
		self.trace = False
		self.trails = True

	def addBlackHole(self, pos=(0,0)):
		self.blackHoles.append(BlackHole(1, pos))

	def addParticle(self, pos=(0,0), vel=(0,0)):
		self.particles.append(Particle(1, pos, vel))

	def physics(self):
		color = 0
		for p in self.particles:
			totalAcc = (0, 0)
			# Sum acceleration from each black hole:
			for bh in self.blackHoles:
				dist = minus(bh.pos, p.pos)
				direction = unit(dist)
				f = force(bh, p, dist)
				totalAcc = plus(totalAcc, times(f, direction))

			# Calculate new velocity
			p.velocity = plus(p.velocity, totalAcc)

			# Calculate new position
			newPos = plus(p.pos, p.velocity)

			# Color Trace:
			if self.trace:
				self.canvas._canvas.create_line(p.pos[0], p.pos[1], newPos[0], newPos[1], fill=COLOR_CHOICES[color])

			# Trails:
			if self.trails:
				self.canvas._canvas.create_line(p.pos[0], p.pos[1], newPos[0], newPos[1], fill=COLOR_CHOICES[color])

			# Increment Color Choice
			color += 1
			if color == len(COLOR_CHOICES):
				color = 0

			# Move particle
			p.move(newPos)

			# Arrows:
			if self.arrows:
				self.canvas.canvasClear(self.arrowId)
				self.arrowId = self.arrowDebug()


	def drawClearLabel(self):
		cl = tk.Label(self.canvas._tk, text="Clear")
		cl.bind("<Button-1>", self._clOnClick)
		cl.pack()

	def drawArrowLabel(self):
		al = tk.Label(self.canvas._tk, text="Toggle Arrows")
		al.bind("<Button-1>", self._alOnClick)
		al.pack()

	def drawTraceLabel(self):
		tl = tk.Label(self.canvas._tk, text="Toggle Trace")
		tl.bind("<Button-1>", self._tlOnClick)
		tl.pack()


	def arrowDebug(self):
		arrowArray = []
		for p in self.particles:
			for bh in self.blackHoles:
				arrowArray.append(self.canvas._canvas.create_line(p.pos[0], p.pos[1], bh.pos[0], bh.pos[1], fill="red", arrow=tk.LAST))
		return arrowArray

	def start(self):
		self.canvas.drawParticleLabel()
		self.drawClearLabel()
		self.drawArrowLabel()
		self.drawTraceLabel()
		self.canvas._tk.after(MILLISECONDS_PER_FRAME, self.update)
		self.canvas._tk.mainloop()

	def draw(self):
		self.bhArtId = []
		self.particleId = []
		color = 0
		for bh in self.blackHoles:
			self.bhArtId.append(self.canvas.drawBlackHole(bh))
		for p in self.particles:
			self.particleId.append(self.canvas.drawParticle(p, COLOR_CHOICES[color]))
			color += 1
			if color == len(COLOR_CHOICES):
				color = 0

	def update(self):
		if self.trace:
			self.canvas.canvasClear(self.bhArtId)
			self.canvas.canvasClear(self.particleId)
		else:
			self.canvas._canvas.delete(tk.ALL)
		self.physics()
		self.draw()
		self.canvas._tk.after(MILLISECONDS_PER_FRAME, self.update)

	def _clOnClick(self, event):
		self.particles = []
		self.blackHoles = []
		self.traceParticles = []
		self.canvas._canvas.delete(tk.ALL)

	def _alOnClick(self, event):
		self.arrows = not self.arrows
		self.canvas.canvasClear(self.arrowId)

	def _tlOnClick(self, event):
		self.trace = not self.trace


		

class Canvas(object):
	"""Simple Canvas object for drawing calls. Also serves as the background for the game"""
	def __init__(self, parent, title='', width=DEFAULT_WINDOW_WIDTH, height=DEFAULT_WINDOW_HEIGHT, color="white"):
		# Attributes:
		self.parent = parent
		self.width = width
		self.height = height

		# Object Tracking
		self.particles = []
		self.blackHoles = []

		# Root Window:
		self._tk = tk.Tk()
		#self._tk.protocol('WM_DELETE_WINDOW', sys.exit)
		self._tk.title(title or "Gravity")

		# Canvas
		self._canvas = tk.Canvas(self._tk, width=width, height=height, bg=color)
		self._canvas.bind("<Button-1>", self._onClick)
		self._canvas.pack() 



		###################################
		
		###################################


	def draw_circle(self, center, radius, lineColor='White', lineWidth=1, filled=1, fillColor="Black"):
		""" Draw a circle with specified radius at center. Returns its tkinter id"""
		if filled == 0:
			fillColor = ""

		x0 = center[0] - radius
		y0 = center[1] - radius
		x1 = center[0] + radius
		y1 = center[1] + radius
		return self._canvas.create_oval(x0, y0, x1, y1, outline=lineColor, fill=fillColor, width=lineWidth)

	def drawBlackHole(self, bh):
		return self.draw_circle(bh.pos, bh.size * BH_CONSTANT, 'White', 1, 1, "Black")

	def drawParticle(self, p, color="White"):
		return self.draw_circle(p.pos, p.size * PARTICLE_CONSTANT, "Black", 1, 1, color)

	def drawParticleLabel(self):
		l = tk.Label(self._tk, text="Add a particle")
		l.bind("<Button-1>", self._plabelOnClick)
		l.pack()
		return l


	def _onClick(self, event):
		if len(self.parent.blackHoles) <= MAX_NUM_BH:
			self.parent.addBlackHole((event.x, event.y))

	def _plabelOnClick(self, event):
		if len(self.parent.particles) <= MAX_NUM_PARTICLES:
			pos, vel = self.wallHug()
			self.parent.addParticle(pos, vel)

	def wallHug(self):
		# 0: top, 1: right, 2: bottom, 3: left
		wall = random.randrange(4)
		px = 0
		py = 0
		vx = 0
		vy = 0
		if wall == 0:
			px = random.randrange(self.width)
			py = self.height
			vx = random.randrange(-self.width/50, self.width/50)
			vy = random.randrange(-self.height/50, 0)
		elif wall == 1:
			px = self.width
			py = random.randrange(self.height)
			vx = random.randrange(-self.width/50, 0)
			vy = random.randrange(-self.height/50, self.height/50)
		elif wall == 2:
			px = random.randrange(self.width)
			py = 0
			vx = random.randrange(-self.width/50, self.width/50)
			vy = random.randrange(self.height/50)
		else:
			px = 0
			py = random.randrange(self.height)
			vx = random.randrange(self.width/50)
			vy = random.randrange(-self.height/50, self.height/50)
		return (px, py), (vx, vy)

	def canvasClear(self, arr):
		for x in arr:
			self._canvas.delete(x)




class Movable(object):
	"""docstring for Movable"""
	def __init__(self, size=1, pos=(0,0), vel=(0,0), isMovable=False):
		super(Movable, self).__init__()
		self.size = 1
		self.pos = pos
		self.velocity = vel
		self.isMovable=isMovable

	def move(self, newPos):
		if self.isMovable:
			self.pos = newPos



		
class BlackHole(Movable):
	"""docstring for BlackHole"""
	def __init__(self, size=1, pos=(0,0)):
		super(BlackHole, self).__init__(size, pos, (0,0), False)
		self.sizeTimesGrav = self.size * GRAV_CONSTANT

	def strength(self, particleMass=1, distance=1):
		""" F = mMG / r^2"""
		return particleMass * self.sizeTimesGrav / (distance * distance)

	def toggleMoveable(self):
		self.isMovable = not self.isMovable

	def incrementSize(self):
		self.size += 1
		self.sizeTimesGrav = self.size * GRAV_CONSTANT

	def _onClick(self):
		self.incrementSize()

class Particle(Movable):
	"""docstring for Particle"""
	def __init__(self, size=1, pos=(0,0), vel=(0,0)):
		super(Particle, self).__init__(size, pos, vel, True)

		
def force(bh, p, dist):
	scalarDist = mag(dist)
	if scalarDist == 0:
		scalarDist = 0.01
	return p.size * bh.sizeTimesGrav #/ (scalarDist * scalarDist)

def minus(a, b):
	return (a[0] - b[0], a[1] - b[1])

def plus(a, b):
	return (a[0] + b[0], a[1] + b[1])

def dot(a, b):
	return (a[0]*b[0], a[1]*b[1])

def times(scalar, vector):
	return (scalar * vector[0], scalar * vector[1])

def unit(a):
	s = mag(a)
	return (a[0] / s, a[1] / s)

def mag(a):
	return math.sqrt(a[0]*a[0] + a[1]*a[1])

def colorCycle():
	global COLOR_CYCLE_VALUE
	if COLOR_CYCLE_VALUE > 2:
		COLOR_CYCLE_VALUE = 0

if __name__  == "__main__":
	g = Gravity()
	g.start()