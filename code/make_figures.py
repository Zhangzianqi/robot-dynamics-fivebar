"""Publication-style figures from stored deterministic simulation arrays."""
from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.patheffects as pe
import numpy as np
from matplotlib.patches import Circle, Arc
from matplotlib.colors import LogNorm
from robot_model import *
from audit_panel_alignment import require_matplotlib_panel_alignment

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'figures'/'generated'; OUT.mkdir(parents=True,exist_ok=True)
QA=ROOT/'outputs'/'validation'; QA.mkdir(parents=True,exist_ok=True)
D=np.load(ROOT/'data'/'simulation_arrays.npz')
R=json.loads((ROOT/'data'/'results.json').read_text(encoding='utf-8'))
NAVY='#203A5F'; TEAL='#168C8C'; ORANGE='#D9863A'; GRAY='#8895A5'; LIGHT='#D9E4ED'; RED='#B5525D'
mpl.rcParams.update({'font.family':'sans-serif','font.sans-serif':['Microsoft YaHei','DejaVu Sans'],
 'axes.unicode_minus':False,'font.size':10,'axes.labelsize':10,'xtick.labelsize':9,'ytick.labelsize':9,
 'legend.fontsize':9,'axes.spines.top':False,'axes.spines.right':False,'axes.linewidth':.8,
 'lines.linewidth':1.7,'pdf.fonttype':42,'svg.fonttype':'none','savefig.facecolor':'white',
 'mathtext.fontset':'dejavusans','legend.frameon':False})


def grid(rows=1,cols=1,height=None):
    fig,ax=plt.subplots(rows,cols,figsize=(7.1,height or (2.8*rows+.25)),squeeze=False)
    fig.subplots_adjust(left=.12,right=.965,bottom=.18 if rows==1 else .10,top=.82 if rows==1 else .94,
                        wspace=.35,hspace=.60)
    axes=ax.ravel()
    for i,a in enumerate(axes):
        a.grid(alpha=.20,lw=.6); a.set_axisbelow(True)
        if len(axes)>1:
            a.annotate(chr(97+i),xy=(0,1),xycoords='axes fraction',xytext=(-16,10),textcoords='offset points',
                       weight='bold',fontsize=11,annotation_clip=False)
    return fig,axes


def legend(a,ncol=2):
    a.legend(loc='lower center',bbox_to_anchor=(.5,1.015),ncol=ncol,columnspacing=1.,handlelength=2.)


def save(fig,name,exclude=None,exemptions=()):
    fig.canvas.draw()
    report=require_matplotlib_panel_alignment(fig,json_out=QA/f'{name}.alignment.json',
       exclude_axes=exclude or [],exemptions=exemptions,tolerance_pt=1.5,strict=True)
    fig.savefig(OUT/f'{name}.pdf')
    fig.savefig(OUT/f'{name}.png',dpi=300)
    fig.savefig(OUT/f'{name}.svg')
    plt.close(fig)


def linkage(a,point,alpha=1.,color_left=NAVY,color_right=TEAL,labels=True):
    ql,qr,*_=parallel_kinematics(point)
    cl=A+P.l1*unit(ql[0]); cr=B+P.l1*unit(qr[0])
    a.plot([A[0],B[0]],[0,0],color=GRAY,lw=5,alpha=.6*alpha)
    for base,elbow,color in [(A,cl,color_left),(B,cr,color_right)]:
        a.plot([base[0],elbow[0],point[0]],[base[1],elbow[1],point[1]],'-o',color=color,lw=3,
               ms=6,mfc='white',mew=1.5,alpha=alpha)
    a.scatter(*point,s=75,c=ORANGE,zorder=5,alpha=alpha,edgecolors='white',linewidths=1.)
    if labels:
        for x,y,txt,dx,dy in [(*A,'A',-.025,-.035),(*B,'B',.015,-.035),
                               (*cl,'C',-.035,.015),(*cr,'D',.015,.015),(*point,'P',.013,.020)]:
            a.text(x+dx,y+dy,txt,color=NAVY,weight='bold')
    return cl,cr


