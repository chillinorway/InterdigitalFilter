import math

MM_PER_IN = 25.4

def _lagrange_zero(points):
    (e1,y1),(e2,y2),(e3,y3) = points
    return y3*y2*e1/((y1-y2)*(y1-y3)) + y1*y3*e2/((y2-y1)*(y2-y3)) + y1*y2*e3/((y3-y1)*(y3-y2))

def _fnrj(ta,b,c,d):
    return (b*c-ta*d)/(c*c+d*d)

def prototype_g(n, ripple_db):
    g=[0.0]*(n+2)
    if ripple_db <= 0:
        for k in range(1,n+1):
            g[k]=2.0*math.sin((2*k-1)*math.pi/(2*n))
        g[n+1]=1.0
        return g,1.0
    c=2*ripple_db/17.37
    beta=math.log((math.exp(c)+1)/(math.exp(c)-1))
    gamma=.5*(math.exp(beta/(2*n))-math.exp(-beta/(2*n)))
    a=[0.0]*(n+1); b=[0.0]*(n+1)
    for k in range(1,n+1):
        a[k]=math.sin(.5*(2*k-1)*math.pi/n)
        b[k]=gamma*gamma+math.sin(k*math.pi/n)**2
    g[1]=2*a[1]/gamma
    for k in range(2,n+1):
        g[k]=4*a[k-1]*a[k]/(b[k-1]*g[k-1])
    g[n+1]=((math.exp(beta/2)+1)/(math.exp(beta/2)-1))**2 if n%2==0 else 1.0
    b0=math.sqrt(10**(.1*ripple_db)-1)
    ca=math.log(b0+math.sqrt(b0*b0+1))/n
    bw3=.5*(math.exp(ca)+math.exp(-ca))
    return g,bw3

def calculate(fc_mhz,bw_mhz,n,ripple_db,z0,ground_mm,rod_dia_mm,end_clear_mm):
    if n<2: raise ValueError("Number of resonators must be at least 2.")
    if fc_mhz<=0 or bw_mhz<=0 or bw_mhz>=2*fc_mhz: raise ValueError("Invalid frequency/bandwidth.")
    if ground_mm<=rod_dia_mm: raise ValueError("Cavity depth must exceed rod diameter.")
    f0=fc_mhz/1000.0
    f1=(fc_mhz-bw_mhz/2)/1000.0
    f2=(fc_mhz+bw_mhz/2)/1000.0
    h=ground_mm/MM_PER_IN
    d=rod_dia_mm/MM_PER_IN
    e=end_clear_mm/MM_PER_IN
    g,bw3=prototype_g(n,ripple_db)
    rbw=f2-f1
    bw3ghz=rbw if ripple_db<=0 else rbw*bw3
    qf=f0/bw3ghz
    qwvl=11.8028/(4*f0)
    ak=[0]*(n+2); rk=[0]*(n+2)
    for k in range(1,n):
        ak[k]=1/(bw3*math.sqrt(g[k]*g[k+1]))
        rk[k]=ak[k]/qf
    ak[n]=g[1]*bw3
    qs=g[1]*bw3*qf
    canh=(math.exp(2*math.pi*e/h)-1)/(math.exp(2*math.pi*e/h)+1)
    zm=59.9585*math.log(4*h/(math.pi*d))
    ze=59.9585*math.log(canh*h*4/(math.pi*d))
    z=math.pi*d/(2*h)
    coth=(math.exp(z)+1)/(math.exp(z)-1)
    sp=[0.0]*n
    rkh=rk[1]*math.sqrt(zm/ze)
    y=math.pi*rkh/4
    t=coth**y
    sp[1]=(h/math.pi)*math.log((t+1)/(t-1))
    for k in range(2,n-1):
        y=math.pi*rk[k]/4
        t=coth**y
        sp[k]=(h/math.pi)*math.log((t+1)/(t-1))
    if n>2: sp[n-1]=sp[1]
    x=math.sqrt(math.pi*z0/(4*ze*qs))
    if not 0<x<1: raise ValueError("Calculated tap position is outside the valid range.")
    aq=2*qwvl*math.atan(x/math.sqrt(1-x*x))/math.pi
    w0=2*math.pi*f0*1e9
    ratio=d/h
    cf=(-.0000422+.0857397*ratio+.0067853*ratio**2-.09092165*ratio**3+.169088*ratio**4)*math.pi*h*2.54
    ww=w0*1e-12
    b2=math.pi*aq/(2*qwvl)
    gg=1/z0
    bb=-math.cos(b2)/(ze*math.sin(b2))
    inner=[]; end=[]
    for frac in (.80,.87,.95):
        el=frac*qwvl
        ang=el*math.pi/(2*qwvl)
        beta=ang-b2
        cp=ww*(cf+.17655*d*d/(qwvl-el))
        inner.append((el,cp-math.cos(ang)/(zm*math.sin(ang))))
        tann=math.tan(beta)
        end.append((el,cp+_fnrj(gg,bb+tann/ze,1-ze*bb*tann,ze*gg*tann)))
    elem=_lagrange_zero(inner)
    eleq=_lagrange_zero(end)
    spac=[sp[k]*MM_PER_IN for k in range(1,n)]
    xpos=[end_clear_mm]
    for s in spac: xpos.append(xpos[-1]+s)
    return dict(fc_mhz=fc_mhz,bw_mhz=bw_mhz,n=n,ripple_db=ripple_db,z0=z0,
                quarter_wave_mm=qwvl*MM_PER_IN,inner_rod_length_mm=elem*MM_PER_IN,
                end_rod_length_mm=eleq*MM_PER_IN,ground_mm=ground_mm,rod_dia_mm=rod_dia_mm,
                end_clear_mm=end_clear_mm,tap_mm=aq*MM_PER_IN,ze_ohm=ze,zm_ohm=zm,
                filter_q=qf,g=g[1:n+2],coupling=ak[1:n+1],spacings_mm=spac,
                x_positions_mm=xpos,box_height_mm=qwvl*MM_PER_IN,
                box_length_mm=xpos[-1]+end_clear_mm,box_depth_mm=ground_mm)
