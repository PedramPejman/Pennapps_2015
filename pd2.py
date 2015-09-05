from scipy.io import wavfile
from matplotlib import pyplot as plt
import numpy as np
import peakutils
from peakutils.plot import plot as pplot
from matplotlib import pyplot
from scipy.signal import butter, lfilter, freqz

##GLOBALS
order = 6
fs = 30.0
cutoff = 3.667  

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
	x = np.arange(len(y))/float(samplerate)
	#Handle both mono and stereo audio
	if len(y[:]) == 2:
		y = y[0:len(y)-1:100, 1]
	else:
		y = y[0:len(y)-1:100]
	y = butter_lowpass_filter(y, cutoff, fs, order)
	x = x[0:len(x)-1:100]
	return x, y

def findPeaks(y):
	return peakutils.indexes(y, thres=0.1, min_dist=100)	

def plot(x, y, indexes):
	pyplot.figure(figsize=(10,6))
	pplot(x, y, indexes)
	pyplot.title('Find peaks')
	pyplot.show()

x,y = readAndExtract('30sleep.wav')
peaks = findPeaks(y)
plot(x, y, peaks)