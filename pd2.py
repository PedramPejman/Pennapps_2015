from scipy.io import wavfile
from matplotlib import pyplot as plt
import numpy as np
import peakutils
from peakutils.plot import plot as pplot
from matplotlib import pyplot
from scipy.signal import butter, lfilter, freqz

#class Event:
#	float timeStamp
#	float intensity
#	float duration

##GLOBALS
order = 6
fs = 30.0
cutoff = 3.667  
STEP = 1.0

def butter_lowpass(cutoff, fs, order=5):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return b, a

def butter_lowpass_filter(data, cutoff, fs, order=5):
    b, a = butter_lowpass(cutoff, fs, order=order)
    y = lfilter(b, a, data)
    return y

def readAndExtract(filename):
	# Load the data and calculate the time of each sample
	samplerate, y = wavfile.read(filename)
	x = np.arange(len(y))
	#Handle both mono and stereo audi	
	if type(y[0]) == np.ndarray:
		y = y[0:len(y)-1:STEP, 1]
	else:
		y = y[0:len(y)-1:STEP]
	y = butter_lowpass_filter(y, cutoff, fs, order)
	x = x[0:len(x)-1:STEP]
	return x, y

def findPeaks(y):
	return peakutils.indexes(y, thres=0.1, min_dist=44000)

def plot(x, y, indexes, breaths):
	pyplot.figure(figsize=(10,6))
	pplot(x, y, indexes)
	pyplot.title('Find peaks')
	#show breaths
	for key in breaths:
		breath = breaths[key]
		pyplot.axvspan(breath[0], breath[1], color='y', alpha=0.5, lw=0)
	
	pyplot.show()

def findBreaths(x, y, peaks):
	breaths = {}
	MAX_BREATH = 44100
	BYTE_SIZE = 5000
	THRESH = 1000
	bmin = None
	bmax = None
	for peak in peaks:
		index = peak - BYTE_SIZE
		#find begining of breath
		while (index > peak-MAX_BREATH):
			sublist = y[(index)*STEP:(index + BYTE_SIZE)*STEP]
			if not len(sublist): break
			avg = sum([abs(x) for x in sublist])/len(sublist)
			if (abs(avg) < THRESH):
				bmin = index
				break
			index = index - BYTE_SIZE
		if not bmin: bmin = index
		index = peak
		
		#find end of breath
		while (index < peak+MAX_BREATH):
			sublist = y[(index)*STEP:(index + BYTE_SIZE)*STEP]
			if not len(sublist): break
			avg = sum([abs(x) for x in sublist])/len(sublist)
			if (abs(avg) < THRESH):
				bmax = index
				break
			index = index + BYTE_SIZE
		if not bmax: bmax = index
		breaths[peak] = (bmin, bmax)
		bmin = None
		bmax= None
	return breaths


x,y = readAndExtract('30sleep.wav')
peaks = findPeaks(y)
breaths = findBreaths(x, y, peaks)
plot(x, y, peaks, breaths)