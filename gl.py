'''
    Diana Ximena de León Figueroa
    Carne 18607
    Laboratorio 2 - Shaders
    Graficas por Computadora
    04 de agosto de 2020
'''

from lib import Render
from utils import V2, V3

bitmap = Render()


def glInit(self):
    pass


def glCreateWindow(width, height):
    bitmap.createWindow(width, height)


def glViewport(x, y, width, height):
    bitmap.viewport(x, y, width, height)


def glClear():
    bitmap.clear()


def glClearColor(r, g, b):
    r = round(r * 255)
    g = round(g * 255)
    b = round(b * 255)
    bitmap.clearColor(r, g, b)


def glColor(r, g, b):
    r = round(r * 255)
    g = round(g * 255)
    b = round(b * 255)
    bitmap.setColor(r, g, b)


def glVertex(x, y):
    X = bitmap.getCordX(x)
    Y = bitmap.getCordY(y)
    bitmap.vertex(X, Y)


def glPoint(x, y):
    X = bitmap.getCordX(x)
    Y = bitmap.getCordY(y)
    bitmap.point(X, Y)


def glLine(x0, y0, x1, y1):
    x0 = bitmap.getCordX(x0)
    y0 = bitmap.getCordY(y0)
    x1 = bitmap.getCordX(x1)
    y1 = bitmap.getCordY(y1)
    bitmap.line(x0, y0, x1, y1)


def glLoad(filename, translate, scale):
    bitmap.load(filename, translate, scale)


def glFinish(filename='out.bmp'):
    bitmap.write(filename)


glCreateWindow(1000, 1000)
glClear()

glLoad('./sphere.obj', V3(500, 500, 0), V3(500, 500, 200))
glFinish('sphere.bmp')
