import sys, math
import numpy as np
from PNM import *

def LoadPFMAndSavePPM(in_path, out_path):
    img_in = loadPFM(in_path)
    img_out = np.empty(shape=img_in.shape, dtype=np.float32)
    height,width,_ = img_in.shape
    minfunc = np.vectorize(lambda x: min(x, 1.0))
    for y in range(height):
        for x in range(width):
            img_out[y,x,:] = minfunc(img_in[y,x,:]) * 255.0

    writePPM(out_path, img_out.astype(np.uint8))

"""
get mask in the shape of a disk over a 2D array
"""
def getDiskMask(img):
    (ydim,xdim,dummy) = img.shape
    # make an open grid of x,y
    y,x = np.ogrid[0:ydim, 0:xdim, ]
    y -= ydim/2                 # centered at the origin
    x -= xdim/2
    # now make a mask
    radius = xdim/2
    mask = x**2+y**2 <= radius**2
    return mask


"""
get Z coordinate of Sphere given its x,y and radius
"""
def getZfromCircle(x,y, radius):
    z = np.sqrt(radius**2 - x**2 - y**2)
    if not np.isnan(z):
        return z
    else:
        return 0


"""
get normal of a point on the sphere given point position and radius
Assume circle center at 0,0,0
"""
def getNormal(x,y, radius):
    return (x/radius, y/radius, getZfromCircle(x,y,radius)/radius)


def getReflection(x,y, radius):
    n = getNormal(x,y, radius)
    v = (0,0,1)
    # NminusV = tuple(np.subtract(n,v))
    # r = tuple(2*j for j in tuple([np.dot(n, v)*i for i in NminusV]))
    r = tuple(np.subtract(np.multiply(2, np.multiply(np.dot(n,v),n)),v))
    return r

def drawNormal(img):
    radius = 511/float(2)
    imgPPM = img
    for x in range(img.shape[1]):
        x -= radius
        for y in range(img.shape[0]):
            y -= radius
            if x**2+y**2 <= radius**2:
                #print 'before: ' + str((x,y))
                (xx,yy,zz) = getNormal(x, y, radius)
                reX = x + radius
                reY = y + radius
                reX = int(reX)
                reY = int(reY)
                img[reX,reY] = (xx,yy,zz)
                #print 'after: ' + str((x,y))
                # print ((xx+1) * 255.0/2,(yy+1) * 255.0/2,(zz+1) * 255.0/2)
                imgPPM[reX,reY] = ((xx+1) * 255.0/2,(yy+1) * 255.0/2,(zz+1) * 255.0/2)

    return imgPPM

def drawR(img):
    radius = 511/float(2)
    imgPPM = img
    for x in range(img.shape[1]):
        x -= radius
        for y in range(img.shape[0]):
            y -= radius
            if x**2+y**2 <= radius**2:
                #print 'before: ' + str((x,y))
                (xx,yy,zz) = getReflection(x, y, radius)
                reX = x + radius
                reY = y + radius
                reX = int(reX)
                reY = int(reY)
                img[reX,reY] = (xx,yy,zz)
                #print 'after: ' + str((x,y))
                # print ((xx+1) * 255.0/2,(yy+1) * 255.0/2,(zz+1) * 255.0/2)
                imgPPM[reX,reY] = ((xx+1) * 255.0/2,(yy+1) * 255.0/2,(zz+1) * 255.0/2)

    return imgPPM


def latLongToSphere(latlongImg, SphereImg):
    latlong = loadPFM(latlongImg)
    radius = 511/float(2)
    for x in range(511):
        x -= radius
        for y in range(511):
            y -= radius
            if x**2+y**2 <= radius**2:
                (xx,yy,zz) = getReflection(x, y, radius)
                # print (x,y)
                #print (xx,yy,zz)
                llX = (xx + 1) * (latlong.shape[0]/2.0)
                llY = (yy + 1) * (latlong.shape[1]/2.0)
                llZ = (zz) * (255)
                # (lat, long) = tolatlong(xx, yy, zz, radius)
                #print (lat,long)
                reX = x + radius
                reY = y + radius
                reX = int(reX)
                reY = int(reY)

                # I think the lat 0, long 0 should be the middle of the image...
                # height, width, _ = latlong.shape
                # lat_coord = (lat + (width / 2)) % width
                # long_coord = (long + (height / 2)) % height

                #SphereImg[reX,reY] = latlong[lat,long]
                SphereImg[reX,reY] = latlong[llX, llY]

def tolatlong(x,y,z,radius):
    phi = np.arctan(np.sqrt(x**2+y**2)/z)
    # print theta
    theta = np.arctan(y/x)
    lat = np.rad2deg(theta)
    long = np.rad2deg(phi)
    lat = int(lat)
    long = int(long)
    return (lat,long)


# img = loadPFM('../GraceCathedral/grace_ball.pfm')
# mask = getDiskMask(img)
# drawCircle(img, mask)
# writePFM('../GraceCathedral/grace_ball.pfm', img)
# LoadPFMAndSavePPM('../GraceCathedral/grace_ball.pfm','../GraceCathedral/grace_ball.ppm')

#
# img = loadPFM('../GraceCathedral/grace_ball_normal.pfm')
# mask = getDiskMask(img)
# imgPPM = drawNormal(img)
# writePFM('../GraceCathedral/grace_ball_normal.pfm', img)
# writePPM('../GraceCathedral/grace_ball_normal.ppm', imgPPM.astype(np.uint8))

# img = loadPFM('../GraceCathedral/grace_ball_reflection.pfm')
# imgPPM = drawR(img)
# writePFM('../GraceCathedral/grace_ball_reflection.pfm', img)
# writePPM('../GraceCathedral/grace_ball_reflection.ppm', imgPPM.astype(np.uint8))
#
img = loadPFM('../GraceCathedral/grace_ball.pfm')
latLongToSphere('../GraceCathedral/grace_latlong.pfm', img)
writePFM('../GraceCathedral/grace_ball.pfm', img)
LoadPFMAndSavePPM('../GraceCathedral/grace_ball.pfm','../GraceCathedral/grace_ball.ppm')
