// Counts page opens and download-button clicks only. No cookies or persistent identifiers.
(()=>{
 'use strict';
 if(location.origin!=='https://alexisnoh37-cell.github.io'||!/^\/streambrief-releases\/(?:index\.html)?$/.test(location.pathname))return;
 if(navigator.doNotTrack==='1'||navigator.globalPrivacyControl===true)return;
 const endpoint='https://streambrief-relay.isn0522.workers.dev/site-events';
 function report(event){
  try{
   const bytes=new Uint8Array(32);crypto.getRandomValues(bytes);
   const batch=btoa(String.fromCharCode(...bytes)).replaceAll('+','-').replaceAll('/','_').replaceAll('=','');
   void fetch(endpoint,{method:'POST',headers:{'Content-Type':'text/plain;charset=UTF-8'},body:JSON.stringify({event,batch}),credentials:'omit',referrerPolicy:'no-referrer',redirect:'error',keepalive:true}).catch(()=>{});
  }catch{/* A blocked statistics request never prevents a download. */}
 }
 let counted=false;
 function visit(){if(counted||document.visibilityState!=='visible')return;counted=true;report('visit');}
 document.addEventListener('visibilitychange',visit);visit();
 for(const [id,event] of [['setup-download','setup'],['update-direct-download','update'],['update-download','update']]){
  document.getElementById(id)?.addEventListener('click',()=>report(event));
 }
})();
