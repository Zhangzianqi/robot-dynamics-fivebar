"""Generate all deterministic simulation arrays and validation metrics."""
from pathlib import Path
from dataclasses import asdict
import json
import numpy as np
from scipy.integrate import solve_ivp, cumulative_trapezoid
from robot_model import *

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data'; QA=ROOT/'outputs'/'validation'
DATA.mkdir(exist_ok=True); QA.mkdir(parents=True,exist_ok=True)


def main():
    t=np.linspace(0,P.duration,1601)
    points=np.array([path(x)[0] for x in t]); dp=np.array([path(x)[1] for x in t]); ddp=np.array([path(x)[2] for x in t])
    states=[serial_state(x) for x in t]
    q=np.array([s[0] for s in states]); dq=np.array([s[1] for s in states]); ddq=np.array([s[2] for s in states])
    tau=np.array([inverse_lagrange(*s) for s in states]); ne=np.array([inverse_newton_euler(*s) for s in states])
    gravity=np.array([grav(x) for x in q]); inertial=np.array([mass(s[0])@s[2] for s in states]); velocity=np.array([coriolis(s[0],s[1])@s[1] for s in states])
    energy=np.array([kinetic(x,v)+potential(x) for x,v in zip(q,dq)])
    power=np.einsum('ij,ij->i',tau,dq); work=cumulative_trapezoid(power,t,initial=0.)

    def ode(time,y):
        ref=serial_state(time)
        control=inverse_lagrange(*ref)
        return np.r_[y[2:],np.linalg.solve(mass(y[:2]),control-coriolis(y[:2],y[2:])@y[2:]-grav(y[:2]))]
    initial=np.r_[q[0],dq[0]]
    sol=solve_ivp(ode,(0,P.duration),initial,t_eval=t,method='DOP853',rtol=1e-10,atol=1e-12,max_step=.01)
    if not sol.success: raise RuntimeError(sol.message)
    pforward=np.array([fk(x) for x in sol.y[:2].T]); error=np.linalg.norm(pforward-points,axis=1)
    convergence=[]
    for step in [.04,.02,.01,.005,.0025]:
        low=solve_ivp(ode,(0,P.duration),initial,t_eval=t,method='RK45',rtol=1e-6,atol=1e-9,max_step=step)
        convergence.append({'max_step_s':step,'max_joint_error_rad':float(np.max(np.abs(low.y[:2].T-q))),
                            'max_cartesian_error_m':float(np.max(np.linalg.norm(np.array([fk(x) for x in low.y[:2].T])-points,axis=1)))})

    random=np.random.default_rng(20261025)
    jerrors=[]; nerrors=[]; mineigen=1e9; skewerror=[]
    for _ in range(500):
        qi=np.array([random.uniform(-np.pi,np.pi),random.uniform(-2.8,-.2)])
        vi=random.uniform(-2,2,2); ai=random.uniform(-5,5,2); eps=1e-6
        jnum=np.column_stack([(fk(qi+np.eye(2)[i]*eps)-fk(qi-np.eye(2)[i]*eps))/(2*eps) for i in range(2)])
        jerrors.append(np.max(np.abs(jnum-jac(qi))))
        nerrors.append(np.max(np.abs(inverse_lagrange(qi,vi,ai)-inverse_newton_euler(qi,vi,ai))))
        mineigen=min(mineigen,np.linalg.eigvalsh(mass(qi)).min())
        mdot=(mass(qi+eps*vi)-mass(qi-eps*vi))/(2*eps)
        s=mdot-2*coriolis(qi,vi)
        skewerror.append(np.max(np.abs(s+s.T)))

    parallel=[parallel_inverse(x,v,a) for x,v,a in zip(points,dp,ddp)]
    ptau=np.array([s[0] for s in parallel]); pforce=np.array([s[1] for s in parallel])
    mx=np.array([s[2] for s in parallel]); gx=np.array([s[3] for s in parallel])
    pl=np.array([s[4][0][0] for s in parallel]); pr=np.array([s[4][1][0] for s in parallel])
    pdql=np.array([s[4][0][1] for s in parallel]); pdqr=np.array([s[4][1][1] for s in parallel])
    theta=np.column_stack((pl[:,0],pr[:,0])); dtheta=np.column_stack((pdql[:,0],pdqr[:,0]))
    mats=[parallel_kinematics(x) for x in points]
    jp=np.array([s[4] for s in mats]); det_a=np.array([np.linalg.det(s[2]) for s in mats]); bdiag=np.array([s[3].diagonal() for s in mats])
    condition=np.array([np.linalg.cond(x) for x in jp])
    nearpoints=np.array([path(x,True)[0] for x in t])
    nearkin=[parallel_kinematics(x) for x in nearpoints]
    nearcondition=np.array([np.linalg.cond(s[4]) for s in nearkin])
    neardeta=np.array([np.linalg.det(s[2]) for s in nearkin])
    neartau=np.array([parallel_inverse(*path(x,True))[0] for x in t])
    safe_unit_gain=np.array([np.max(np.abs(s[4].T@np.array([0.,1.]))) for s in mats])
    near_unit_gain=np.array([np.max(np.abs(s[4].T@np.array([0.,1.]))) for s in nearkin])
    pfk=np.array([parallel_fk(x) for x in theta]); perr=np.linalg.norm(pfk-points,axis=1)
    penergy=np.array([parallel_energy(x,v) for x,v in zip(points,dp)])
    ppower=np.einsum('ij,ij->i',ptau,dtheta); pwork=cumulative_trapezoid(ppower,t,initial=0.)
    virtual_error=np.max(np.abs(ppower-np.einsum('ij,ij->i',pforce,dp)))
    closure_error=np.max([np.linalg.norm(fk(l,A)-fk(r,B)) for l,r in zip(pl,pr)])
    parallel_jac_error=[]
    for i in np.linspace(0,len(t)-1,41,dtype=int):
        eps=1e-6
        jnum=np.column_stack([(parallel_fk(theta[i]+np.eye(2)[j]*eps)-parallel_fk(theta[i]-np.eye(2)[j]*eps))/(2*eps) for j in range(2)])
        parallel_jac_error.append(np.max(np.abs(jnum-jp[i])))

    xs=np.linspace(-.55,.55,251); ys=np.linspace(.01,.60,161)
    grid=np.full((len(ys),len(xs)),np.nan); reachable=np.zeros_like(grid,dtype=bool)
    # Only the elbow-outward IK branches and the upper circle-intersection assembly are retained.
    for iy,y in enumerate(ys):
        for ix,x in enumerate(xs):
            point=np.array([x,y])
            if not all(abs(P.l1-P.l2)<np.linalg.norm(point-o)<P.l1+P.l2 for o in (A,B)): continue
            try:
                ql,qr,aa,bb,j=parallel_kinematics(point)
                if abs(np.linalg.det(aa))<1e-10 or np.min(np.abs(bb.diagonal()))<1e-10: continue
                if np.linalg.norm(parallel_fk([ql[0],qr[0]])-point)>1e-8: continue
                reachable[iy,ix]=True; grid[iy,ix]=np.linalg.cond(j)
            except (ValueError,np.linalg.LinAlgError): pass

    samples={}
    for time in [0.,1.,2.,3.,4.]:
        pt,vel,acc=path(time); qs,vs,acs=serial_state(time)
        torque,force,mm,gg,ss=parallel_inverse(pt,vel,acc)
        samples[str(time)]={'point_m':pt.tolist(),'q_rad':qs.tolist(),'dq_rad_s':vs.tolist(),'ddq_rad_s2':acs.tolist(),
        'M_kg_m2':mass(qs).tolist(),'C_dq_Nm':(coriolis(qs,vs)@vs).tolist(),'g_Nm':grav(qs).tolist(),
        'tau_serial_Nm':inverse_lagrange(qs,vs,acs).tolist(),'tau_parallel_Nm':torque.tolist(),
        'parallel_F_N':force.tolist(),'Mx_kg':mm.tolist(),'Gx_N':gg.tolist()}
    static_samples={}
    for height in [.38,.355,.34,.305]:
        point=np.array([0.,height]);ql,qr,aa,bb,j=parallel_kinematics(point)
        torque,force,mm,gg,ss=parallel_inverse(point,np.zeros(2),np.zeros(2))
        static_samples[str(height)]={'point_m':point.tolist(),'qL_rad':ql.tolist(),'qR_rad':qr.tolist(),
          'Jp_m_per_rad':j.tolist(),'condition_Jp':float(np.linalg.cond(j)), 'det_A':float(np.linalg.det(aa)),
          'unit_vertical_force_tau_Nm':(j.T@np.array([0.,1.])).tolist(),
          'whole_robot_gravity_tau_Nm':torque.tolist(),'Gx_N':gg.tolist()}
    results={'parameters':asdict(P),'samples':samples,'static_samples':static_samples,'validation':{
      'trajectory_samples':len(t),'dt_s':float(t[1]-t[0]),'random_seed':20261025,'random_samples':500,
      'random_ne_lagrange_max_abs_Nm':max(nerrors),'path_ne_lagrange_max_abs_Nm':float(np.max(np.abs(tau-ne))),
      'jacobian_finite_difference_max_abs_m_per_rad':max(jerrors),'mass_min_eigenvalue_random_kg_m2':float(mineigen),
      'skew_symmetry_max_abs':max(skewerror),'serial_inverse_kinematic_max_m':float(np.max([np.linalg.norm(fk(x)-p) for x,p in zip(q,points)])),
      'forward_max_joint_error_rad':float(np.max(np.abs(sol.y[:2].T-q))),'forward_max_position_error_m':float(error.max()),
      'serial_work_energy_max_abs_J':float(np.max(np.abs(energy-energy[0]-work))),
      'parallel_closure_max_m':float(closure_error),'parallel_forward_inverse_max_m':float(perr.max()),
      'parallel_jacobian_finite_difference_max_abs_m_per_rad':float(max(parallel_jac_error)),
      'parallel_virtual_power_max_W':float(virtual_error),'parallel_work_energy_max_abs_J':float(np.max(np.abs(penergy-penergy[0]-pwork))),
      'parallel_min_abs_det_A':float(np.min(np.abs(det_a))),'parallel_min_abs_Bdiag_m':float(np.min(np.abs(bdiag))),
      'parallel_max_condition_J':float(condition.max()),'parallel_min_mass_eigenvalue_kg':float(np.linalg.eigvalsh(mx).min()),
      'serial_peak_abs_tau_Nm':np.max(np.abs(tau),axis=0).tolist(),'parallel_peak_abs_tau_Nm':np.max(np.abs(ptau),axis=0).tolist(),
      'serial_peak_abs_velocity_rad_s':np.max(np.abs(dq),axis=0).tolist(),'serial_peak_abs_acceleration_rad_s2':np.max(np.abs(ddq),axis=0).tolist(),
      'parallel_theta_range_rad':np.column_stack((theta.min(axis=0),theta.max(axis=0))).tolist(),
      'workspace_grid_shape':list(grid.shape),'workspace_reachable_count':int(reachable.sum()),
      'near_singular_max_condition_J':float(nearcondition.max()),
      'near_singular_min_abs_det_A':float(np.min(np.abs(neardeta))),
      'near_singular_peak_abs_tau_Nm':np.max(np.abs(neartau),axis=0).tolist(),
      'safe_max_unit_vertical_force_torque_m':float(safe_unit_gain.max()),
      'near_max_unit_vertical_force_torque_m':float(near_unit_gain.max()),
      'convergence':convergence}}
    (DATA/'results.json').write_text(json.dumps(results,indent=2,ensure_ascii=False),encoding='utf-8')
    np.savez_compressed(DATA/'simulation_arrays.npz',t=t,points=points,dp=dp,ddp=ddp,q=q,dq=dq,ddq=ddq,tau=tau,ne=ne,
      gravity=gravity,inertial=inertial,velocity=velocity,energy=energy,power=power,work=work,
      qforward=sol.y[:2].T,pforward=pforward,forward_error=error,ptau=ptau,pforce=pforce,mx=mx,gx=gx,theta=theta,dtheta=dtheta,
      pl=pl,pr=pr,jp=jp,det_a=det_a,bdiag=bdiag,condition=condition,penergy=penergy,ppower=ppower,pwork=pwork,
      xs=xs,ys=ys,workspace_condition=grid,workspace_reachable=reachable,
      nearpoints=nearpoints,nearcondition=nearcondition,neardeta=neardeta,neartau=neartau,
      safe_unit_gain=safe_unit_gain,near_unit_gain=near_unit_gain)
    np.savetxt(DATA/'serial_trajectory.csv',np.column_stack((t,points,q,dq,ddq,tau,ne,energy,power,work,error)),delimiter=',',
      header='t_s,px_m,py_m,q1_rad,q2_rad,dq1_rad_s,dq2_rad_s,ddq1_rad_s2,ddq2_rad_s2,tau1_Nm,tau2_Nm,ne1_Nm,ne2_Nm,energy_J,power_W,work_J,forward_error_m',comments='')
    np.savetxt(DATA/'parallel_trajectory.csv',np.column_stack((t,points,theta,dtheta,ptau,pforce,det_a,bdiag,condition,penergy,ppower,pwork)),delimiter=',',
      header='t_s,px_m,py_m,thetaL_rad,thetaR_rad,dthetaL_rad_s,dthetaR_rad_s,tauL_Nm,tauR_Nm,Fx_N,Fy_N,detA,bL_m,bR_m,condJ,energy_J,power_W,work_J',comments='')
    np.savetxt(DATA/'workspace_condition.csv',grid,delimiter=',')
    np.savetxt(DATA/'workspace_x_m.csv',xs,delimiter=',')
    np.savetxt(DATA/'workspace_y_m.csv',ys,delimiter=',')
    np.savetxt(DATA/'near_singular_comparison.csv',np.column_stack((t,nearpoints,nearcondition,neardeta,neartau,safe_unit_gain,near_unit_gain)),delimiter=',',
      header='t_s,px_m,py_m,near_condJ,near_detA,near_tauL_Nm,near_tauR_Nm,safe_unit_vertical_force_gain_m,near_unit_vertical_force_gain_m',comments='')
    (QA/'numerical_checks.json').write_text(json.dumps(results['validation'],indent=2),encoding='utf-8')
    print(json.dumps(results['validation'],indent=2))
    # Scientific regression guards: independent identities, rather than a code mirror.
    assert max(nerrors)<1e-10, 'Newton-Euler / Lagrange disagreement'
    assert max(jerrors)<1e-7 and max(parallel_jac_error)<1e-6, 'Analytic / numerical Jacobian disagreement'
    assert closure_error<1e-10 and perr.max()<1e-10, 'Parallel loop closure / assembly disagreement'
    assert virtual_error<1e-10, 'Virtual work mapping violated'
    assert np.max(np.abs(energy-energy[0]-work))<1e-4, 'Serial power-energy inconsistency'
    assert np.max(np.abs(penergy-penergy[0]-pwork))<1e-4, 'Parallel power-energy inconsistency'


if __name__=='__main__': main()
