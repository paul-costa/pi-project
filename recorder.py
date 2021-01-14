from datetime import datetime
import re

# recording
import sounddevice as sd
from scipy.io import wavfile
import time
import numpy as np

# playback
import soundfile as sf

# delete
import os


recording = False

fs = 44100      # Sample rate
seconds = 60     # max duration 60

lengthOfRecording = 0

myrecordingsNameArr = []    # arr with names of wav files
myrecordingsArr = []        # arr for recorder function/info


# audio recording functions
def startRecording(inputLang):
    myrecordingsArr.append(sd.rec(int(seconds * fs), samplerate=fs, channels=2))

    # call stop after 1 minute automatically 
    global lengthOfRecording
    lengthOfRecording=0

    # address global recording bool for stopping
    global recording
    recording = True
    
    while(recording):
        lengthOfRecording += 1
        print("recording seconds left: " + str(seconds-lengthOfRecording))
        time.sleep(1)
        
        if(lengthOfRecording==seconds):
            return stopRecording(inputLang)


def stopRecording(inputLang):
    # address global recording bool for stopping
    global recording
    recording = False

    datetimeString = re.sub('[^0-9]', '', str(datetime.now())) + "." + inputLang + ".wav"
    myrecordingsNameArr.append(datetimeString)
    
    # saving wavs got compression/data type errors -> conversion from float into int (https://stackoverflow.com/questions/52249985/python-speech-recognition-tool-does-not-recognize-wav-file)
    y = (np.iinfo(np.int32).max * (myrecordingsArr[-1]/np.abs(myrecordingsArr[-1]).max())).astype(np.int32)
    wavfile.write('recordings/'+myrecordingsNameArr[-1], fs, y)  # Save as WAV file



# audio playback functions
def playAudio(filename):
    # print('\nplayback started')
    fileFound = True

    # filename should either be 'last' (recording playback) or specified filename
    if filename == 'last' or filename == 'null':
        filename = 'recordings/'+myrecordingsNameArr[-1] # getting last file in array
    else:
        if filename in myrecordingsNameArr:                  # check if requested recording exists in recordingsarray
            filename = 'recordings/'+filename                # getting request recording
        else: 
            fileFound = False

    # get data for audio file and play
    if fileFound:
        data, fs = sf.read(filename, dtype='float32')  
        sd.play(data, fs)
        sd.wait()
    else:
        raise Exception('Requested recording file not found')


def playTTS(pathToFile):
    # XXX implement TTS playback (maybe send TTS wav files to frontend?)
    print('TTS playback to be implemented')



def pauseAudio():
    sd.stop()


def deleteAllRecordings():
    global myrecordingsNameArr
    global myrecordingsArr
    
    for recordingName in myrecordingsNameArr:
        os.remove('recordings/'+recordingName)
    
    myrecordingsArr = []
    myrecordingsNameArr = []



# functions for accessing and manipulatig wav files and file mgmt

# scan dir for .wav recordings
def getRecordingsInDir():
    for filename in os.listdir('recordings/'):
        myrecordingsNameArr.append(filename)       # put them in the array with filenames

# returns list of wav filenames on server
def getRecordingFileNames():
    return myrecordingsNameArr