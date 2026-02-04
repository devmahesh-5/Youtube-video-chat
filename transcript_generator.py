from youtube_transcript_api import YouTubeTranscriptApi
class Transcript_Generator:
    def __init__(self,videoId):
        self.videoId = videoId

    def generate_transcript(self):
        ytt_api = YouTubeTranscriptApi()
        fetched_transcript = ytt_api.fetch(self.videoId)
        # print(fetched_transcript)

        if(fetched_transcript):
            return fetched_transcript
        else:
            return None
        

    

        