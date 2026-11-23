const test=require('node:test'),assert=require('node:assert/strict'),vm=require('node:vm'),fs=require('node:fs'),crypto=require('node:crypto');
const source=fs.readFileSync('site/metrics.js','utf8');
function run(overrides={}){
 const events={},calls=[];let next=0;
 const context={location:{origin:'https://alexisnoh37-cell.github.io',pathname:'/streambrief-releases/'},navigator:{},document:{visibilityState:'visible',addEventListener:(key,fn)=>events[key]=fn,getElementById:id=>({addEventListener:(key,fn)=>events[id]=fn})},crypto:{getRandomValues:bytes=>{bytes.set(crypto.createHash('sha256').update('TEST-'+next++).digest());return bytes;}},btoa,Uint8Array,fetch:(url,options)=>{calls.push({url,options});return Promise.resolve({ok:true});},...overrides};
 vm.runInNewContext(source,context);return {context,events,calls};
}
test('one visit per document and independent setup/update click counts without download interception',()=>{
 const {calls,events}=run();assert.equal(calls.length,1);events.visibilitychange();assert.equal(calls.length,1);
 events['setup-download']();events['update-direct-download']();events['update-download']();
 assert.deepEqual(calls.map(x=>JSON.parse(x.options.body).event),['visit','setup','update','update']);
 const batches=calls.map(x=>JSON.parse(x.options.body).batch);assert.equal(new Set(batches).size,4);
 for(const x of calls){assert.deepEqual(Object.keys(JSON.parse(x.options.body)).sort(),['batch','event']);assert.match(JSON.parse(x.options.body).batch,/^[-_A-Za-z0-9]{43}$/);assert.equal(x.options.credentials,'omit');assert.equal(x.options.referrerPolicy,'no-referrer');assert.equal(x.options.keepalive,true);}
});
test('hidden tabs wait until visible; privacy signals and local previews do not report',()=>{
 const document={visibilityState:'hidden',addEventListener:(k,fn)=>document.handler=fn,getElementById:()=>null};const s=run({document});assert.equal(s.calls.length,0);document.visibilityState='visible';document.handler();assert.equal(s.calls.length,1);
 for(const options of [{navigator:{doNotTrack:'1'}},{navigator:{globalPrivacyControl:true}},{location:{origin:'http://127.0.0.1:8002',pathname:'/streambrief-releases/'}},{location:{origin:'https://alexisnoh37-cell.github.io',pathname:'/other-project/'}}])assert.equal(run(options).calls.length,0);
});
test('blocked or unavailable statistics never throw from download clicks',()=>{
 const s=run({fetch:()=>{throw Error('TEST network blocked');}});assert.doesNotThrow(()=>s.events['setup-download']());
 assert(!/localStorage|sessionStorage|document\.cookie|preventDefault/.test(source));
});
