def HandleLessThanSec(audio_ranges:list):
    new_audio_ranges = []
    idx = None
    for i in range(len(audio_ranges)):
        if i == idx:
            continue
        elif i == (len(audio_ranges) - 1):
            new_audio_ranges.append(audio_ranges[i])
        else:
            audio_range = audio_ranges[i]
            seg_duration = audio_range['end'] - audio_range['start']
            if seg_duration < 1:
                # print(seg_duration)
                end = audio_range['start'] + 1
                # print('end',end)
                while i < (len(audio_ranges) - 1) and end > audio_ranges[i+1]['start']:
                    end = audio_ranges[i+1]['end']
                    # print(i)
                    i += 1
                idx = i
                new_audio_ranges.append({'start':audio_range['start'], 'end':end})
            else:
                new_audio_ranges.append(audio_ranges[i])
                i += 1
            
    return new_audio_ranges

def SplitLongDuration(seg, duration_limit:int=3.5):
    new_segments = []
    seg_duration = seg['end'] - seg['start']
    gap = 0.025
    new_segments_count = int(seg_duration/duration_limit)
    start = seg['start'] 
    for i in range(new_segments_count):
        end = start + duration_limit 
        new_segments.append({'start':start, 'end':end})
        start = end + gap 
    if (seg['end'] - start) < 1:
        new_segments[-1]['end'] = seg['end']
    else:
        new_segments.append({'start':start,'end':seg['end']})
    return new_segments