def fig01():
    fig,axs=grid(height=4.5); a=axs[0]
    pt=np.array([0.,.38]);cl,cr=linkage(a,pt)
    a.text(-.38,.24,'左 2R 支链',color=NAVY,ha='center')
    a.text(.38,.24,'右 2R 支链',color=TEAL,ha='center')
    for base,elbow,color,sign in [(A,cl,NAVY,-1),(B,cr,TEAL,1)]:
        m=(base+elbow)/2
        a.text(m[0]+sign*.045,m[1],'l1',color=color,ha='center')
        m=(elbow+pt)/2
        a.text(m[0],m[1]+.030,'l2',color=color,ha='center')
    ql,qr,*_=parallel_kinematics(pt)
    for base,theta,label,color in [(A,ql[0],r'$\theta_L$',NAVY),(B,qr[0],r'$\theta_R$',TEAL)]:
        a.plot([base[0],base[0]+.085],[0,0],color=GRAY,lw=.7)
        a.add_patch(Arc(base,.095,.095,theta1=0,theta2=np.degrees(theta),color=color,lw=1.))
        pos=base+.115*unit(theta/2)
        a.text(*pos,label,color=color,ha='center',va='center',fontsize=13)
    ext=cl+.075*unit(ql[0])
    a.plot([cl[0],ext[0]],[cl[1],ext[1]],':',color=NAVY,lw=.8)
    a.add_patch(Arc(cl,.085,.085,theta1=np.degrees(ql.sum()),theta2=np.degrees(ql[0]),color=ORANGE,lw=1.))
    a.text(cl[0]+.065,cl[1]+.052,r'$q_{2L}$',color=ORANGE,fontsize=13,ha='center')
    a.text(0,-.075,'固定基座 AB = 0.36 m',ha='center',color=GRAY)
    a.text(0,.465,'竖直平面五杆并联机器人',ha='center',color=NAVY,weight='bold',fontsize=12)
    a.annotate('',xy=(.45,.08),xytext=(.45,.20),arrowprops={'arrowstyle':'->','color':ORANGE,'lw':1.6})
    a.text(.46,.145,'g',color=ORANGE,va='center')
    a.text(-.43,.15,'y',color=GRAY);a.annotate('',xy=(-.44,.145),xytext=(-.44,.05),arrowprops={'arrowstyle':'->','color':GRAY})
    a.text(-.335,.057,'x',color=GRAY);a.annotate('',xy=(-.34,.05),xytext=(-.44,.05),arrowprops={'arrowstyle':'->','color':GRAY})
    a.set(xlim=(-.48,.53),ylim=(-.10,.50),aspect='equal');a.axis('off')
    save(fig,'fig01_mechanism')


def fig02():
    fig,axs=grid(1,2,height=3.3);a,b=axs
    # A dedicated geometric view has equal metric aspect, explicitly exempt from shared box height.
    for fraction in [0,.25,.5,.75]:
        pt=path(P.duration*fraction)[0]
        linkage(a,pt,alpha=.27,labels=False)
    a.plot(D['points'][:,0],D['points'][:,1],color=ORANGE,lw=2.5,label='安全椭圆轨迹')
    a.scatter(*D['points'][0],color=ORANGE,s=25)
    a.set(xlabel='x / m',ylabel='y / m',xlim=(-.34,.34),ylim=(-.02,.46))
    a.set_aspect('equal',adjustable='datalim')
    legend(a,1)
    t=D['t']; s=t/P.duration; h=10*s**3-15*s**4+6*s**5
    b.plot(t,h,color=NAVY,label='归一化相位 h')
    b.plot(t,(30*s*s-60*s**3+30*s**4)/P.duration,color=TEAL,label='相位速率 dh/dt')
    b.set(xlabel='时间 / s',ylabel='相位与速率');legend(b,1)
    save(fig,'fig02_path_timing')


