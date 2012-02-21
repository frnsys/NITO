#!/usr/bin/python
# NITO 1.0
# nito.py
# Copyright (c) 2010 - 2012 Francis Tseng.

import Image
import codecs
import math
import re
import binascii
import easygui
import sys

'''****************'''
'''DEFINE FUNCTIONS'''
'''****************'''

def text2hex(string):
	'''
	converts text string to hexadecimal string,
	returns list of hexadecimal colors, with last item
	as total number of colors
	'''
	hexstr = string.encode('hex_codec') #encodes string into hexadecimal
	hexlen = len(hexstr)
	scope = math.ceil(hexlen/6) #gets number of pixels/colors to be written
	hexlist = []
	for i in range(0,hexlen,6): #slices hex string into list of hex colors
		hexcolor = hexstr[i:i+6]
		hexlist.append(hexcolor)
	hexlist.append(scope) #adds scope to the end of the hex-color list
	return hexlist

def rgb2hex(rgb):
	hexcolor = '%02x%02x%02x' % rgb
	return hexcolor

def hex2rgb(hexcolor):
	'''
	converts hexadecimal colors to rgb color values,
	returns tuple of (r,g,b) values
	'''
	hexcolor = hexcolor.strip()
	if hexcolor[2:6] == '':	#if no values for the last four spaces, add 0's
		hexcolor = hexcolor + '0000'
	elif hexcolor[4:6] == '': #if no values for the last two spaces, add 0's
		hexcolor = hexcolor + '00'
	r, g, b = hexcolor[:2], hexcolor[2:4], hexcolor[4:6]
	r, g, b = [int(n,16) for n in (r,g,b)]
	return (r, g, b)

def text2dec(key):
	'''
	converts text string to decimal
	'''
	hexstr = key.encode('hex_codec') #encodes string into hexadecimal
	if len(hexstr)<=16:
		dec = int(hexstr,16) #converts hexadecimal string into decimal
	elif len(hexstr)>16: #hexstrings over length of 16 will become long type
		dec = int(hexstr,16)*0.000001
	if type(dec) is long: #if type is long, throw error
		raise ValueError, "Text input is too long!"
	else:
		decstr = str(dec) #converts dec to string
		m = re.findall(r'\d+',decstr) #extracts only numbers
		mdecstr = ''.join(m) #concats numbers to single string
		return mdecstr

def coordcalc(string):
	'''
	calculates initial x,y coordinates and plotting values,
	returns a tuple
	'''
	d = text2dec(string)
	initX = (int(d[0])+1)*(int(d[2])+1)*(int(d[-1])+1)+(int(d[-6:-4]))
	initY = (int(d[1])+1)*(int(d[3])+1)*(int(d[-2])+1)+(int(d[-5:-3]))
	plotX = math.floor((int(d[-1])+1)*(int(d[-3])+1)*(int(d[-5])+1)/3)
	plotY = math.floor((int(d[-2])+1)*(int(d[-4])+1)*(int(d[-6])+1)/3)
	return (initX, initY, plotX, plotY)

def calcxup(x,plotX):
	newx = (math.fabs(math.sin(x))*x)+(plotX)
	return int(newx)
def calcyup(y,plotY):
	newy = (math.fabs(math.sin(y))*y)+(plotY)
	return int(newy)
def calcxdown(x,plotX):
	newx = math.fabs((math.fabs(math.sin(x))*x)-(plotX))
	return int(newx)
def calcydown(y,plotY):
	newy = math.fabs((math.fabs(math.sin(y))*y)-(plotY))
	return int(newy)

def plotter(coords, scope, imgdim):
	'''
	calculates all x,y coordinates to plot
	returns a list of tuples (x,y)
	'''
	x, y, plotX, plotY = coords[0], coords[1], coords[2], coords[3]
	imgwidth, imgheight = imgdim[0], imgdim[1]
	xylist = []
	for i in range(0,int(scope)):
		if i >= 1:	#if not first output, then modify x & y
			if calcxup(x,plotX) < imgwidth :	#checks if new x is within image bounds
				if calcyup(y,plotY) < imgheight: #checks if new y is within bounds
					y = calcyup(y,plotY)
				elif calcydown(y,plotY) > 0:
					y = calcydown(y,plotY)
				else:
					y = y + 1
				x = calcxup(x,plotX)
			elif calcxdown(x,plotX) > 0:	#checks if new x is within image bounds
				if calcyup(y,plotY) < imgheight:
					y = calcyup(y,plotY)
				elif calcydown(y,plotY) > 0:
					y = calcydown(y,plotY)
				else:
					y = y + 1
				x = calcxdown(x,plotX)
		else:	#if first output, don't modify x & y
			if x > imgwidth:
				x = math.floor(x/imgwidth)
			if y > imgheight:
				y = math.floor(y/imgheight)
		xylist.append([x,y]) 	#adds new coordinates as tuples in a list
	for i in range(0,len(xylist)): #checks for and modifies duplicate coordinates
		for j in range(0,len(xylist)):
			if i != j:
				if xylist[i][0] == xylist[j][0]:
					xylist[j][0] = xylist[j][0] + 1
				if xylist[i][1] == xylist[j][1]:
					xylist[j][1] = xylist[j][1] + 1
	return xylist

def encoder(xylist, hexlist, pix):
	'''
	sets the pixels in the image
	'''
	for i in range(0,len(xylist)):
		x, y = xylist[i][0], xylist[i][1]
		rgb = hex2rgb(hexlist[i])
		pix[x,y] = rgb
	return pix

