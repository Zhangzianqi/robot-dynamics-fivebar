"""Course-model board-inclination / drawing-speed sweeps; not hardware data."""
from pathlib import Path
from dataclasses import replace
import json
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import robot_model as model
import make_figures as plot

ROOT=Path(__file__).resolve().parents[1]
N=401
original=model.P
mpl.rcParams.update({'font.family':'sans-serif','font.sans-serif':['Microsoft YaHei','DejaVu Sans'],
  'font.size':10,'legend.fontsize':9,'pdf.fonttype':42,'svg.fonttype':'none'})


def evaluate(duration,gravity,near=False):
    model.P=replace(original,duration=float(duration),gravity=float(gravity))
    t=np.linspace(0,duration,N)
    dynamic=[];static=[]
    for time in t:
        p,v,a=model.path(time,near_singular=near)
        dynamic.append(model.parallel_inverse(p,v,a)[0])
        static.append(model.parallel_inverse(p,np.zeros(2),np.zeros(2))[0])
    return np.max(np.abs(dynamic),axis=0),np.max(np.abs(static),axis=0)


def main():
    angle_records=[];time_records=[]
    try:
        for angle in [0,30,60,90]:
            peak,static=evaluate(4.,original.gravity*np.sin(np.radians(angle)))
            angle_records.append({'gamma_deg':angle,'in_plane_gravity_m_s2':float(original.gravity*np.sin(np.radians(angle))),
                'peak_left_Nm':float(peak[0]),'peak_right_Nm':float(peak[1]),'peak_both_Nm':float(peak.max()),
                'static_limit_both_Nm':float(static.max())})
        for duration in [2,4,8,16]:
            for near in [False,True]:
                peak,static=evaluate(duration,original.gravity,near)
                time_records.append({'duration_s':duration,'path':'near' if near else 'safe',
                  'peak_left_Nm':float(peak[0]),'peak_right_Nm':float(peak[1]),'peak_both_Nm':float(peak.max()),
                  'static_limit_both_Nm':float(static.max())})
    finally:
        model.P=original
    results={'interpretation':'Deterministic course-model simulation, not Quanser measurements or parameter reproduction.',
      'samples_per_trajectory':N,'nominal_parameters':original.__dict__,
      'inclination_assumption':'gamma=0 horizontal board; gamma=90 vertical board; in-plane gravity=9.81 sin(gamma); out-of-plane reactions and pen contact/friction not modeled.',
      'inclination':angle_records,'duration':time_records}
    (ROOT/'data'/'scenario_sweeps.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
    np.savetxt(ROOT/'data'/'scenario_inclination.csv',np.array([[r[k] for k in ['gamma_deg','in_plane_gravity_m_s2','peak_left_Nm','peak_right_Nm','peak_both_Nm','static_limit_both_Nm']] for r in angle_records]),
      delimiter=',',header='gamma_deg,in_plane_gravity_m_s2,peak_left_Nm,peak_right_Nm,peak_both_Nm,static_limit_both_Nm',comments='')
    with (ROOT/'data'/'scenario_duration.csv').open('w',encoding='utf-8') as f:
        f.write('duration_s,path,peak_left_Nm,peak_right_Nm,peak_both_Nm,static_limit_both_Nm\n')
        for r in time_records:
            f.write(','.join(str(r[k]) for k in ['duration_s','path','peak_left_Nm','peak_right_Nm','peak_both_Nm','static_limit_both_Nm'])+'\n')
    fig,axs=plot.grid(1,2,height=3.4)
    angles=[r['gamma_deg'] for r in angle_records]
    axs[0].plot(angles,[r['peak_both_Nm'] for r in angle_records],'-o',color=plot.NAVY,label='安全轨迹，T = 4 s',ms=4)
    axs[0].set(xlabel='板面倾角 γ / °',ylabel='峰值驱动扭矩 / (N·m)',xticks=angles)
    plot.legend(axs[0],1)
    for path,color,label in [('safe',plot.NAVY,'安全轨迹'),('near',plot.ORANGE,'近奇异对照')]:
        rows=[r for r in time_records if r['path']==path]
        assert all(r['peak_both_Nm']>0 and r['duration_s']>0 for r in rows)
        axs[1].plot([r['duration_s'] for r in rows],[r['peak_both_Nm'] for r in rows],'-o',color=color,label=label,ms=4)
        axs[1].axhline(rows[0]['static_limit_both_Nm'],color=color,ls='--',lw=1.)
    axs[1].set_xscale('log',base=2);axs[1].set_yscale('log')
    axs[1].set(xlabel='单圈执行时间 T / s',ylabel='峰值驱动扭矩 / (N·m)',xticks=[2,4,8,16],xticklabels=['2','4','8','16'])
    plot.legend(axs[1],1)
    name='fig11_installation_speed'
    fig.canvas.draw()
    plot.require_matplotlib_panel_alignment(fig,json_out=plot.QA/f'{name}.alignment.json',strict=True)
    fig.savefig(plot.OUT/f'{name}.pdf')
    fig.savefig(plot.OUT/f'{name}.svg')
    fig.savefig(plot.OUT/f'{name}.png',dpi=300)
    plt.close(fig)
    print(json.dumps(results,indent=2,ensure_ascii=False))


if __name__=='__main__': main()
