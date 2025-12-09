import{n as s,k as i,r as m,j as e}from"./index.DmrHunjf.js";import{P as c,R as l}from"./RenderInPortalIfExists.D4_dxQEi.js";const p=""+new URL("../media/flake-0.DgWaVvm5.png",import.meta.url).href,d=""+new URL("../media/flake-1.B2r5AHMK.png",import.meta.url).href,f=""+new URL("../media/flake-2.BnWSExPC.png",import.meta.url).href,o=150,S=150,g=10,E=90,u=4e3,n=(t,a=0)=>Math.random()*(t-a)+a,w=()=>i(`from{transform:translateY(0)
      rotateX(`,n(360),`deg)
      rotateY(`,n(360),`deg)
      rotateZ(`,n(360),"deg);}to{transform:translateY(calc(100vh + ",o,`px))
      rotateX(0)
      rotateY(0)
      rotateZ(0);}`),x=s("img",{target:"es7rdur0"})(({theme:t})=>({position:"fixed",top:"-150px",marginLeft:`${-150/2}px`,zIndex:t.zIndices.balloons,left:`${n(E,g)}vw`,animationDelay:`${n(u)}ms`,height:`${o}px`,width:`${S}px`,pointerEvents:"none",animationDuration:"3000ms",animationName:w(),animationTimingFunction:"ease-in",animationDirection:"normal",animationIterationCount:1,opacity:1})),_=100,r=[p,d,f],I=r.length,M=({particleType:t})=>e(x,{src:r[t]}),h=function({scriptRunId:a}){return e(l,{children:e(c,{className:"stSnow","data-testid":"stSnow",scriptRunId:a,numParticleTypes:I,numParticles:_,ParticleComponent:M})})},P=m.memo(h);export{_ as NUM_FLAKES,P as default};
