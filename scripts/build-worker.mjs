import fs from 'node:fs/promises';
import path from 'node:path';
import {build} from 'esbuild';
const root=process.cwd(),dist=path.join(root,'dist'),assets={};
async function walk(dir){for(const entry of await fs.readdir(dir,{withFileTypes:true})){const full=path.join(dir,entry.name);if(entry.isDirectory()){if(!['server','.openai'].includes(entry.name))await walk(full)}else{const name='/'+path.relative(dist,full).replaceAll('\\','/');const ext=path.extname(name);assets[name]={body:await fs.readFile(full,'utf8'),type:ext==='.html'?'text/html;charset=utf-8':ext==='.css'?'text/css;charset=utf-8':ext==='.js'?'application/javascript;charset=utf-8':'text/plain'}}}}
await walk(dist);
let library;
try{library=JSON.parse(await fs.readFile('backend/data/library.json','utf8'))}catch{
 const d=JSON.parse(await fs.readFile('backend/data/demo.json','utf8'));
 library=d.sources.filter(s=>s.excerpt).map(s=>({...s,content:[{page:s.page,text:s.excerpt}]}));
 console.log('Full local library unavailable. Building with verified short excerpts; run ingestion for full retrieval.');
}
const passages=library.flatMap(d=>(d.kind==='Annual report'?d.content.slice(0,8):d.content).map(p=>({ticker:d.ticker,source_id:d.id,page:p.page,text:p.text})));
const entry=`import {api} from './worker/api.mjs';
const assets=${JSON.stringify(assets)};
const passages=${JSON.stringify(passages)};
export default {async fetch(request,env,ctx){
const url=new URL(request.url);
if(url.pathname.startsWith('/api/')){try{return await api(request,env,passages)}catch{return new Response(JSON.stringify({detail:'Research is temporarily unavailable.'}),{status:503,headers:{'Content-Type':'application/json'}})}}
if(!['GET','HEAD'].includes(request.method))return new Response('Method not allowed',{status:405});
const asset=assets[url.pathname==='/'?'/index.html':url.pathname];
if(!asset)return new Response('Not found',{status:404});
return new Response(request.method==='HEAD'?null:asset.body,{headers:{'Content-Type':asset.type,'Cache-Control':url.pathname.startsWith('/assets/')?'public,max-age=31536000,immutable':'no-cache','X-Content-Type-Options':'nosniff','Referrer-Policy':'strict-origin-when-cross-origin','Content-Security-Policy':"default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; img-src 'self' data:; connect-src 'self'; frame-ancestors 'self' https://*.chatgpt.com https://chatgpt.com"}});
}};`;
await fs.mkdir(path.join(dist,'server'),{recursive:true});
await build({stdin:{contents:entry,resolveDir:root,sourcefile:'finn-worker.js'},outfile:path.join(dist,'server/index.js'),bundle:true,format:'esm',platform:'browser',target:'es2022',minify:true});
console.log(`Built FINN Worker: ${Object.keys(assets).length} assets; ${passages.length} indexed pages.`);
