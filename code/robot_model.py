"""Deterministic planar 2R / five-bar models, SI units, y positive upward."""
from dataclasses import dataclass
import numpy as np


@dataclass(frozen=True)
class Parameters:
    l1: float = .32
    l2: float = .28
    m1: float = .8
    m2: float = .6
    mp: float = .25
    d: float = .36
    gravity: float = 9.81
    duration: float = 4.

    @property
    def i1(self): return self.m1*self.l1**2/12
    @property
    def i2(self): return self.m2*self.l2**2/12


P = Parameters()
A = np.array([-P.d/2, 0.])
B = np.array([P.d/2, 0.])


def perp(v): return np.array([-v[1], v[0]])
def cross(a,b): return a[0]*b[1]-a[1]*b[0]
def unit(a): return np.array([np.cos(a),np.sin(a)])


def fk(q, origin=A):
    return origin + P.l1*unit(q[0]) + P.l2*unit(q[0]+q[1])


def ik(point, origin=A, elbow=-1):
    x,y=np.asarray(point)-origin
    c=(x*x+y*y-P.l1**2-P.l2**2)/(2*P.l1*P.l2)
    if abs(c)>1+1e-12: raise ValueError('Point outside branch workspace')
    q2=elbow*np.arccos(np.clip(c,-1,1))
    q1=np.arctan2(y,x)-np.arctan2(P.l2*np.sin(q2),P.l1+P.l2*np.cos(q2))
    return np.array([q1,q2])


def jac(q):
    u1=perp(unit(q[0])); u2=perp(unit(q.sum()))
    return np.column_stack((P.l1*u1+P.l2*u2,P.l2*u2))


def jacdot(q,dq):
    v1=-unit(q[0])*dq[0]; v2=-unit(q.sum())*dq.sum()
    return np.column_stack((P.l1*v1+P.l2*v2,P.l2*v2))


def mass(q,payload=P.mp):
    r1=P.l1/2; r2=P.l2/2
    a=P.i1+P.i2+P.m1*r1*r1+P.m2*(P.l1**2+r2*r2)+payload*(P.l1**2+P.l2**2)
    b=P.m2*P.l1*r2+payload*P.l1*P.l2
    d=P.i2+P.m2*r2*r2+payload*P.l2**2
    c=np.cos(q[1])
    return np.array([[a+2*b*c,d+b*c],[d+b*c,d]])


def coriolis(q,dq,payload=P.mp):
    b=P.m2*P.l1*P.l2/2+payload*P.l1*P.l2
    h=b*np.sin(q[1])
    return np.array([[-h*dq[1],-h*dq.sum()],[h*dq[0],0.]])


def grav(q,payload=P.mp):
    a=P.m1*P.l1/2+P.m2*P.l1+payload*P.l1
    b=P.m2*P.l2/2+payload*P.l2
    return P.gravity*np.array([a*np.cos(q[0])+b*np.cos(q.sum()),b*np.cos(q.sum())])


def inverse_lagrange(q,dq,ddq,payload=P.mp):
    return mass(q,payload)@ddq+coriolis(q,dq,payload)@dq+grav(q,payload)


def inverse_newton_euler(q,dq,ddq,payload=P.mp):
    """Independent planar outward acceleration / inward wrench recursion."""
    r1=P.l1/2*unit(q[0]); r12=P.l1*unit(q[0])
    r2=P.l2/2*unit(q.sum()); rt=P.l2*unit(q.sum())
    a1=ddq[0]*perp(r1)-dq[0]**2*r1
    ao2=ddq[0]*perp(r12)-dq[0]**2*r12
    a2=ao2+ddq.sum()*perp(r2)-dq.sum()**2*r2
    at=ao2+ddq.sum()*perp(rt)-dq.sum()**2*rt
    g=np.array([0.,-P.gravity])
    f1=P.m1*(a1-g); f2=P.m2*(a2-g); ft=payload*(at-g)
    tau2=P.i2*ddq.sum()+cross(r2,f2)+cross(rt,ft)
    tau1=P.i1*ddq[0]+cross(r1,f1)+tau2+cross(r12,f2+ft)
    return np.array([tau1,tau2])


