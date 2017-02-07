#!/usr/bin/python
import sys, getopt, math
import numpy as np
from PNM import *

def LoadAndSavePFM(in_path, out_path):
    img_in = loadPFM(in_path)
    img_out = np.empty(shape=img_in.shape, dtype=img_in.dtype)
    height,width,_ = img_in.shape # Retrieve height and width
    for y in range(height):
        for x in range(width):
            img_out[y,x,:] = img_in[y,x,:] # Copy pixels

    writePFM(out_path, img_out)

def LoadAllPFMs(in_path, in_name, num):
	imgs = np.empty(num, dtype=object)
	for x in range(num):
		string = in_path + "/" + in_name + `x + 1` + ".pfm"
		imgs[x] = loadPFM(string)
	return imgs

def GetWeighting(val):
	w_func = np.vectorize(lambda x: (math.cos(math.pi + x * 2 * math.pi) + 1) / 2 if (0.005 < x < 0.92) else 0.0) # TODO: linear hat-weighting
	return w_func(val)


def ProcessPixel(pfms, x, y):
	pxl_sum = 0
	w_sum = 0
	for idx,img in enumerate(pfms):
		w = GetWeighting(img[y][x])
		w_sum += w
		pxl = img[y][x]
		pxl = pxl / pow(4,idx) # TODO: Fix when pxl contains a 1.0
		log_func = np.vectorize(math.log)
		pxl = log_func(pxl)
		pxl_sum += pxl * w

	exp_func = np.vectorize(lambda x, y: math.exp(x / y) if y != 0 else math.exp(x))
	return exp_func(pxl_sum, w_sum)

def Test():
	rect = (300, 400, 400, 500)
	pfms = LoadAllPFMs("../Memorial", "memorial", 7)
	img_out = np.empty(shape=pfms[0].shape, dtype=pfms[0].dtype)

	for y in range(rect[1], rect[3]):
		for x in range(rect[0], rect[2]):
			img_out[y,x,:] = ProcessPixel(pfms, x, y)

	writePFM("smalltest.pfm", img_out)

def ProcessPFMs():
	pfms = LoadAllPFMs("../Memorial", "memorial", 7)
	img_out = np.empty(shape=pfms[0].shape, dtype=pfms[0].dtype)

	height,width,_ = pfms[0].shape
	maxval = height * width
	i = 0
	for y in range(height):
		for x in range(width):
			img_out[y,x,:] = ProcessPixel(pfms, x, y)
			p = i * 100 / maxval
			sys.stdout.write("\r" + `p` + "%")
			i += 1
	
	out_path = "f.pfm"
	writePFM(out_path, img_out)
	sys.stdout.write("\n")
	return out_path

def CreateLinearPPM(pfm_path, stops):
	img_pfm = loadPFM(pfm_path)
	scale_func = np.vectorize(lambda x: min(x * pow(2, stops), 1.0) * 255)
	img_out = scale_func(img_pfm)
	out_path = "n.ppm"
	writePPM(out_path, img_out.astype(np.uint8))
	return out_path

def ApplyGamma(in_path, gamma):
	img_in = loadPPM(in_path)
	gamma_func = np.vectorize(lambda x: pow(x, 1.0 / gamma))
	img_out = gamma_func(img_in)
	writePPM("g.ppm", img_out.astype(np.uint8))

if '__main__' == __name__:
	try:
		opts, args = getopt.getopt(sys.argv[1:], "rs:g:")
	except getopt.GetoptError:
		print 'part1.py (-r) -s <stops> -g <gamma>'
		sys.exit(2)
	
	pfm_path = "f.pfm"
	stops = 0
	gamma = 2.2
	for opt, arg in opts:
		if opt == "-r":
			pfm_path = ProcessPFMs()
		elif opt == "-s":
			stops = int(arg)
		elif opt == "-g":
			gamma = float(arg)

	n_path = CreateLinearPPM(pfm_path, stops)
	ApplyGamma(n_path, gamma)
