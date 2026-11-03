"""Synthesized sound effects (no samples needed). LIB holds the ready-made sounds."""
import numpy as np
SR=48000
rng=np.random.default_rng(7)
def env(n,att,dec):
    t=np.arange(n)/SR; return np.minimum(t/att,1)*np.exp(-np.maximum(t-att,0)/dec)
def lp(x,cut):
    y=np.zeros_like(x); s=0.0
    a=1-np.exp(-2*np.pi*np.asarray(cut)/SR)
    a=np.broadcast_to(a,x.shape)
    for i in range(len(x)): s+=a[i]*(x[i]-s); y[i]=s
    return y
def whoosh(d=0.45):
    n=int(d*SR); t=np.arange(n)/n
    x=rng.standard_normal(n)
    cut=300+5000*np.sin(np.pi*t)**2
    y=lp(x,cut)-lp(lp(x,cut),200)
    e=np.sin(np.pi*t)**1.5
    y=y*e; return 0.9*y/np.abs(y).max()
def ding(d=1.2):
    n=int(d*SR); t=np.arange(n)/SR
    y=(np.sin(2*np.pi*1568*t)+0.6*np.sin(2*np.pi*2352*t)+0.35*np.sin(2*np.pi*3136*t))*np.exp(-t/0.35)*np.minimum(t/0.003,1)
    y2=np.zeros(n); k=int(0.09*SR)
    y2[k:]=(np.sin(2*np.pi*2093*t[:n-k])+0.5*np.sin(2*np.pi*3136*t[:n-k]))*np.exp(-t[:n-k]/0.45)*np.minimum(t[:n-k]/0.003,1)
    y=y+y2; return 0.9*y/np.abs(y).max()
def boom(d=1.1):
    n=int(d*SR); t=np.arange(n)/SR
    f=45+110*np.exp(-t/0.08); ph=2*np.pi*np.cumsum(f)/SR
    y=np.sin(ph)*np.exp(-t/0.35)*np.minimum(t/0.004,1)
    y+=0.5*lp(rng.standard_normal(n),900)*np.exp(-t/0.05)
    y=np.tanh(2.2*y); return 0.95*y/np.abs(y).max()
def pop(d=0.09):
    n=int(d*SR); t=np.arange(n)/SR
    f=500+900*t/d; y=np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t/0.025)
    return 0.8*y/np.abs(y).max()
def riser(d=1.0):
    n=int(d*SR); t=np.arange(n)/n
    x=rng.standard_normal(n); y=lp(x,400+7000*t**2)
    y=y*(t**2); return 0.8*y/np.abs(y).max()
def bleep(d):
    t=np.arange(int(d*SR))/SR; return 0.5*np.sin(2*np.pi*1000*t)
def bubble(d=0.16, f0=380, f1=1100):
    n=int(d*SR); t=np.arange(n)/SR
    f=f0+(f1-f0)*(t/d)**0.6; y=np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t/0.045)*np.minimum(t/0.004,1)
    return 0.8*y/np.abs(y).max()
def sparkle(d=1.3):
    n=int(d*SR); t=np.arange(n)/SR; y=np.zeros(n)
    for k,f in enumerate([1318.5,1568,1975.5,2637,3136]):
        o=int(k*0.055*SR); tt=t[:n-o]
        y[o:]+= (np.sin(2*np.pi*f*tt)+0.3*np.sin(2*np.pi*2*f*tt))*np.exp(-tt/0.28)*np.minimum(tt/0.002,1)*(0.9-0.1*k)
    return 0.85*y/np.abs(y).max()
def thump(d=0.7):
    n=int(d*SR); t=np.arange(n)/SR
    f=48+70*np.exp(-t/0.05); y=np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t/0.22)*np.minimum(t/0.006,1)
    return 0.9*y/np.abs(y).max()
def softwhoosh(d=0.5):
    n=int(d*SR); t=np.arange(n)/n
    x=rng.standard_normal(n); y=lp(x,250+2600*np.sin(np.pi*t)**2); y=y-lp(y,300)
    y*=np.sin(np.pi*t)**2; return 0.8*y/np.abs(y).max()
LIB={"bubble":bubble(),"bubble_hi":bubble(0.14,600,1600),"sparkle":sparkle(),"thump":thump(),"softwhoosh":softwhoosh(),"whoosh":whoosh(),"ding":ding(),"boom":boom(),"pop":pop(),"riser":riser()}
