import os
import subprocess
import wave
import math
import ffmpeg
from pathlib import Path
from pydub import AudioSegment
from pydub.silence import detect_nonsilent, split_on_silence



def ExtractAudio(filepath):
    directory = os.path.dirname(filepath)  # directory of file
    convfilepath = directory + '/' + Path(filepath).stem + '_conv'
    # command = "ffmpeg -hide_banner -loglevel error -y  -i {} -ab 256k -ac 1 -ar 16000 -vn {}.wav".format(
    #     filepath, convfilepath)
    # result = subprocess.run(command, shell=True, stdout=subprocess.PIPE)
    try:
        ffmpeg.input(filepath).output(
            convfilepath,
            ab='256k',
            ac=1,
            ar=16000,
            vn=None
        ).overwrite_output().run(quiet=True)
        return convfilepath, 0  # success
    except ffmpeg.Error as e:
        print("FFmpeg error:", e.stderr.decode() if e.stderr else str(e))
        return None, 1  # failure


def GetAudioSegment(filename, segment_number, start, end, limit,seg_length, over_lap=0.5):
    file_duration = end
    with wave.open(filename + '.wav', "rb") as infile:
        # get file data
        nchannels = infile.getnchannels()
        sampwidth = infile.getsampwidth()
        framerate = infile.getframerate()
        AudioSegments = []
        seg_lengths = []
        patterns_count = math.ceil(limit/seg_length)
        # print(patterns_count)
        for p in range(patterns_count-1):
            seg_lengths.append(seg_length)
        last_segment_length = limit - (patterns_count-1)*seg_length
        if last_segment_length:
            seg_lengths.append(last_segment_length)
        # print(seg_lengths)
        i = 0
        while start < file_duration:
            if i>0:
                start = start - over_lap
            if start < 0:
                start = 0
            # set position in wave to start of segment
            infile.setpos(math.floor((start) * framerate))
            # set segment length in seconds
            seg_length = seg_lengths[i % patterns_count]
            # if the last segment end is exceeding the original end, set it to the original
            if (start + seg_length) > file_duration:
                seg_length = file_duration - start
            end = start + seg_length
            # extract data
            data = infile.readframes(math.ceil((seg_length) * framerate))
            AudioSegment_Name = f"{filename}_{segment_number}_{i}"+'.wav'
            # get new start and end time
            #new_start = str(datetime.timedelta(seconds=round(start + i * limit)))
            #new_end = str(datetime.timedelta(seconds=round((start + i * limit) + seg_length)))
            # write the extracted data to a new file
            with wave.open(AudioSegment_Name, 'w') as outfile:
                outfile.setnchannels(nchannels)
                outfile.setsampwidth(sampwidth)
                outfile.setframerate(framerate)
                outfile.setnframes(int(len(data) / sampwidth))
                outfile.writeframes(data)
            AudioSegments.append({'file': AudioSegment_Name, 'start': start, 'end': end})
            start = start + seg_length
            end = start + seg_length
            i=i+1
    return AudioSegments


def SplitOnSilence(filePath,min_silence_len:int=250):
    sound = AudioSegment.from_wav(filePath)
    fileName = os.path.splitext(filePath)[0]
    audio_ranges = detect_nonsilent(sound, min_silence_len=min_silence_len, silence_thresh=-40 )
    audio_chunks = split_on_silence(sound, min_silence_len=min_silence_len, silence_thresh=-40 )
    audio_ranges_in_sec = []
    chunk_files = []
    for i, data in enumerate(zip(audio_ranges,audio_chunks)):
        start,end,chunk = data[0][0], data[0][1], data[1]
        
        # output_file = os.path.dirname(fileName) + ("/chunk{0}.wav".format(i))
        # chunk_files.append(output_file)
        # chunk.export(output_file, format="wav")
        audio_ranges_in_sec.append({'start':start/1000, 'end':end/1000})
    return audio_ranges_in_sec, chunk_files