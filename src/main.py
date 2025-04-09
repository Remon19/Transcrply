# -*- coding: utf-8 -*-
import argparse
import os
import sys
from utils.audio_utils import ExtractAudio
from processing import TranscripeToSRT

def main():
    
    argparser = argparse.ArgumentParser(description="Transcribe audio files to SRT format.")
    argparser.add_argument("audio_file", type=str, help="Path to the audio file to transcribe.")
    argparser.add_argument("--use_whisper", action="store_true", help="Use Whisper for transcription.")
    argparser.add_argument("--language", type=str, default="arabic", help="Language for transcription.")
    
    args = argparser.parse_args()
    audio_file = args.audio_file
    use_whisper = args.use_whisper
    language = args.language    
    convfilepath, error = ExtractAudio(audio_file)
    if not error:
        print(f"Extracted audio to {convfilepath}.wav")
        TranscripeToSRT(convfilepath+'.wav', use_whisper=use_whisper, language=language)
    else:
        print(f"Error extracting audio from {audio_file}.")
        sys.exit(1)
    # Clean up the extracted audio file
    os.remove(convfilepath+'.wav')
    print(f"Transcription completed. SRT file saved as {os.path.splitext(audio_file)[0]}.srt")
    
    
    
    
    
    
    
    
    
    
    
if __name__ == "__main__":
    main()