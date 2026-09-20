export default async function handler(req,res){
  try{
    const q=req.url.includes('?')?req.url.slice(req.url.indexOf('?')):'';
    const target='https://5s-smart-order.netlify.app/api/admin-state'+q;
    const headers={};
    for(const k of ['content-type','authorization','x-order-tenant','cache-control']) if(req.headers[k]) headers[k]=req.headers[k];
    const init={method:req.method,headers,redirect:'manual'};
    if(req.method!=='GET'&&req.method!=='HEAD'){
      if(typeof req.body==='string'||Buffer.isBuffer(req.body)) init.body=req.body;
      else if(req.body!=null) init.body=JSON.stringify(req.body);
    }
    const r=await fetch(target,init);
    const buf=Buffer.from(await r.arrayBuffer());
    const ct=r.headers.get('content-type'); if(ct) res.setHeader('content-type',ct);
    res.setHeader('cache-control','no-store');
    res.status(r.status).send(buf);
  }catch(e){
    res.status(502).json({error:'Không kết nối được backend hiện tại'});
  }
}
