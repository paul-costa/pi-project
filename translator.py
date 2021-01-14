# import tts & stt library, google translator
from gtts import gTTS
import speech_recognition as sr
from googletrans import Translator      # alpha version needed: googletrans==3.1.0a0        https://stackoverflow.com/questions/52455774/googletrans-stopped-working-with-error-nonetype-object-has-no-attribute-group

# fsmgmt libraries
import os
import shutil                           # operating system library for enhanced file structure manipulation




# function for extracting text from recording - returns list with [extractedText as string, inputLanguage as string]
def speechToText(filename):
    file = sr.AudioFile('recordings/' + filename)   # read in audio file using speech_recognition functions

    # init stt engine
    r = sr.Recognizer()

    with file as source:                            # convert file into py class 'speech_recognition.AudioData'
        audio = r.record(source)

    inputLang = filename.split('.')[1]
    outputLang = ''



    # input language specification by rfc5646   https://tools.ietf.org/html/rfc5646
    if(inputLang == 'en'):
        inputLangRfc = 'en-US'
        outputLang = 'de'
    elif(inputLang == 'de'):
        inputLangRfc = 'de-DE'
        outputLang = 'en'
    else:
        inputLangRfc = None
        outputLang = None

    # run recognition
    extractedText = ''
    
    try:
        extractedText = r.recognize_google(audio, None, inputLangRfc) 
    except:
        return 'speech recognition failed'


    
    # call translate function
    return translate(filename, extractedText, outputLang, inputLang)


# google translate based function with automatic input language detection
def translate(filename, textToTranslate, destinationLang, srcLang):
    gTranslator = Translator()
    gTranslateData = gTranslator.translate(textToTranslate, destinationLang, srcLang)

    return writeToFileSystem(filename, gTranslateData)



# function which writes translated files (type declares whether text or audio) to filesystem
def writeToFileSystem(filename, gTranslateData):
    # create directory for translation
    dirPath = 'translations/'+filename.split('.')[0]

    if(os.path.exists(dirPath)):    # check if directory already exists
        shutil.rmtree(dirPath)      # delete directory and containing files
    
    os.mkdir(dirPath)


    # create directories for de and en
    os.mkdir(dirPath+'/en')
    os.mkdir(dirPath+'/de')



    return writeTextFiles(dirPath, filename.split('.')[0], gTranslateData)



# creates text files in directory with data from google translate operation and returns array [srcFilePath, destFilePath]
def writeTextFiles(dirPath, filename, gTranslateData):
    srcLang = gTranslateData.src
    destLang = gTranslateData.dest
    srcText = gTranslateData.extra_data['translation'][0][1]
    destText = gTranslateData.text

    # create file paths
    srcFilePath = dirPath + '/' + srcLang + '/'
    destFilePath = dirPath + '/' + destLang + '/'
    
    # create files
    srcFile = open(srcFilePath + filename + '.' + srcLang + '.txt', 'x', encoding='utf-8')
    destFile = open(destFilePath + filename + '.' + destLang + '.txt', 'x', encoding='utf-8')
    
    # write text in files
    srcFile.write(remove_umlaut(srcText).capitalize() + '.')
    destFile.write(remove_umlaut(destText).capitalize() + '.')
    
    # close files again
    srcFile.close()
    destFile.close()

    return writeAudioFiles([srcFilePath, destFilePath])


# create tts audio files from all text files in the given directory
def writeAudioFiles(arrOfDirPaths):
    translationsFiles = []
    
    for dirPath in arrOfDirPaths:
        for file in os.listdir(dirPath):
            text = open(dirPath + file, 'r').read()             # open text file and get string
            tts = gTTS(text, lang=file.split('.')[1])   # tts string from text file with resp. language
            tts.save(dirPath + file[:-4] + '.wav')    # write it to wav

            translationsFiles.append(text)
            translationsFiles.append(dirPath + file[:-4] + '.wav')

    # return object with information on directory and filenames
    return translationsFiles



def deleteAllTranslations():
    shutil.rmtree('translations')
    os.mkdir('translations')



# source: https://gist.github.com/johnberroa/cd49976220933a2c881e89b69699f2f7
def remove_umlaut(string):
    u = 'ü'.encode()
    U = 'Ü'.encode()
    a = 'ä'.encode()
    A = 'Ä'.encode()
    o = 'ö'.encode()
    O = 'Ö'.encode()
    ss = 'ß'.encode()

    string = string.encode()
    string = string.replace(u, b'ue')
    string = string.replace(U, b'Ue')
    string = string.replace(a, b'ae')
    string = string.replace(A, b'Ae')
    string = string.replace(o, b'oe')
    string = string.replace(O, b'Oe')
    string = string.replace(ss, b'ss')

    string = string.decode('utf-8')
    return string

    


# speechToText('20210106223206023933.en.wav')
# speechToText('20210106223752541062.de.wav')