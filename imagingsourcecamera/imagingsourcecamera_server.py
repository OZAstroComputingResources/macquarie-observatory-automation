# coding: utf-8
# A user can input the settings they want and then the program will take some images with the camera using these settings

import unicap
import time
import sys
import Image
import pyfits
import numpy
import os
import pyraf
from pyraf import iraf
import math
import socket


class ImagingSourceCameraServer:

	dev = unicap.Device( unicap.enumerate_devices()[0] ) # I am assuming this will be the first camera the program comes across
	
	# The central pixel coordinates
	central_xpixel = 320.0   # 640 x pixel width
	central_ypixel = 240.0   # 480 y pixel height
	north_move_arcsecs = 0
	east_move_arcsecs = 0
	oneArcsecinPixelsN = 1  # This tells us how many pixels there are to one arcsecond in the North/South direction
	oneArcsecinPixelsE = 1  # This tells us how many pixels there are to one arcsecond in the East/West direction
	axis_flip = 1.0
	theta = 0 
	transformation_matrix = [math.cos(theta), math.sin(theta), -1*math.sin(theta), math.cos(theta)]	
	
	# Transformation matrix to be visualised as follows:
	#
	#    |   cos(theta)   sin(theta)   |      ie      |   transformation_matrix[0]  transformation_matrix[1]   |
	#    |  -sin(theta)   cos(theta)   |              |   transformation_matrix[2]  transformation_matrix[3]   |
	#
	# Transformation matrix is a rotation matrix.
	
	#Store the default camera settings here
	frameRateDefault = 30.0
	exposureAutoDefault = 3
	exposureAbsoluteDefault = 333
	gainDefault = 1023
	brightnessDefault = 0
	gammaDefault = 100
	
	#Put in the allowed values for relevant options
	#We give an array for each variable
	frameRateAllowedValues = range(1,241) #setting up the allowed frame rates to be in 0.25 increments 
	for r in range(0,len(frameRateAllowedValues)):
		frameRateAllowedValues[r] = frameRateAllowedValues[r]*0.25
	exposureAutoAllowedValues = range(0,4)
	exposureAbsoluteAllowedValues = range(1, 36000001)
	gammaAllowedValues = range(1, 501)
	brightnessAllowedValues = range(0, 64)
	gainAllowedValues = range(260, 1024)

	properties = ['frame rate', 'Exposure, Auto', 'Exposure (Absolute)', 'Gain', 'Brightness', 'Gamma']
	default_values = [frameRateDefault, exposureAutoDefault, exposureAbsoluteDefault, brightnessDefault, gammaDefault]
	allowed_range = [frameRateRange, exposureAutoRange, exposureAbsoluteRange, gainRange, brightnessRange, gammaRange]
	set_values = [frameRateDefault, exposureAutoDefault, exposureAbsoluteDefault, brightnessDefault, gammaDefault]
	
	

	
