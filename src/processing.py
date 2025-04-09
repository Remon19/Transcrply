import math
import whisper
import torch
import librosa
import demucs
from os import path
from utils.audio_utils import GetAudioSegment, SplitOnSilence
from utils.segments_utils import HandleLessThanSec, SplitLongDuration
from utils.sub_utils import FormatTime, AdjustSrtIndex, BreakLongTranscription
from utils.misc import remove_directory

def Separate_Vocals(audiopath):
    curr_dir = '/ai-workspace/Remon/MediaTranscription'
    demucs.separate.main(["--two-stems", "vocals", "-n", "mdx_extra", f"{audiopath}"])
    print('done')
    vocalPath = curr_dir + '/separated/mdx_extra/' + path.splitext(path.basename(audiopath))[0] + '/vocals.wav'
    print(vocalPath)
    return vocalPath

def DevideAndRemoveMusic(filePath):
    fileName = path.splitext(filePath)[0] 
    duration = librosa.get_duration(filename=filePath)
    duration_limit = 1800
    start = 0
    overlap = 1
    parts = []
    if duration > duration_limit:
        parts_count = math.ceil(duration/duration_limit)
        for i in range(parts_count):
            end = start + duration_limit
            part = GetAudioSegment(fileName, f'd_{i}', start, end
                                    , duration_limit,duration_limit, 5)
            trials = 0
            while trials < 5:
                try:
                    part[0]['file'] = ExtractAudio(Separate_Vocals(part[0]['file']))[0]
                    parts.append(part)
                    break
                except:
                    trials +=1
                
            start = end - overlap
    else:
        parts.append([{'file':ExtractAudio(Separate_Vocals(filePath))[0],'start':0,'end':duration}])    
    return parts
    

whisper_model = None
device = 'cuda' if torch.cuda.is_available() else 'cpu'
def TranscripeWhisper(file, language='arabic'):
    global whisper_model

    # Load the model only if it hasn't been loaded yet
    if whisper_model is None:
        whisper_model = whisper.load_model("large-v3", device=device)

    audio = whisper.load_audio(file)
    audio = whisper.pad_or_trim(audio)
    mel = whisper.log_mel_spectrogram(audio, n_mels=128).to(whisper_model.device)
    options = whisper.DecodingOptions(language=language)
    result = whisper.decode(whisper_model, mel, options)
    # print(result.text)
    return {'text': result.text}


def CutAndGetSrt(file, idx,seg,duration_limit, start_offset,use_whisper:bool=False, language='arabic', char_limit:int=32, overlap=0.25,):
    fileName = path.splitext(file)[0]
    seg_file = GetAudioSegment(fileName, f'd_{idx}',seg['start']-overlap,seg['end']+overlap,limit=duration_limit,seg_length=duration_limit,over_lap=0)
    start = FormatTime(start_offset+ seg['start'])
    end = FormatTime(start_offset + seg['end'])
    # if detect_lang(seg_file[0]['file']) == 'en':
    #     print('using whisper')
    #     transcription_text = TranscripeWhisper(seg_file[0]['file'], language='arabic')
    # else:
    if language != 'arabic' or use_whisper:
        transcription = TranscripeWhisper(seg_file[0]['file'],language=language)
    else:
        transcription,error= transcript_file(seg_file[0]['file'],'speaker00',start='', end='')
        if error:
            transcription_text = '\n'
    transcription_text = transcription['text']
    # print(transcription_text)
    if len(transcription_text.rstrip()) == 0:
        return None
        # print(transcription_text) 
        # transcription_text = CorrectSpelling(transcription_text)
    if len(transcription_text) >= char_limit:
        transcription_text = BreakLongTranscription(transcription_text)
    # print(transcription_text)
    segment = f'{idx+1}\n{start} --> {end}\n{transcription_text}\n\n'
    print(segment)
    return segment

def TranscripeToSRT(file, use_whisper:bool=False, language:str='arabic', duration_limit=3.5, char_limit:int=32, overlap=0.25):
    fileName = path.splitext(file)[0]
    # os.mkdir(path.join(fileName,'/output/'))
    # os.chdir(path.join(fileName,'/output/'))
    parts = DevideAndRemoveMusic(file)
    with open(fileName + '.srt', 'w', encoding='utf-8') as srtFile:
        for part in parts:
            seg_ranges,_ = SplitOnSilence(part[0]['file']+'.wav')
            seg_ranges = HandleLessThanSec(seg_ranges)
            for i,seg in enumerate(seg_ranges):
                seg_duration = seg['end'] - seg['start']
                if seg_duration > 3.5:
                    split_segs = SplitLongDuration(seg,duration_limit)
                    for seg in split_segs:
                        try:
                            segment = CutAndGetSrt(part[0]['file'], i, seg, 5, part[0]['start'],use_whisper,language,char_limit,overlap)
                            srtFile.write(segment)
                        except:
                            continue
                else:
                    try:
                        segment = CutAndGetSrt(part[0]['file'], i, seg, 5, part[0]['start'],use_whisper,language, char_limit,overlap)       
                        srtFile.write(segment)  
                    except:
                        continue       
    AdjustSrtIndex(fileName + '.srt')
    for part in parts:
        remove_directory(path.dirname(part[0]['file']))
        # os.remove(path.dirname(part[0]['file'])+'.wav')
        