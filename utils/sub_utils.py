import pysrt
import re


def FormatTime(seconds:float):
    miliseconds = (seconds - int(seconds)) * 1000
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)

    return "%02d:%02d:%02d,%03d" % (hours, minutes, seconds, miliseconds)

def AdjustSrtIndex(fileName):
    subs = pysrt.open(fileName)
    with open(fileName, 'w', encoding='utf-8') as srtFile:
        for i, sub in enumerate(subs, start=1):
            sub.index = i
            segment = f"{sub.index}\n{sub.start} --> {sub.end}\n{sub.text}\n\n"        
            srtFile.write(segment)
            
def BreakLongTranscription(transcription_text):
    words = transcription_text.split()
    line1 = ' '.join(words[:len(words)//2])
    line2 = ' '.join(words[len(words)//2:]) 
    return line1+'\n'+line2         