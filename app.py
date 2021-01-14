# rest components
from flask import Flask
from flask_restful import Resource, Api, reqparse
import json
from flask_cors import CORS

# import other python files
import recorder
import translator


app = Flask(__name__)
api = Api(app)

# cors configuration
CORS(app)

class Recordings(Resource):
    def post(self):
        #parser for reading data which gets provided from the front end (language selection)
        parser = reqparse.RequestParser()  # initialize
        
        parser.add_argument('langObj', required=True)
        parser.add_argument('startOrStopRecording')
        parser.add_argument('playOrPauseAudio')
        parser.add_argument('filename')
        parser.add_argument('deleteAll')
        
        args = parser.parse_args()  # parse arguments to dictionary
        
        langObjStr = args.langObj.replace("'", '"') # convert json string to json obj representation
        langObj = json.loads(langObjStr)


        startStopRec = str(args.startOrStopRecording)
        playPauseAudio = str(args.playOrPauseAudio)
        filename = str(args.filename)

        deleteAllStr = str(args.deleteAll)


        if(deleteAllStr == 'true'):
            voiceRecordingsDelete()
            return {'request': 'delete complete'}, 200
        else:
            voiceRecording(langObj, startStopRec, playPauseAudio, filename)

            recFileNameArrStr = ','.join(recorder.getRecordingFileNames())

            if(startStopRec == 'start' or startStopRec == 'stop'):
                return {'request': 'recording ' + 'stop', 'data': recFileNameArrStr}, 200 
            elif(playPauseAudio == 'play' or playPauseAudio == 'pause'):
                return {'request': 'playback ' + 'pause'}, 200 
            else: 
                return {'request': 'error'}, 500


    # return the list of available recordings 
    def get(self):
        # get file names and create string for transfer
        recFileNameArrStr = ','.join(recorder.getRecordingFileNames())
        return {'data' : recFileNameArrStr}



class Translations(Resource):
    def post(self):
        #parser for reading data which gets provided from the front end (language selection)
        parser = reqparse.RequestParser()  # initialize
        parser.add_argument('filename')
        parser.add_argument('deleteAll')
        args = parser.parse_args()  # parse arguments to dictionary
        

        if(str(args.deleteAll) == 'true'):
            translator.deleteAllTranslations()
            return {'request': 'delete complete'}, 200
        else:
            translationData = translator.speechToText(str(args.filename))

            if translationData == 'speech recognition failed':
                return {'request': 'translation failed', 'data': translationData}, 200
            else:
                translationData = json.dumps({
                    "srcFilename": str(args.filename),
                    "textSrc": translationData[0], 
                    "filenameSrc": translationData[1], 
                    "textDest": translationData[2], 
                    "filenameDest": translationData[3]
                })
                return {'request': 'translation complete', 'data': translationData}, 200 



# class for playback of tts files
class TTS(Resource):
    def post(self):
        #parser for reading data which gets provided from the front end (language selection)
        parser = reqparse.RequestParser()  # initialize
        parser.add_argument('pathToFile')
        args = parser.parse_args()  # parse arguments to dictionary
        
        recorder.playTTS(str(args.pathToFile))

        return {'request': 'TTS playback stop'}, 200



# endpoint for rest client
api.add_resource(Recordings, '/recordings')  # '/recordings' is our entry point for voice input
api.add_resource(Translations, '/translations')  # '/translations' is our entry point for translation requests
api.add_resource(TTS, '/tts')  # '/translations' is our entry point for translation requests



# get pre-existing recordings in directory
recorder.getRecordingsInDir()



# voice recording
def voiceRecording(langObj, startStopRec, playPauseAudio, filename):
    if (startStopRec == 'start'):
        recorder.startRecording(langObj['in'])
    elif (startStopRec == 'stop'):
        # after recording query file name and return it to frontend 
        recorder.stopRecording(langObj['in'])

    if (playPauseAudio == 'play'):
        recorder.playAudio(filename)
    elif (playPauseAudio == 'pause'):
        recorder.pauseAudio()


def voiceRecordingsDelete():
    recorder.deleteAllRecordings()






# run Flask Backend App
if __name__ == '__main__':
    app.run()