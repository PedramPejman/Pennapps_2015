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
	y = normalize(y)[0]
	y = butter_lowpass_filter(y, cutoff, fs, order)
	x = x[0:len(x)-1:STEP]
	return x, y

def findPeaks(y):
	return peakutils.indexes(y, thres=0.1, min_dist=44100)

def plot(x, y, indexes, breaths):
	pyplot.figure(figsize=(10,6))
	pplot(x, y, indexes)
	pyplot.title('Find peaks')
	#show breaths
	for breath in breaths:
		pyplot.axvspan(breath[2], breath[3], color='y', alpha=0.5, lw=0)
	
	pyplot.show()

def normalize(a, axis=-1, order=2):
    l2 = np.atleast_1d(np.linalg.norm(a, order, axis))
    l2[l2==0] = 1
    return a / np.expand_dims(l2, axis)

def findBreaths(x, y, peaks):
	breaths = []
	MAX_BREATH = 44100
	BYTE_SIZE = 5000
	THRESH = .03
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
		breaths.append([peak, y[peak], bmin, bmax])
		bmin = None
		bmax= None
	return aggregate(breaths)

def aggregate(breaths):
	i = 0
	while i < len(breaths)-1:
		if (breaths[i][3] > breaths[i+1][2]):
			breaths[i][3] = breaths[i+1][3]
			breaths[i][1] = max(breaths[i][1], breaths[i+1][1])
			del breaths[i+1]
		i = i + 1
	return breaths

def writeToFile(file, breaths):
	file = open(file, 'w')
	for breath in breaths:
		for val in breath:
			file.write(str(val)+", ")
			print(val)
		file.write("\n")
		print()
	file.close()


x,y = readAndExtract('apnea.wav')
peaks = findPeaks(y)
breaths = findBreaths(x, y, peaks)
writeToFile('out.txt', breaths)
plot(x, y, peaks, breaths)