#******************************* The main camera commands ***********************************#

		
		
	def cmd_setCameraValues(self):
		'''This sets up the camera with the exposure settings etc. wanted by the user. If no input is given
		this will list the allowed values for each of the settings, otherwise a user can set each setting individually. 
		The properties are: FrameRate, ExposureAuto, ExposureAbs, Gain, Brightness, Gamma. To set a property type:
		setCameraValues FrameRate 3 \nTo get a list of properties type: setCameraValues show.\nTo use the default settings
		type "setCameraValues default"'''
		commands = str.split(the_command)
		if len(commands) == 1:
			message = ""
			for i in range(0, len(self.properties)-1):
				message += " property: "+properties[i]+', allowed range: '+str(self.allowed_range[i][0])+' to '+str(self.allowed_range[i][-1]+', in increments of: 'str(int(self.allowed_range[i][1]) - int(self.allowed_range[i][0]))+"\n"
			return message
		elif len(commands) == 2 and commands[1] == 'show':
			message = ''
			for i in range(0, len(self.properties)-1):
				message += properties[i]+' '+set_values[i]+'\n'
			return message

		elif len(commands) == 2 and commands[1] == 'default':
			for i in range(0,len(self.properties)-1):
				prop = self.dev.get_property( self.properties[i] )
				prop['value'] = float(self.set_values[i])
				self.dev.set_property( prop )
			return 'Default settings used for all properties.'

		elif len(commands) == 3:
			#fmts = self.dev.enumerate_formats()
			#props = self.dev.enumerate_properties()
			pro = commands[1]
			try: float(commands[2])
			except Exception: return 'Invalid input'
			if pro == 'FrameRate' and float(commands[2]) in self.allowed_range[0]: self.set_values[0] == float(commands[2])
			elif pro == 'ExposureAuto' and float(commands[2]) in self.allowed_range[1]: self.set_values[1] == float(commands[2])
			elif pro == 'ExposureAbs' and float(commands[2]) in self.allowed_range[2]: self.set_values[2] == float(commands[2])
			elif pro == 'Gain' and float(commands[2]) in self.allowed_range[3]: self.set_values[3] == float(commands[2])
			elif pro == 'Brightness' and float(commands[2]) in self.allowed_range[4]: self.set_values[4] == float(commands[2])
			elif pro == 'Gamma' and float(commands[2]) in self.allowed_range[5]: self.set_values[5] == float(commands[2])*100.0
			else: return 'Invalid input, type "setCameraValues show" for a list of allowed inputs and ranges'
			for i in range(0,len(self.properties)-1):
				prop = self.dev.get_property( self.properties[i] )
				prop['value'] = float(self.set_values[i])
				self.dev.set_property( prop )
		return str(pro)+' value updated'
		


	def cmd_starDistanceFromCenter(self, the_command):
		'''This checks the position of the brighest star in shot with reference to the center of the frame and
		the sharpness of the same star. A call to this function will return a vector distance between the centeral
		pixel and the brightest star in arcseconds in the North and East directions. When calling this function 
		you must specify which file for daofind to use (do not add the file extension, ie type "filename" NOT "filename.fits"'''
		commands = str.split(the_command)
		if len(commands) =! 2: return 'Invalid input, give name of file with data.'
		filename = commands[1]	
		dDec = 0
		dAz = 0
		brightest_star_info = self.analyseImage(filename'.fits', filename'.txt') 
		star_sharp = float(brightest_star_info[3])  # We will use this to check the focus of the star
		star_mag = float(brightest_star_info[2])    # We use this to identify the brightest star
		xpixel_pos = float(brightest_star_info[0])  # x pixel position of the brightest star
		ypixel_pos = float(brightest_star_info[1])  # y pixel position of the brightest star
		# Find distance from the center of the image
		x_distance = float(self.central_xpixel) - xpixel_pos # The position of the star relative to the central pixel
		y_distance = float(self.central_ypixel) - ypixel_pos
		vector_to_move = [x_distance, y_distance]
		translated_x = self.transformation_matrix[0]*x_distance + self.transformation_matrix[1]*y_distance
		translated_y =  (self.transformation_matrix[2]*x_distance + self.transformation_matrix[3]*y_distance)*self.axis_flip

		#Need to convert distance into coordinates for the telescope orientation

		# we should have it in RA Dec
		dArcsecN = translated_x*self.oneArcsecinPixelsN
		dArcsecE = translated_y*self.oneArcsecinPixelsE*-1.0 # Now we convert where to move a positive is a move East
		return [dArcsecN, dArcsecE] 
		# ^ This returns the distance between the central pixel and the brightest star in arcseconds in the North and East directions		
		
		
		
	def cmd_captureImages(self, the_command):
		'''This takes the photos to be used for science. Input the name of the images to capture (images will then be
		numbered: ie filename1.fits filename2.fits) and the number of images to capture. Note: when specifying a filename
		you do not need to include the extention: ie input "filename" not "filename.fits"'''
		commands = str.split(the_command)
		if len(commands) != 3: return 'Please input number of images to capture.'
		try: int(commands[2])
		except Exception: return 'Invalid number.'
		upperlimit = int(commands[2])
		base_filename = commands[1]
		self.dev.start_capture()
		imgbuf = self.dev.wait_buffer( 10 ) 
		for i in range( 0, upperlimit ):
			#self.dev.set_property( prop )
			t1 = time.time()
			imgbuf = self.dev.wait_buffer( 11 )
			dt = time.time() - t1
			#print 'dt: %f  ===> %f' % ( dt, 1.0/dt )
			filename= base_filename+str(i)
			rgbbuf = imgbuf.convert( 'RGB3' )
			dummy = rgbbuf.save( filename+'.raw' ) # saves it in RGB3 raw image format
			Image.open( filename+'.raw' ).save( filename+'.jpg' ) # saves as a jpeg
			os.system("convert -depth 8 -size 640x480+17 "+ filename+'.raw' +" "+ filename+'.fits') # saves as a fits file
		self.dev.stop_capture()


	def cmd_orientationCapture(self, the_command):  # need to have some define settings for this perhaps who knows
		'''This will take the photos for camera orientation and automatically name them
		so that another function can calculate the orientation easily. For the base photograph type
		the command "base", to take the photograph after the telescope has been moved North type "north amountmoved" where
		amountmoved is in arcseconds. To take the photograph after the telescope has been moved East type
		"east amountmoved" where again amountmoved is in arcseconds'''
		commands = str.split(the_command)
		image_name
		if len(commands) == 2 and commands[1] == 'base': image_name = 'base_orientation'
		elif len(commands) == 3:
			if commands[1] == 'North' and self.is_float_try(commands[2]):
				image_name = 'north_orientation'
				self.north_move_arcsecs = float(commands[2])
			elif commands[1] == 'East' and self.is_float_try(commands[2]):
				image_name = 'east_orientation'
				self.east_move_arcsecs = float(commands[2])
		else: return 'Invalid input'
		self.dev.start_capture()
		
		imgbuf = self.dev.wait_buffer( 10 ) #Prolly wont work with the below

		t1 = time.time()
		imgbuf = self.dev.wait_buffer( 11 )
		dt = time.time() - t1
		
		rgbbuf = imgbuf.convert( 'RGB3' )
		dummy = rgbbuf.save( image_name+'.raw' ) #saves it in RGB3 raw image format
		Image.open( image_name+'.raw' ).save( image_name+'.jpg' ) #saves as a jpeg
		os.system("convert -depth 8 -size 640x480+17 "+ image_name+'.raw' +" "+ image_name+'.fits') #saves as a fits file
		
		self.dev.stop_capture()
		return str(commands[1])+' image captured.' # change this to a number perhaps for ease when automating


	def cmd_calculateCameraOrientation(self, the_command):
		'''This does the maths for the camera orientation. In this we treat the x axis as the North axis'''
		base_star_info = self.analyseImage('base_orientation.fits','base_orientation.txt')
		north_star_info = self.analyseImage('north_orientation.fits','north_orientation.txt')
		east_star_info = self.analyseImage('east_orientation.fits','east_orientation.txt')
		if base_bright_star == 0 or north_bright_star == 0 or east_bright_star == 0:
			return 'Orientation photos need to be taken'
		brightest_star_info = self.find_brightest_star(outfile)
		star_sharp = float(brightest_star_info[3])    # We will use this to check the focus of the star
		base_xpixel_pos = float(base_star_info[0])    # x pixel position of the brightest star
		base_ypixel_pos = float(base_star_info[1])    # y pixel position of the brightest star
		base_star_mag = float(brightest_star_info[2]) # We use this to identify the brightest star
		north_xpixel_pos = float(north_star_info[0])
		north_ypixel_pos = float(north_star_info[1])
		north_star_mag = float(north_star_info[2])
		east_xpixel_pos = float(east_star_info[0])  # The east move is to determine if we need a swap or not
		east_y_pixel_pos = float(east_star_info[1])
		east_star_mag = float(east_star_info[2])

		vector_movedN = [base_xpixel_pos - north_xpixel_pos, base_ypixel_pos - north_ypixel_pos]
		hypotenuseN = math.hypot(vector_movedN[0], vector_movedN[1])) # this is number of pixels moved for N/S
		self.oneArcsecinPixelsN = hypotenuesN/self.north_move_arcsecs
		self.theta = math.tan(abs(vector_movedN[1]/vector_movedN[0]))

		if vector_movedN[0] < 0 and vector_movedN[1] < 0: self.theta = math.pi+ self.theta
		elif vector_movedN[0] < 0 and vector_movedN[1] > 0: self.theta = math.pi - self.theta
		elif vector_movedN[0] > 0 and vector_movedN[1] < 0: self.theta = 2*math.pi - self.theta
		elif vector_movedN[0] > 0 and vector_movedN[1] > 0: # All good nothing to do
		elif vector_movedN[0] == 0 and vector_movedN[1] > 0: self.theta = math.pi/2.0
		elif vector_movedN[0] == 0 and vector_movedN[1] < 0: self.theta = 3.0*math.pi/2.0
		elif vector_movedN[0] > 0 and vector_movedN[1] == 0: self.theta = 0
		elif vector_movedN[0] < 0 and vector_movedN[1] == 0: self.theta = math.pi
		else: return "I shouldn't be able to get here. Theta Error.'

		# Need to recalculate the transformation matrix:
		self.transformation_matrix = [math.cos(self.theta), math.sin(self.theta), -1*math.sin(self.theta), math.cos(self.theta)]	

		vector_movedE = [north_xpixel_pos - east_xpixel_pos, north_ypixel_pos - east_ypixel_pos]
		hypotenuseE = math.hypot(vector_movedE[0], vector_movedE[1])) # this is number of pixels moved for E/W
		self.oneArcsecinPixelsE = hypotenuesE/self.east_move_arcsecs

		translated_y =  self.transformation_matrix[2]*vector_movedE[0] + self.transformation_matrix[3]*vector_movedE[1]
		if translated_y =< 0: self.axis_flip = 1 # because positive is west, negative is east
		elif translated y > 0: self.axis_flip = -1
		else: 'Oops'
		return 'Orientation complete'

		#  The above camera orientation command uses the following definition for the axis' with all rotations
		#  being made in an anticlockwise direction
		#
		#	      W
		#             |
		#             |
		#	      |
		#  S ------------------- N
		#	      |
		#	      |
		#	      |
		#	      E



	def cmd_calculateBestFocus(self,the_command):
		'''Here we need to take a bunch of images at different focuses and use iraf to estimate the
		position of best focus. This will be easiest with a focuser like the JMI where you can go to
		specific positions and move by specific amounts.'''
		#commands = str.split(the_command)
		#if len(commands) != 2: return 'Invalid input'
		#try: int(commands[1])
		#except Exception: return 'Error, input the number of photos taken for focusing calculation'
		filename = 'focusing_image'
		# Need to check the correct number of files exist
		# Need to actually work out how to use the blooming starfocus command in iraf

		# A very basic focusing routine here could just take a photo, find the brightest star
		# do a daofind on the fits file and return the sharpness of the brightest star
		# it would then be down to a user/loop to do this, move focus, and if the sharpness decreased
		# to continue moving the focuser in the same direction but if the sharpness goes up, to move the
		# focuser in the other direction
		# do this and half the distances you're traveling when you over step the best focus point till the distance
		# gets down to 1 count
		self.cmd_captureImages(filename, 1)
		bright_star_info = self.analyseImage(filename+'.fits', 'focus_output.txt')
		sharpness_value = bright_star_info[3]
		return sharpness_value
		


