from dataclasses import dataclass
from typing import List, Optional, Dict, Any

@dataclass
class StepRecord:
    index: int
    page: int
    frames: List[Optional[int]]
    hit: bool
    replaced_index: Optional[int]
    algorithm_state: Dict[str, Any]

def simulate_fifo(pages: List[int], frame_count: int) -> List[StepRecord]:
    frames = [None]*frame_count


    ptr = 0
    steps=[]
    for i,p in enumerate(pages):
        hit = p in frames
        replaced=None
        if not hit:
            if None in frames:
                idx = frames.index(None)
                frames[idx]=p
                replaced=idx
            else:
                replaced=ptr
                frames[ptr]=p
                ptr = (ptr+1)%frame_count
        steps.append(StepRecord(i,p,frames.copy(),hit,(replaced if not hit else None),{"fifo_ptr":ptr}))
    return steps

def simulate_lru(pages: List[int], frame_count:int)->List[StepRecord]:
    frames=[None]*frame_count
    last_used={}
    steps=[]
    for i,p in enumerate(pages):
        hit = p in frames
        replaced=None
        if hit:
            last_used[p]=i
        else:
            if None in frames:
                idx=frames.index(None)
                frames[idx]=p
                replaced=idx
                last_used[p]=i
            else:
                lru_page=min(frames, key=lambda x:last_used.get(x,-1))
                idx=frames.index(lru_page)
                frames[idx]=p
                replaced=idx
                last_used[p]=i
        steps.append(StepRecord(i,p,frames.copy(),hit,(replaced if not hit else None),{"last_used":last_used.copy()}))
    return steps

def simulate_clock(pages: List[int], frame_count:int)->List[StepRecord]:
    frames=[None]*frame_count
    use=[0]*frame_count
    hand=0
    steps=[]
    for i,p in enumerate(pages):
        hit = p in frames
        replaced=None
        if hit:
            idx=frames.index(p)
            use[idx]=1
        else:
            if None in frames:
                idx=frames.index(None)
                frames[idx]=p
                use[idx]=1
                replaced=idx
            else:
                while True:
                    if use[hand]==0:
                        replaced=hand
                        frames[hand]=p
                        use[hand]=1
                        hand=(hand+1)%frame_count
                        break
                    else:
                        use[hand]=0
                        hand=(hand+1)%frame_count
        steps.append(StepRecord(i,p,frames.copy(),hit,(replaced if not hit else None),{"clock_hand":hand,"use":use.copy()}))
    return steps

ALGO_MAP={"FIFO":simulate_fifo,"LRU":simulate_lru,"CLOCK":simulate_clock}

def generate_steps(algo:str, seq:List[int], frames:int)->List[StepRecord]:
    if algo not in ALGO_MAP: raise ValueError("Unsupported algorithm")
    return ALGO_MAP[algo](seq, frames)