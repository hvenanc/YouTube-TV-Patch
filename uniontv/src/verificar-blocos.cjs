const fs=require('fs'),vm=require('vm'),assert=require('assert');
const path=require('path');
const original=fs.readFileSync(process.argv[2]).subarray(0x853944,0x853944+22137).toString('ascii');
const files=['original','r4'];
const replacement=fs.readFileSync(path.join(__dirname,'cobalt-startup-patched.js'),'utf8');
const bounds=[[0,305],[305,594],[594,10851],[10851,22137]];
(async()=>{for(const [index,file]of files.entries()){
 const source=index===0?original:replacement;const context=vm.createContext({});
 // The native loader evaluates every embedded array independently, before the
 // Window bindings exist. Do not supply DOM/timers at this stage.
 for(let i=0;i<4;i++)vm.runInContext(source.slice(...bounds[i]),context,{filename:'native-block-'+i+'.js',timeout:2000});
 if(index===1){assert.equal(vm.runInContext('typeof document',context),'undefined');assert.equal(vm.runInContext('typeof setTimeout',context),'undefined');assert.equal(vm.runInContext('JSON.parse(\'{"playerAds":true}\').playerAds',context),false);}
 const timers=[];context.document={body:{style:{}}};context.setTimeout=(fn,delay)=>{timers.push({fn,delay})};context.DOMException=DOMException;context.Blob=Blob;context.FormData=FormData;context.XMLHttpRequest=function(){};
 vm.runInContext('FetchInternal={encodeToUTF8:s=>Uint8Array.from(Array.from(s),c=>c.charCodeAt(0)),decodeFromUTF8:a=>String.fromCharCode(...a),isUrlValid:()=>true}',context);
 const result=JSON.parse(await vm.runInContext(`(async()=>{
 const stream=new ReadableStream({start(c){c.enqueue('video');c.close()}});const reader=stream.getReader();const first=await reader.read(),end=await reader.read();
 const response=new Response('{"videoDetails":{"videoId":"keep"},"adPlacements":[1],"nested":{"adSlots":[2],"playerAds":true,"adBreaks":[3]}}');
 return JSON.stringify({first,end,json:await response.json(),text:await new Response('ok').text(),header:new Headers({name:'value'}).get('name'),bytes:new ByteLengthQueuingStrategy({highWaterMark:4}).size(new Uint8Array(3))});})()`,context));
 assert.equal(result.first.value,'video');assert.equal(result.end.done,true);assert.equal(result.text,'ok');assert.equal(result.header,'value');assert.equal(result.bytes,3);assert.equal(result.json.videoDetails.videoId,'keep');
 if(index===1){assert.equal(result.json.adPlacements.length,0);assert.equal(result.json.nested.adSlots.length,0);assert.equal(result.json.nested.playerAds,false);assert.equal(result.json.nested.adBreaks.length,0);
 assert.equal(context.document.body.style.border,'8px solid red');assert.equal(timers.length,1);assert.equal(timers[0].delay,10000);timers[0].fn();assert.equal(context.document.body.style.border,'');
 const body=JSON.parse(vm.runInContext('input={videoId:"keep",playbackContext:{contentPlaybackContext:{signatureTimestamp:123}}};JSON.stringify(input)',context));assert.equal(body.playbackContext.contentPlaybackContext.isInlinePlaybackNoAd,true);assert.equal(body.playbackContext.contentPlaybackContext.signatureTimestamp,123);assert.equal(vm.runInContext('input.playbackContext.contentPlaybackContext.isInlinePlaybackNoAd',context),undefined);
 assert.equal(vm.runInContext('JSON.parse(\'{"n":2}\',(k,v)=>k==="n"?v+1:v).n',context),3);assert.equal(vm.runInContext('JSON.parse(\'{"n":2}\',true).n',context),2);assert.equal(vm.runInContext('JSON.stringify({n:2},(k,v)=>k==="n"?v+1:v,2)',context),JSON.stringify({n:3},null,2));assert.throws(()=>vm.runInContext('JSON.parse("invalid")',context));assert.throws(()=>vm.runInContext('x={};x.x=x;JSON.stringify(x)',context));}
 console.log('PASS',file,': all 4 blocks run independently without DOM; post-binding streams/HTTP/JSON passed',index===1?'; hooks, request flag, immutable input, revivers and transient marker passed':'');
}})().catch(e=>{console.error(e);process.exitCode=1});
