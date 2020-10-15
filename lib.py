'''
    Diana Ximena de León Figueroa
    Carne 18607
    Laboratorio 2 - Shaders
    Graficas por Computadora
    04 de agosto de 2020
'''

from utils import *
from obj import Obj
import random
import math

'''
    ****************************************
'''
BLACK = color(0, 0, 0)
WHITE = color(255, 255, 255)

'''
    ****************************************
'''


class Render(object):
    def __init__(self):
        self.framebuffer = []
        self.zbuffer = []
        self.color = WHITE
        self.activeShader = 'TIERRA'

    def createWindow(self, width, height):
        self.width = width
        self.height = height

    def point(self, x, y, selectColor=None):
        try:
            self.framebuffer[y][x] = selectColor or self.color
        except:
            pass

    def viewport(self, x, y, width, height):
        self.xViewPort = x
        self.yViewPort = y
        self.viewPortWidth = width
        self.viewPortHeight = height

    def clear(self):
        self.framebuffer = [
            [BLACK for x in range(self.width)]
            for y in range(self.height)
        ]

        self.zbuffer = [
            [-float('inf') for x in range(self.width)]
            for y in range(self.height)
        ]

    def clearColor(self, r, g, b):
        newColor = color(r, g, b)
        self.framebuffer = [
            [newColor for x in range(self.width)]
            for y in range(self.height)
        ]

    def setColor(self, r, g, b):
        self.color = color(r, g, b)

    def getCordX(self, x):
        return round((x+1) * (self.viewPortWidth/2) + self.xViewPort)

    def getCordY(self, y):
        return round((y+1) * (self.viewPortHeight/2) + self.yViewPort)

    def vertex(self, x, y):
        self.point(x, y)

    def line(self, x0, y0, x1, y1):
        dy = abs(y1 - y0)
        dx = abs(x1 - x0)

        steep = dy > dx

        if steep:
            x0, y0 = y0, x0
            x1, y1 = y1, x1

        if x0 > x1:
            x0, x1 = x1, x0
            y0, y1 = y1, y0

        dy = abs(y1 - y0)
        dx = abs(x1 - x0)

        offset = 0
        threshold = dx
        y = y0
        inc = 1 if y1 > y0 else -1

        for x in range(x0, x1):
            if steep:
                self.point(y, x)

            else:
                self.point(x, y)

            offset += 2 * dy
            if offset >= threshold:
                y += inc
                threshold += 2 * dx

    def triangle1(self, A, B, C, selectColor=None):
        if y > B.y:
            A, B = B, A
        if y > C.y:
            A, C = C, A
        if B.y > C.y:
            B, C = C, B

        dx_ac = C.x - x
        dy_ac = C.y - y

        if dy_ac == 0:
            return

        mi_ac = dx_ac/dy_ac

        dx_ab = B.x - x
        dy_ab = B.y - y

        if dy_ab != 0:
            mi_ab = dx_ab/dy_ab

            for y in range(y, B.y + 1):
                xi = round(x - mi_ac * (y - y))
                xf = round(x - mi_ab * (y - y))

                if xi > xf:
                    xi, xf = xf, xi
                for x in range(xi, xf + 1):
                    self.point(x, y, selectColor)

        dx_bc = C.x - B.x
        dy_bc = C.y - B.y

        if dy_bc:

            mi_bc = dx_bc/dy_bc

            for y in range(B.y, C.y + 1):
                xi = round(x - mi_ac * (y - y))
                xf = round(B.x - mi_bc * (B.y - y))

                if xi > xf:
                    xi, xf = xf, xi
                for x in range(xi, xf + 1):
                    self.point(x, y, selectColor)

    def triangle2(self, A, B, C, selectColor):
        xMin, xMax, yMin, yMax = bbox(A, B, C)
        for x in range(xMin, xMax + 1):
            for y in range(yMin, yMax + 1):
                P = V2(x, y)
                w, v, u = barycentric(A, B, C, P)
                if w < 0 or v < 0 or u < 0:
                    continue

                z = A.z * w + B.z * u + C.z * v

                try:
                    if z > self.zbuffer[x][y]:
                        self.point(x, y, selectColor)
                        self.zbuffer[x][y] = z
                except:
                    pass

    def triangle(self, A, B, C):
        xMin, xMax, yMin, yMax = bbox(A, B, C)
        for x in range(xMin, xMax + 1):
            for y in range(yMin, yMax + 1):
                P = V2(x, y)
                w, v, u = barycentric(A, B, C, P)
                if w < 0 or v < 0 or u < 0:
                    continue

                z = A.z * w + B.z * u + C.z * v

                '''
                if self.activeShader == 'TIERRA':
                    color1, color2, color3 = self.shadersTierra(x, y, intensity)
                else:
                    color1, color2, color3 = self.shadersLuna(x, y, intensity)

                pColorR = round(color1[0] * w + color1[1] * u + color1[2] * v)
                pColorG = round(color2[0] * w + color2[1] * u + color2[2] * v)
                pColorB = round(color3[0] * w + color3[1] * u + color3[2] * v)

                selectColor = color(pColorR, pColorG, pColorB)
                '''

                selectColor = self.nuevoShader(x, y)

                try:
                    if z > self.zbuffer[x][y]:
                        self.point(x, y, selectColor)
                        self.zbuffer[x][y] = z
                except:
                    pass

    def load(self, filename, translate, scale):
        model = Obj(filename)

        for face in model.faces:
            vcount = len(face)

            if vcount == 3:
                f1 = face[0][0] - 1
                f2 = face[1][0] - 1
                f3 = face[2][0] - 1

                v1 = V3(model.vertices[f1][0],
                        model.vertices[f1][1], model.vertices[f1][2])
                v2 = V3(model.vertices[f2][0],
                        model.vertices[f2][1], model.vertices[f2][2])
                v3 = V3(model.vertices[f3][0],
                        model.vertices[f3][1], model.vertices[f3][2])

                x1 = round((v1.x * scale.x) + translate.x)
                y1 = round((v1.y * scale.y) + translate.y)
                z1 = round((v1.z * scale.z) + translate.z)

                x2 = round((v2.x * scale.x) + translate.x)
                y2 = round((v2.y * scale.y) + translate.y)
                z2 = round((v2.z * scale.z) + translate.z)

                x3 = round((v3.x * scale.x) + translate.x)
                y3 = round((v3.y * scale.y) + translate.y)
                z3 = round((v3.z * scale.z) + translate.z)

                A = V3(x1, y1, z1)
                B = V3(x2, y2, z2)
                C = V3(x3, y3, z3)

                self.triangle(A, B, C)

            else:
                f1 = face[0][0] - 1
                f2 = face[1][0] - 1
                f3 = face[2][0] - 1
                f4 = face[3][0] - 1

                v1 = V3(model.vertices[f1][0],
                        model.vertices[f1][1], model.vertices[f1][2])
                v2 = V3(model.vertices[f2][0],
                        model.vertices[f2][1], model.vertices[f2][2])
                v3 = V3(model.vertices[f3][0],
                        model.vertices[f3][1], model.vertices[f3][2])
                v4 = V3(model.vertices[f4][0],
                        model.vertices[f4][1], model.vertices[f4][2])

                x1 = round((v1.x * scale.x) + translate.x)
                y1 = round((v1.y * scale.y) + translate.y)
                z1 = round((v1.z * scale.z) + translate.z)

                x2 = round((v2.x * scale.x) + translate.x)
                y2 = round((v2.y * scale.y) + translate.y)
                z2 = round((v2.z * scale.z) + translate.z)

                x3 = round((v3.x * scale.x) + translate.x)
                y3 = round((v3.y * scale.y) + translate.y)
                z3 = round((v3.z * scale.z) + translate.z)

                x4 = round((v4.x * scale.x) + translate.x)
                y4 = round((v4.y * scale.y) + translate.y)
                z4 = round((v4.z * scale.z) + translate.z)

                A = V3(x1, y1, z1)
                B = V3(x2, y2, z2)
                C = V3(x3, y3, z3)
                D = V3(x4, y4, z4)

                self.triangle(A, B, C)

                self.triangle(A, D, C)

    def write(self, filename='out.bmp'):
        f = open(filename, 'bw')

        f.write(char('B'))
        f.write(char('M'))
        f.write(dword(14 + 40 + self.width * self.height * 3))
        f.write(dword(0))
        f.write(dword(14 + 40))

        # image header
        f.write(dword(40))
        f.write(dword(self.width))
        f.write(dword(self.height))
        f.write(word(1))
        f.write(word(24))
        f.write(dword(0))
        f.write(dword(self.width * self.height * 3))
        f.write(dword(0))
        f.write(dword(0))
        f.write(dword(0))
        f.write(dword(0))

        # pixel data
        for x in range(self.height):
            for y in range(self.width):
                f.write(self.framebuffer[x][y])

        f.close()

    def nuevoShader(self, x, y):
        COLOR_1 = 115, 80, 50
        COLOR_4 = 165, 130, 100
        intensity = 0.5
        if self.activeShader == 'LUNA':
            COLOR_1 = 80, 60, 50
            COLOR_4 = 124, 115, 95
            intensity = 0.3

        r1, g1, b1 = COLOR_1
        r2, g2, b2, = COLOR_4

        dc = 0
        
        if y >= 375 and y <= 425:
            r1, g1, b1 = COLOR_1
            r2, g2, b2 = COLOR_4
            dc = abs(y - 400)
        elif y < 450 or y > 350:
            r1, g1, b1 = COLOR_1
            r2, g2, b2 = COLOR_4
            dc = abs(y - 400)
        
        dc = dc / 50
        r = round(r1 + dc * (r2 - r1) * intensity)
        g = round(g1 + dc * (g2 - g1) * intensity)
        b = round(b1 + dc * (b2 - b1) * intensity)
        
        if intensity > 1:
            return color(255, 255, 255)
        elif intensity < 0:
            return color(0, 0, 0)
        else:
            return color(r, g, b)
