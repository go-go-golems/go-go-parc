// node run-media-browser.cjs /absolute/path/to/playwright/module
// A separate browser and ephemeral loopback server; never touches user tabs.
const fs=require('node:fs'),path=require('node:path'),http=require('node:http');
const assert=require('node:assert/strict');
const {chromium}=require(process.argv[2]);
function boxes(bytes,depth=0){
 if(depth>8||bytes.length>4*1024*1024)throw Error('box admission');
 const result=[];let offset=0;
 while(offset<bytes.length){
  if(result.length>=512||bytes.length-offset<8)throw Error('truncated box');
  let size=bytes.readUInt32BE(offset),header=8;
  const type=bytes.toString('ascii',offset+4,offset+8);
  if(size===1){if(bytes.length-offset<16)throw Error('truncated extended size');size=Number(bytes.readBigUInt64BE(offset+8));header=16;}
  if(size===0)size=bytes.length-offset;
  if(!Number.isSafeInteger(size)||size<header||offset+size>bytes.length)throw Error('invalid box size');
  const box={type,offset,size};
  if(['moov','trak','mdia','minf','stbl','mvex','moof','traf'].includes(type))box.children=boxes(bytes.subarray(offset+header,offset+size),depth+1);
  result.push(box);offset+=size;
 }
 return result;
}
(async()=>{
 assert.throws(()=>boxes(Buffer.from([0,0,0,4,109,111,111,118])));
 assert.throws(()=>boxes(Buffer.from([0,0,0,20,109,111,111,118])));
 const root=__dirname,media=path.join(root,'outputs/media/no-b');
 const playlist='#EXTM3U\n#EXT-X-VERSION:7\n#EXT-X-TARGETDURATION:2\n#EXT-X-PLAYLIST-TYPE:VOD\n#EXT-X-MAP:URI="init.mp4"\n'+
  [0,1,2].map(i=>(i===1?'#EXT-X-DISCONTINUITY\n':'')+'#EXT-X-PROGRAM-DATE-TIME:2026-09-09T00:00:0'+[0,4,6][i]+'.000Z\n#EXTINF:2.000,\nfragment-0'+i+'.m4s\n').join('')+'#EXT-X-ENDLIST\n';
 const files=new Map([['/',fs.readFileSync(path.join(root,'media-browser.html'))],['/presentation.m3u8',Buffer.from(playlist)],
  ...['index.json','init.mp4','fragment-00.m4s','fragment-01.m4s','fragment-02.m4s'].map(n=>['/'+n,fs.readFileSync(path.join(media,n))])]);
 const requests=[];
 const server=http.createServer((req,res)=>{const bytes=files.get(req.url);requests.push({url:req.url,status:bytes?200:404,bytes:bytes?.length||0});
  if(!bytes){res.writeHead(404);res.end();return}
  res.writeHead(200,{'Content-Length':bytes.length,'Content-Type':req.url==='/'?'text/html':req.url.endsWith('.json')?'application/json':req.url.endsWith('.m3u8')?'application/vnd.apple.mpegurl':'video/mp4'});res.end(bytes);});
 await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
 let browser;
 try{
  browser=await chromium.launch({headless:true});
  const page=await browser.newPage();const errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto('http://127.0.0.1:'+server.address().port+'/');
  const result=await page.evaluate(()=>window.exercise());assert.deepEqual(errors,[]);
  const image=Buffer.from(result.image.split(',')[1],'base64');delete result.image;
  result.browser=await browser.version();result.requests=requests;
  result.boxes=Object.fromEntries([...files].filter(([n])=>n.endsWith('.mp4')||n.endsWith('.m4s')).map(([n,b])=>[n,boxes(b)]));
  result.box_walker_tests='two malformed-size inputs rejected';
  const out=path.join(root,'outputs');fs.writeFileSync(path.join(out,'delivery.m3u8'),playlist);
  fs.writeFileSync(path.join(out,'media-browser-frame.png'),image);
  fs.writeFileSync(path.join(out,'media-browser.json'),JSON.stringify(result,null,2)+'\n');
  console.log(JSON.stringify({buffered:result.buffered,frames:[result.first,result.after],cleanup:result.trace.at(-1),browser:result.browser},null,2));
 }finally{if(browser)await browser.close();await new Promise(resolve=>server.close(resolve));}
})().catch(error=>{console.error(error);process.exitCode=1});