def fig03():
    fig,axs=grid(2,2,height=5.6);t=D['t']
    for a,key,ylabel in zip(axs[:3],['q','dq','ddq'],['关节角 / rad','角速度 / (rad/s)','角加速度 / (rad/s²)']):
        a.plot(t,D[key][:,0],color=NAVY,label='关节 1');a.plot(t,D[key][:,1],color=TEAL,label='关节 2')
        a.set(xlabel='时间 / s',ylabel=ylabel);legend(a)
    cond=np.array([np.linalg.cond(jac(q)) for q in D['q']]); det=np.array([abs(np.linalg.det(jac(q))) for q in D['q']])
    axs[3].plot(t,cond,color=ORANGE,label='串联 Jacobian 条件数')
    axs[3].set(xlabel='时间 / s',ylabel='条件数 κ(Js)');legend(axs[3],1)
    save(fig,'fig03_serial_kinematics')


def fig04():
    fig,axs=grid(1,2,height=3.0);angles=np.linspace(-np.pi+.002,-.002,600)
    det=np.abs(P.l1*P.l2*np.sin(angles));condition=np.array([np.linalg.cond(jac(np.array([1.,q2]))) for q2 in angles])
    axs[0].plot(np.degrees(angles),det,color=NAVY)
    axs[0].set(xlabel='相对肘角 q2 / °',ylabel='|det Js| / m²')
    axs[1].semilogy(np.degrees(angles),condition,color=TEAL)
    axs[1].set(xlabel='相对肘角 q2 / °',ylabel='条件数 κ(Js)')
    save(fig,'fig04_serial_singularity')


def fig05():
    fig,axs=grid(2,1,height=5.4);t=D['t']
    for i,a in enumerate(axs):
        a.plot(t,D['tau'][:,i],color=NAVY,lw=2.2,label='总驱动扭矩')
        a.plot(t,D['gravity'][:,i],color=GRAY,ls='--',label='重力项')
        a.plot(t,D['inertial'][:,i],color=TEAL,label='惯性项')
        a.plot(t,D['velocity'][:,i],color=ORANGE,ls=':',label='速度耦合项')
        a.set(xlabel='时间 / s',ylabel=f'关节 {i+1} 扭矩 / (N·m)');legend(a,4)
    save(fig,'fig05_serial_torques')


def fig06():
    fig,axs=grid(2,2,height=5.8);t=D['t']
    axs[0].plot(t,1e6*D['forward_error'],color=NAVY)
    axs[0].set(xlabel='时间 / s',ylabel='正动力学回放位置误差 / μm')
    residual=np.max(np.abs(D['tau']-D['ne']),axis=1)
    axs[1].plot(t,1e15*residual,color=TEAL,lw=.8)
    axs[1].set(xlabel='时间 / s',ylabel='两种动力学扭矩差 / (fN·m)')
    axs[2].plot(t,D['energy']-D['energy'][0],color=NAVY,label='机械能变化 ΔE')
    axs[2].plot(t,D['work'],color=ORANGE,ls='--',label='累积驱动功 W')
    axs[2].set(xlabel='时间 / s',ylabel='能量 / J');legend(axs[2])
    axs[3].plot(t,1e6*(D['energy']-D['energy'][0]-D['work']),color=TEAL,label='串联')
    axs[3].plot(t,1e6*(D['penergy']-D['penergy'][0]-D['pwork']),color=ORANGE,label='并联')
    axs[3].set(xlabel='时间 / s',ylabel='功-能残差 / μJ');legend(axs[3])
    save(fig,'fig06_validation')


