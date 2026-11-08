"""Exports test windows + Python reference results for the C test (run from fw/)."""
import re, sys, numpy as np, scipy.io as sio
from scipy.signal import resample_poly
from scipy.stats import kurtosis, skew
DATA="../modelo/out/AI-SED/cwru"
WIN,STEP,NB=1024,512,16
FILES={"sano":[97,98,99,100],"pista_int":[105,106,107,108],"bola":[118,119,120,121],"pista_ext":[130,131,132,133]}
def load(n):
    m=sio.loadmat(f"{DATA}/{n}.mat"); k=[k for k in m if k.startswith("X%03d"%n) and "DE_time" in k][0]
    return resample_poly(m[k].ravel(),10,9)
def features(w):
    w=w-np.mean(w); rms=np.sqrt(np.mean(w**2)); pk=np.max(np.abs(w))
    td=[rms,pk,pk/(rms+1e-12),kurtosis(w),skew(w),np.std(w)]
    sp=np.abs(np.fft.rfft(w*np.hanning(WIN)))/WIN
    fd=[np.log10(np.sum(b**2)+1e-12) for b in np.array_split(sp[1:],NB)]
    return np.array(td+fd,dtype=np.float32)
# weights from the very same header the C code includes
t=open("include/modelo_pesos.h").read()
def arr(name):
    body=re.search(r"static const float %s\[[^=]*=(.*?);\n"%name,t,re.S).group(1)
    return np.array(eval(body.replace("f","").replace("{","[").replace("}","]")),dtype=np.float64)
MEAN,SCALE,W1,B1,W2,B2,W3,B3=[arr(n) for n in "MEAN SCALE W1 B1 W2 B2 W3 B3".split()]
def predict(f):
    z=(f-MEAN)/SCALE; h=np.maximum(0,z@W1+B1); h=np.maximum(0,h@W2+B2); o=h@W3+B3
    p=np.exp(o-o.max()); p/=p.sum(); return int(p.argmax()),p
rng=np.random.default_rng(99)
W=[];Y=[];F=[];P=[];S=[]
scen=[("clean",None,1.0),("snr10",10,1.0),("snr0",0,1.0),("gain0.5",None,0.5),("gain2",None,2.0)]
for si,(nm,db,g) in enumerate(scen):
    for ci,c in enumerate(FILES):
        s=load(FILES[c][3])*g          # 3 HP load (never seen in training)
        if db is not None: s=s+rng.normal(0,np.sqrt(np.mean(s**2)/10**(db/10)),len(s))
        for i in range(0,len(s)-WIN+1,STEP):
            w=s[i:i+WIN].astype(np.float32); f=features(w.astype(np.float64)); p,_=predict(f)
            W.append(w);Y.append(ci);F.append(f);P.append(p);S.append(si)
W=np.array(W,np.float32);F=np.array(F,np.float32)
with open("data/ref.bin","wb") as fh:
    np.array([len(W)],np.int32).tofile(fh); W.tofile(fh); np.array(Y,np.int32).tofile(fh)
    F.tofile(fh); np.array(P,np.int32).tofile(fh); np.array(S,np.int32).tofile(fh)
for si,(nm,_,_) in enumerate(scen):
    m=np.array(S)==si; print(f"python {nm:8s}: n={m.sum():4d} acc={np.mean(np.array(P)[m]==np.array(Y)[m]):.4f}")
