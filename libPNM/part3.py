import sys, math
import numpy as np
from PNM import *
from grace_ball import *

def sphereToLatlong(sphere_img):
    latlong_img = np.empty(shape=(384, 768, 3), dtype=sphere_img.dtype)
    radius = 511/float(2)
    for x in range(511):
        x -= radius
        for y in range(511):
            y -= radius
            if (x**2)+(y**2) <= radius**2:
                (xx,yy,zz) = getReflection(x, y, radius)
                (lat, long) = tolatlong(xx, yy, zz)
        
                height,width,_ = latlong_img.shape
                # lat_coord 0 should be middle of latlong map
                lat_coord = ((lat + 0.5) % 1) * width
                # long_coord is from bottom, latlong indexes from the top
                long_coord = (1 - long) * height
                
                reX = x + radius
                reY = y + radius
                reX = int(reX)
                reY = int(reY)

                latlong_img[long_coord, lat_coord] = sphere_img[reY, reX]
    
    return latlong_img

def getSpherePixel(lat, long):
    phi = lat * 2 * np.pi
    theta = long * np.pi
    #theta = np.pi - theta

    # y = np.sin(phi) * np.cos(theta)
    # x = np.sin(phi) * np.sin(theta)
    x = 255 * np.sin(phi) * np.sin(theta)
    y = 255 * np.cos(theta)
    radius = 510/float(2)
    return (int(x + radius), int(y + radius))

def getLatlong(x, y, width, height):
    lat = ((float(x) / width) - 0.5)
    long = 1 - (float(y) / height)
    return (lat, long)

def createLatlong(sphere_img):
    latlong_img = np.empty(shape=(384, 768, 3), dtype=sphere_img.dtype)
    height, width, _ = latlong_img.shape
    for y in range(height):
        for x in range(width):
            lat, long = getLatlong(x, y, width, height)
            sx, sy = getSpherePixel(lat, long)

            latlong_img[y, x] = sphere_img[sy, sx]
    return latlong_img


if '__main__' == __name__:
    sphere_img = loadPFM('../MirrorBall/mirror_ball.pfm')
    latlong_img = createLatlong(sphere_img)
    writePFM('../MirrorBall/mirror_latlong.pfm', latlong_img)
    LoadPFMAndSavePPM('../MirrorBall/mirror_latlong.pfm','../MirrorBall/mirror_latlong.ppm')