def fig07():
    fig,axs=grid(height=4.5);a=axs[0]
    z=D['workspace_condition'];cmap=mpl.colormaps['viridis'].copy();cmap.set_bad('#F2F4F6')
    im=a.pcolormesh(D['xs'],D['ys'],z,cmap=cmap,norm=LogNorm(vmin=1,vmax=300),shading='auto',rasterized=True)
    a.plot(D['points'][:,0],D['points'][:,1],color='white',lw=2.4,label='安全轨迹',
       path_effects=[pe.withStroke(linewidth=3.4,foreground=NAVY)])
    a.plot(D['nearpoints'][:,0],D['nearpoints'][:,1],color=ORANGE,lw=1.6,label='近奇异对照')
    a.scatter([A[0],B[0]],[0,0],s=24,marker='s',c=NAVY,clip_on=False)
    a.set(xlabel='x / m',ylabel='y / m',xlim=(-.55,.55),ylim=(0,.60));legend(a)
    # Place colorbar outside the inference axes, exclude it from the panel comparability gate.
    cax=fig.add_axes([.89,.13,.025,.75]);a.set_position([.12,.13,.72,.75])
    cb=fig.colorbar(im,cax=cax,extend='max');cb.set_label('并联 Jacobian 条件数 κ(Jp)')
    save(fig,'fig07_parallel_workspace',exclude=[cax])


def fig08():
    fig,axs=grid(2,2,height=5.6);t=D['t']
    axs[0].plot(t,np.degrees(D['theta'][:,0]),color=NAVY,label='左主动关节')
    axs[0].plot(t,np.degrees(D['theta'][:,1]),color=TEAL,label='右主动关节')
    axs[0].set(xlabel='时间 / s',ylabel='主动关节角 / °');legend(axs[0])
    axs[1].plot(t,np.abs(D['det_a']),color=ORANGE)
    axs[1].set(xlabel='时间 / s',ylabel='|det A|')
    axs[2].plot(t,np.abs(D['bdiag'][:,0]),color=NAVY,label='|bL|')
    axs[2].plot(t,np.abs(D['bdiag'][:,1]),color=TEAL,label='|bR|')
    axs[2].set(xlabel='时间 / s',ylabel='驱动传递系数 / m');legend(axs[2])
    axs[3].plot(t,D['condition'],color=ORANGE)
    axs[3].set(xlabel='时间 / s',ylabel='条件数 κ(Jp)')
    save(fig,'fig08_parallel_kinematics')


def fig09():
    fig,axs=grid(2,1,height=5.3);t=D['t']
    static=np.array([parallel_kinematics(p)[-1].T@g for p,g in zip(D['points'],D['gx'])])
    for i,a in enumerate(axs):
        a.plot(t,D['ptau'][:,i],color=NAVY if i==0 else TEAL,label='整机动力学扭矩')
        a.plot(t,static[:,i],color=GRAY,ls='--',label='静态重力扭矩')
        a.plot(t,D['ptau'][:,i]-static[:,i],color=ORANGE,label='惯性与速度项')
        a.set(xlabel='时间 / s',ylabel=f'{"左" if i==0 else "右"}电机扭矩 / (N·m)');legend(a,3)
    save(fig,'fig09_parallel_dynamics')


def fig10():
    fig,axs=grid(3,1,height=7.5);t=D['t']
    axs[0].semilogy(t,D['condition'],color=NAVY,label='安全轨迹')
    axs[0].semilogy(t,D['nearcondition'],color=ORANGE,label='近奇异对照')
    axs[0].set(xlabel='时间 / s',ylabel='条件数 κ(Jp)');legend(axs[0])
    axs[1].semilogy(t,np.max(np.abs(D['ptau']),axis=1),color=NAVY,label='安全轨迹')
    axs[1].semilogy(t,np.max(np.abs(D['neartau']),axis=1),color=ORANGE,label='近奇异对照')
    axs[1].set(xlabel='时间 / s',ylabel='最大驱动扭矩 / (N·m)');legend(axs[1])
    axs[2].semilogy(t,D['safe_unit_gain'],color=NAVY,label='安全轨迹')
    axs[2].semilogy(t,D['near_unit_gain'],color=ORANGE,label='近奇异对照')
    axs[2].set(xlabel='时间 / s',ylabel='竖直传力增益 / m');legend(axs[2])
    save(fig,'fig10_singularity_comparison')


if __name__=='__main__':
    for f in [fig01,fig02,fig03,fig04,fig05,fig06,fig07,fig08,fig09,fig10]:
        f();print(f.__name__,'exported')
