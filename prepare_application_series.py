"""Portable QASM emitters for the ACTUAL E.ON and Airbus discrete steps.
No runtime SDK, hardware login or cloud submission. Logical circuits only.
"""
import hashlib,json,math,sys
from pathlib import Path
import numpy as np
import native_response as N
ROOT=Path(__file__).parent

def emit(folder,rows,metadata):
    out=ROOT/folder/'series_v6';out.mkdir(exist_ok=True)
    circuits=[]
    for name,n,ops,details in rows:
        text=N.qasm(n,ops);f=name+'.qasm';(out/f).write_text(text,newline='\n')
        circuits.append({'id':name,'file':f,'n_qubits':n,'sha256':hashlib.sha256(text.encode()).hexdigest(),**N.cost(ops),**details})
    manifest={'version':6,'status':'EMITTED_NOT_FLOWN','shots_per_circuit':8192,
              'total_shots_per_run':8192*len(rows),'circuits':circuits,
              'backend':None,'layout':None,'hardware_qualified':False,**metadata}
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2))
    return {'circuits':len(rows),'max_logical_cx':max(x['logical_cx_before_routing'] for x in circuits),
            'total_shots_per_run':manifest['total_shots_per_run']}

def eon_ops(F,geo,x,k,quench=True,coupling=True):
    on=F.active_mask(x);pairs=geo['pairs'];ops=N.prep([p for i,p in enumerate(pairs) if on[i]])
    if quench:ops += [('x',pairs[F.QUENCH_RUNG][0])]
    for _ in range(k):
        ops += [('rzz',a,b,-F.MU*F.DT*float(geo['w_pair'][i])) for i,(a,b) in enumerate(pairs) if on[i]]
        for i,(a,b) in enumerate(pairs):
            if on[i]:ops += [('rx',a,-2*F.DT),('rx',b,-2*F.DT)]
        if coupling:ops += [('rxx',p,q,2*F.DT*w/4) for p,q,w in geo['bonds'] if on[p//2] and on[q//2]]
    return N.expand(ops)

def eon():
    sys.path.insert(0,str(ROOT/'EON_SUBMISSION_PACKAGE'))
    import eon_nisq_field as F
    from eon_dynamics_crossing import CORE
    geo=F.geometry();rows=[]
    for arm,x in CORE.items():
        for k in range(9): rows.append((f'{arm}_k{k}',20,eon_ops(F,geo,x,k),{'arm':arm,'k':k,'control':False}))
    for mode in ['no_quench','no_coupling']:
        for k in range(9):
            rows.append((f'certified_{mode}_k{k}',20,eon_ops(F,geo,CORE['certified'],k,quench=mode!='no_quench',coupling=mode!='no_coupling'),
                         {'arm':'certified','k':k,'control':mode}))
    # Cross-check original independent matrix implementation on active subspaces.
    checks=[]
    for arm,x in CORE.items():
        on=F.active_mask(x);active=[q for i,p in enumerate(geo['pairs']) if on[i] for q in p]
        mapping={q:i for i,q in enumerate(active)};n=len(active)
        ops=eon_ops(F,geo,x,1)
        mapped=[]
        for o in ops:
            if o[0] in ['cx','rzz']:mapped.append((o[0],mapping[o[1]],mapping[o[2]],*o[3:]))
            else:mapped.append((o[0],mapping[o[1]],*o[2:]))
        got=N.run(n,mapped)
        pairs=[(mapping[a],mapping[b]) for i,(a,b) in enumerate(geo['pairs']) if on[i]]
        bonds=[(mapping[a],mapping[b],w) for a,b,w in geo['bonds'] if a in mapping and b in mapping]
        weights=[w for i,w in enumerate(geo['w_pair']) if on[i]]
        ref=F.prepare(n,pairs,[True]*len(pairs));ref=F.quench(ref,n,mapping[geo['pairs'][F.QUENCH_RUNG][0]])
        target=F.evolve_series(ref,n,pairs,bonds,weights,[True]*len(pairs),1)[-1]
        observed=[N.zz(got,a,b) for a,b in pairs]
        checks.append({'arm':arm,'active_qubits':n,'original_model_max_parity_error':float(np.max(abs(np.array(target)-observed)))})
    assert max(x['original_model_max_parity_error'] for x in checks)<1e-10
    result=emit('EON_SUBMISSION_PACKAGE',rows,{'target':'original ordered discrete step; no continuous-time exactness claim',
                'arms':list(CORE),'depths':list(range(9)),'model_parity_checks':checks,
                'readout':'pair parities on pairs 7,8,9 -> RMS leftover, then uniform temporal power'})
    return result

def airbus_ops(nr,mode,k,coupling=True):
    ops=[]
    for i in range(nr):
        s=.9*math.sin(2*math.pi*mode*i/nr)
        ops += [('ry',2*i,2*math.asin(math.sqrt((1-s)/2)))]
    for _ in range(k):
        ops += [('rzz',2*i,2*i+1,-N.KAPPA*.3) for i in range(nr)]
        ops += [('rx',q,-.6) for q in range(2*nr)]
        if coupling:
            for i in range(nr-1):ops += [('rxx',2*i+1,2*i+2,.3),('ryy',2*i+1,2*i+2,.3)]
    return N.expand(ops)

def airbus():
    rows=[]
    for mode in [1,2]:
        for coupled in [True,False]:
            for k in range(17):
                name=f'mode{mode}_'+('coupled' if coupled else 'decoupled')+f'_k{k}'
                rows.append((name,42,airbus_ops(21,mode,k,coupled),{'mode':mode,'k':k,'exchange':coupled}))
    return emit('airbus',rows,{'target':'original RX/ZZ/XX/YY ordered discrete step, phi=0',
                'depths':list(range(17)),'readout':'equal-time connected covariance, spatial Fourier X(q,k)',
                'scope':'uniform series fixes sampling; it does not establish a fluid-model bridge or classical hardness'})

if __name__=='__main__':
    result={'eon':eon(),'airbus':airbus()}
    (ROOT/'validation/application_emitters.json').write_text(json.dumps(result,indent=2))
    print(json.dumps(result,indent=2))