#*********************************** End of user commands ***********************************#


	def analyseImage(self, input_image, outfile)
		iraf.noao(_doprint=0)     # load noao
		iraf.digiphot(_doprint=0) # load digiphot
		iraf.apphot(_doprint=0)   # load apphot
		
		self.check_if_file_exists(outfile)
		try: iraf.daofind(image = input_image, output = outfile)
		except Exception: return 0
		brightest_star_info = self.find_brightest_star(outfile)
		return brightest_star_info


	def is_float_try(self, stringtry):
		try:
			float(stringtry)
			return True
		except ValueError:
			return False


	def find_brightest_star(self, readinfile):
		try: starfile = open(readinfile)
		except Exception: return 'ERROR file not found' # <-- change this to returning a number
		startemp = starfile.readlines()
		brighteststar = 50
		xpixel = 0
		ypixel = 0
		for lines in startemp:
			if lines[0][0] != '#': #don't want the comments
				linetemp = str.split(lines)
				if float(linetemp[2]) < brighteststar:
					starmag = float(linetemp[2])
					xpixel = float(linetemp[0])
					ypixel = float(linetemp[1])
					starsharp = float(linetemp[3])
		return [starmag, xpixel, ypixel, starsharp]
	

	def check_if_file_exists(self, filename):
		#i = 0 # counter to stop this going on forever
		if os.path.isfile(filename): os.remove(filename)
		return filename
	

		
		