def kinetic(q,dq,payload=P.mp): return float(.5*dq@mass(q,payload)@dq)
def potential(q,payload=P.mp):
    a=P.m1*P.l1/2+P.m2*P.l1+payload*P.l1
    b=P.m2*P.l2/2+payload*P.l2
    return P.gravity*(a*np.sin(q[0])+b*np.sin(q.sum()))


def path(t, near_singular=False):
    s=np.clip(t/P.duration,0.,1.)
    h=10*s**3-15*s**4+6*s**5
    hd=(30*s*s-60*s**3+30*s**4)/P.duration
    hdd=(60*s-180*s*s+120*s**3)/P.duration**2
    phi=2*np.pi*h; w=2*np.pi*hd; alpha=2*np.pi*hdd
    cy,ry=(.34,.035) if near_singular else (.38,.025)
    point=np.array([.04*np.cos(phi),cy+ry*np.sin(phi)])
    dp=np.array([-.04*np.sin(phi)*w,ry*np.cos(phi)*w])
    ddp=np.array([-.04*(np.cos(phi)*w*w+np.sin(phi)*alpha),
                   ry*(-np.sin(phi)*w*w+np.cos(phi)*alpha)])
    return point,dp,ddp


def branch_state(point,dp,ddp,origin=A,elbow=-1):
    q=ik(point,origin,elbow); j=jac(q)
    dq=np.linalg.solve(j,dp)
    ddq=np.linalg.solve(j,ddp-jacdot(q,dq)@dq)
    return q,dq,ddq


def serial_state(t): return branch_state(*path(t))


def parallel_kinematics(point):
    ql=ik(point,A,-1); qr=ik(point,B,1)
    cl=A+P.l1*unit(ql[0]); cr=B+P.l1*unit(qr[0])
    el=(point-cl)/P.l2; er=(point-cr)/P.l2
    amat=np.vstack((el,er))
    bmat=np.diag([P.l1*el@perp(unit(ql[0])),P.l1*er@perp(unit(qr[0]))])
    jp=np.linalg.solve(amat,bmat)
    return ql,qr,amat,bmat,jp


def parallel_fk(theta,upper=True):
    cl=A+P.l1*unit(theta[0]); cr=B+P.l1*unit(theta[1])
    delta=cr-cl; distance=np.linalg.norm(delta)
    if distance<1e-12 or distance>2*P.l2+1e-12: raise ValueError('No isolated real circle intersection')
    mid=(cl+cr)/2
    offset=np.sqrt(max(0.,P.l2**2-distance**2/4))*perp(delta/distance)
    candidates=np.array([mid+offset,mid-offset])
    return candidates[np.argmax(candidates[:,1]) if upper else np.argmin(candidates[:,1])]


def parallel_inverse(point,dp,ddp):
    states=[branch_state(point,dp,ddp,A,-1),branch_state(point,dp,ddp,B,1)]
    force=P.mp*(ddp-np.array([0.,-P.gravity]))
    mx=P.mp*np.eye(2); gx=np.array([0.,P.mp*P.gravity])
    for q,dq,ddq in states:
        ji=np.linalg.inv(jac(q))
        force+=ji.T@inverse_lagrange(q,dq,ddq,payload=0.)
        mx+=ji.T@mass(q,payload=0.)@ji
        gx+=ji.T@grav(q,payload=0.)
    *_,jp=parallel_kinematics(point)
    return jp.T@force,force,mx,gx,states


def parallel_energy(point,dp):
    ql,qr,*_=parallel_kinematics(point)
    energy=.5*P.mp*dp@dp+P.mp*P.gravity*point[1]
    for q,base in [(ql,A),(qr,B)]:
        dq=np.linalg.solve(jac(q),dp)
        energy+=kinetic(q,dq,payload=0.)+potential(q,payload=0.)
    return energy
