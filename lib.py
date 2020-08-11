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

    def createWindow(self, width, height):
        self.width = width
        self.height = height

    def point(self, x, y, selectColor = None):
        try:
            self.framebuffer[y][x] = selectColor or  self.color
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

    def triangle1(self, A, B, C, selectColor = None):
        if A.y > B.y:
            A, B = B, A
        if A.y > C.y:
            A, C = C, A
        if B.y > C.y:
            B, C = C, B

        dx_ac = C.x - A.x
        dy_ac = C.y - A.y

        if dy_ac == 0:
            return

        mi_ac = dx_ac/dy_ac

        dx_ab = B.x - A.x
        dy_ab = B.y - A.y

        if dy_ab != 0:
            mi_ab = dx_ab/dy_ab

            for y in range(A.y, B.y + 1):
                xi = round(A.x - mi_ac * (A.y - y))
                xf = round(A.x - mi_ab * (A.y - y))

                if xi > xf:
                    xi, xf = xf, xi
                for x in range(xi, xf + 1):
                    self.point(x, y, selectColor)

        dx_bc = C.x - B.x
        dy_bc = C.y - B.y

        if dy_bc:

            mi_bc = dx_bc/dy_bc

            for y in range(B.y, C.y + 1):
                xi = round(A.x - mi_ac * (A.y - y))
                xf = round(B.x - mi_bc * (B.y - y))

                if xi > xf:
                    xi, xf = xf, xi
                for x in range(xi, xf + 1):
                    self.point(x, y, selectColor)

    def triangle(self, A, B, C, selectColor):
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
                
    def load(self, filename, translate, scale):
        model = Obj(filename)

        light = V3(-0.3, 0.7, 0.8)
        
        for face in model.faces:
            vcount = len(face)

            if vcount == 3:
                f1 = face[0][0] - 1
                f2 = face[1][0] - 1
                f3 = face[2][0] - 1

                v1 = V3(model.vertices[f1][0], model.vertices[f1][1], model.vertices[f1][2])
                v2 = V3(model.vertices[f2][0], model.vertices[f2][1], model.vertices[f2][2])
                v3 = V3(model.vertices[f3][0], model.vertices[f3][1], model.vertices[f3][2])

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

                normal = cross(sub(B, A), sub(C, A))
                intensity = dot(norm(normal), light)

                actualColor = self.shaders(A, intensity)

                self.triangle(A, B, C, actualColor)
                

            else:
                f1 = face[0][0] - 1
                f2 = face[1][0] - 1
                f3 = face[2][0] - 1
                f4 = face[3][0] - 1   

                v1 = V3(model.vertices[f1][0], model.vertices[f1][1], model.vertices[f1][2])
                v2 = V3(model.vertices[f2][0], model.vertices[f2][1], model.vertices[f2][2])
                v3 = V3(model.vertices[f3][0], model.vertices[f3][1], model.vertices[f3][2])
                v4 = V3(model.vertices[f4][0], model.vertices[f4][1], model.vertices[f4][2])

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

                normal = cross(sub(B, A), sub(C, A))
                intensity = dot(norm(normal), light)

                actualColor = self.shaders(A, intensity)
                
                self.triangle(A, B, C, actualColor)

                actualColor = self.shaders(C, intensity)

                self.triangle(A, D, C, actualColor)

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

    '''
    def shaders1(self, x, y, z, intensity):
        grey = random.randint(120, 150)
        d = random.randint(0, 50)
        0 = random.randint(115, 210)
        0 = random.randint(90, 165)
        if x > 400 + d and x < 600 - d and y >= 720 + d and y < 800 - d:
            selectColor = color(208, 215, 224)
            zColor = color(208, 215, 224)
        elif x > 450 + d and x < 600 - d and y >= 650 and y < 700 + d:
            selectColor = color(grey, grey, 100)
        elif x > 375 + d and x < 675 - d and y >= 500 - d and y < 650 + d:
            selectColor = color(0, 150, 0)
        elif x > 475 + d and x < 600 - d and y >= 450 - d and y < 500 + d:
            selectColor = color(0, 120, 0)
            zColor = color(0, 120, 0)
        elif x > 490 + d and x < 510 - d and y >= 400 and y < 450:
            selectColor = color(0, 100, 0)
            zColor = color(0, 100, 0)
        elif x > 530 + d and x < 590 - d and y >= 350 and y < 450:
            selectColor = color(0, grey, 0)
        elif x > 550 + d and x < 580 - d and y >= 200 - d and y < 350:
            selectColor = color(0, grey, 0)
        else:
            grey = round(255 * intensity)
            if grey < 0:
                grey = 0
            elif grey > 255:
                grey = 255
            z = round(z % 255)
            selectColor = color(0, 0, grey)
            zColor = color(0, 0, z)
            
        return x, y, selectColor, zColor
    '''

    def shaders(self, A, intensity):
        d = random.randint(0, 50)
        grey = random.randint(120, 150)
        if A.x > 400 and A.x < 600 and A.y >= 720 and A.y < 800:
            selectColor = color(208, 215, 224)
        elif A.x > 450 + d and A.x < 600 - d and A.y >= 650 and A.y < 700 + d:
            selectColor = color(grey, grey, 100)
        elif A.x > 375 + d and A.x < 675 - d and A.y >= 500 - d and A.y < 650 + d:
            selectColor = color(0, 150, 0)
        elif A.x > 475 + d and A.x < 600 - d and A.y >= 450 - d and A.y < 500 + d:
            selectColor = color(0, 120, 0)
        elif A.x > 490 + d and A.x < 510 - d and A.y >= 400 and A.y < 450:
            selectColor = color(0, 100, 0)
        elif A.x > 530 + d and A.x < 590 and A.y >= 350 and A.y < 450:
            selectColor = color(0, grey, 0)
        elif A.x > 550 + d and A.x < 580 and A.y >= 200 and A.y < 350:
            selectColor = color(0, grey, 0)
        
        else:
            grey = round(255 * intensity)
            if grey < 0:
                grey = 0
            elif grey > 255:
                grey = 255
            selectColor = color(0, 0, grey)
        return selectColor