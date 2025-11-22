from typing import List, Tuple, Dict

class BankersAlgorithm:
    def __init__(self, allocation: List[List[int]], maximum: List[List[int]], available: List[int]):
        self.allocation=allocation
        self.maximum=maximum
        self.available=available[:]
        self.n=len(allocation)
        self.m=len(allocation[0]) if self.n>0 else 0
        self.need=self._compute_need()

    def _compute_need(self):
        need=[]
        for i in range(self.n):
            need.append([self.maximum[i][j]-self.allocation[i][j] for j in range(self.m)])
        return need

    def state(self)->Dict:
        return {"Allocation":self.allocation,"Max":self.maximum,"Need":self.need,"Available":self.available}

    def is_safe_state(self)->Tuple[bool,List[int],List[Dict]]:
        work=self.available[:]
        finish=[False]*self.n
        seq=[]
        trace=[]
        while True:
            progress=False
            for i in range(self.n):
                if not finish[i]:
                    if all(self.need[i][j] <= work[j] for j in range(self.m)):
                        trace.append({"process":i,"work_before":work[:],"need":self.need[i][:],"allocation":self.allocation[i][:]})
                        for j in range(self.m):
                            work[j]+=self.allocation[i][j]
                        finish[i]=True
                        seq.append(i)
                        progress=True
            if not progress:
                break
        return all(finish), seq, trace

    def request(self, pid:int, req:List[int])->Tuple[bool,str]:
        if any(req[j]>self.need[pid][j] for j in range(self.m)):
            return False,"请求超过该进程最大需求(Need)"
        if any(req[j]>self.available[j] for j in range(self.m)):
            return False,"资源当前不可用(Available)"
        orig_av=self.available[:]
        orig_alloc=[r[:] for r in self.allocation]
        orig_need=[r[:] for r in self.need]
        for j in range(self.m):
            self.available[j]-=req[j]
            self.allocation[pid][j]+=req[j]
            self.need[pid][j]-=req[j]
        safe, seq,_ = self.is_safe_state()
        if safe:
            return True, f"请求批准，安全序列: {seq}"
        else:
            self.available=orig_av
            self.allocation=orig_alloc
            self.need=orig_need
            return False,"请求导致不安全，已回滚"