def decoder(xylist, pix, scope):
	'''
	decodes the pixels into message
	'''
	decoded = []
	for i in range(0,int(scope)):
		x, y = xylist[i][0], xylist[i][1]
		rgb = pix[x,y]
		hexcolor = rgb2hex(rgb) #converts rgb to hex
		decodestr = binascii.unhexlify(hexcolor) #converts hex to text
		decoded.append(decodestr)
	decodedtext = ''.join(decoded) #concats decoded segments into full message
	return decodedtext

'''*************'''
'''END FUNCTIONS'''
'''*************'''

defaultimgpath = "/Users/"

while True:
	'''ENCODER OR DECODER?'''
	choice = easygui.buttonbox(msg='Encode/Decode',title='NITO',choices=('Encoder','Decoder','Quit'))

	if choice == 'Encoder':
		while True:
			'''INPUT IMAGE'''
			imgpath = easygui.fileopenbox(msg="Select image to encode",title="Open Image",default=defaultimgpath,filetypes=[["*.jpg","*.jpeg","JPG files"],"*.png"])
			defaultimgpath = imgpath
			if imgpath == None: #if user hits cancel
				break
			else:
				img = Image.open(imgpath)
				imgdim = img.size #gets image dimensions as a tuple
				print 'Image Path: '+str(imgpath)
				print 'Image Dimensions: '+str(imgdim)
				pix = img.load() #loads image for faster access
				
				while True:
					'''INPUT MESSAGE'''
					message = easygui.enterbox(msg="Enter your message to encode",title="Message Input",default="",strip=True)
					if message == None: #if user hits Cancel
						break
					elif message == "":
						easygui.msgbox(msg="Please enter a message.",title="Enter a Message",ok_button="OK")
						continue
					else:
						print 'Message: '+str(message)
						
						while True:
							'''INPUT KEY'''
							key = easygui.enterbox(msg="Enter your unlock key",title="Key Input",default="",strip=True)
							if key == None: #if user hits cancel
								break
							elif key == "":
								easygui.msgbox(msg="Please enter a key.",title="Enter a Key",ok_button="OK")
								continue
							else:
								print 'Key: '+str(key)
								
								'''RUN FUNCTIONS'''
								#Convert Input Message to list of RGB tuples
								hexlist = text2hex(message)
								rgblist = []
								for i in range(0,len(hexlist)-1):
									rgblist.append(hex2rgb(hexlist[i]))
								print 'RGB List: '+str(rgblist)
								scope = len(rgblist)
								print 'Scope: '+str(scope)

								#Convert Input Key to Coordinates
								coords = coordcalc(key)
								print 'Initial X,Y,modifiers: '+str(coords)
								xylist = plotter(coords,scope,imgdim)
								print 'Coordinates: '+str(xylist)

								#Plot the Pixels
								encoder(xylist,hexlist,pix)

								'''RETURN SCOPE'''
								easygui.msgbox(msg=scope,title="Scope",ok_button="OK")
								while True:
									'''SAVE IMAGE'''
									savefile = easygui.filesavebox(msg="Save encoded image as...",title="Save Image",default="image")
									if savefile == None: #if user hits cancel
										break
									elif savefile == "":
										easygui.msgbox(msg="Please enter an image name.",title="Enter a Name",ok_button="OK")
										continue
									else:
										img.save(savefile+'.png','png')
										sys.exit(0) #quit after saving image!
		if imgpath == None: #if user hits cancel, return to selection menu
			continue

	elif choice == 'Decoder':
		while True:
			'''INPUT IMAGE'''
			imgpath = easygui.fileopenbox(msg="Select image to encode",title="Open Image",default=defaultimgpath,filetypes=["*.png"])
			defaultimgpath = imgpath
			if imgpath == None: #if user hits cancel
				break
			else:
				img = Image.open(imgpath)
				imgdim = img.size #gets image dimensions as a tuple
				print 'Image Path: '+str(imgpath)
				print 'Image Dimensions: '+str(imgdim)
				pix = img.load() #loads image for faster access
				while True:
					'''INPUT KEY'''
					key = easygui.enterbox(msg="Enter your unlock key",title="Key Input",default="",strip=True)
					if key == None: #if user hits cancel
						break
					elif key == "":
						easygui.msgbox(msg="Please enter a key.",title="Enter a Key",ok_button="OK")
						continue
					else:
						print 'Key: '+str(key)
						
						while True:
							'''INPUT SCOPE'''
							scope = easygui.integerbox(msg="Enter estimated scope",title="Scope Input",default="",lowerbound=0,upperbound=999)
							if scope == None: #if user hits cancel
								break
							elif scope =="":
								easygui.msgbox(msg="Please enter a scope.",title="Enter a Scope",ok_button="OK")
								continue
							else:
								print 'Estimated Scope: '+str(scope)
								
								'''RUN FUNCTIONS'''
								#Convert Input Key to Coordinates
								coords = coordcalc(key)
								print 'Initial X,Y,modifiers: '+str(coords)
								xylist = plotter(coords,scope,imgdim)
								print 'Coordinates: '+str(xylist)

								#Read Pixels
								decodedtext = decoder(xylist,pix,scope)

								'''RETURN MESSAGE'''
								easygui.textbox(msg='Message:',title='Message',text=decodedtext,codebox=0)
								sys.exit(0)
			if imgpath == None: #if user hits cancel, quit
				sys.exit(0)
	
	elif choice == 'Quit':
		sys.exit(0)

	
