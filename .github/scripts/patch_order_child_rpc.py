from pathlib import Path
import re

FILES=[Path("index.html"),Path("smart-order-v26.html")]

SYNC_URL="https://upojgdqkkjwtbrzljffo.supabase.co"
SYNC_KEY="sb_publishable_6b_dKKWTQr64yptqlcSPPA_Ww7achl0"

for p in FILES:
    s=p.read_text(encoding="utf-8")

    old="""const ORDER_CHILD_PHONE=(ORDER_CHILD_PARAMS.get('phone')||'').trim().slice(0,20);
window.ORDER_TENANT_ID=ORDER_TENANT_ID;window.SMART_ORDER_CORE_VERSION=161;"""
    new="""const ORDER_CHILD_PHONE=(ORDER_CHILD_PARAMS.get('phone')||'').trim().slice(0,20);
const ORDER_CHILD_APP_ID=(ORDER_CHILD_PARAMS.get('appid')||ORDER_TENANT_ID).trim().slice(0,80);
const ORDER_CHILD_SYNC_PIN=(ORDER_CHILD_PARAMS.get('syncpin')||'').trim().slice(0,20);
window.ORDER_TENANT_ID=ORDER_TENANT_ID;window.ORDER_CHILD_APP_ID=ORDER_CHILD_APP_ID;window.SMART_ORDER_CORE_VERSION=161;"""
    if old not in s:
        raise SystemExit(f"{p}: không tìm thấy ORDER_CHILD_PHONE")
    s=s.replace(old,new,1)

    pattern=r"""if\(ORDER_TENANT_ID!=='npp1'\)\{\n const prefix='smart_order_'\+ORDER_TENANT_ID\+'__',proto=Storage\.prototype;.*?\n\}\n</script>"""
    repl="""if(ORDER_TENANT_ID!=='npp1'){
 const prefix='smart_order_'+ORDER_TENANT_ID+'__',proto=Storage.prototype;
 for(const method of ['getItem','setItem','removeItem']){const original=proto[method];proto[method]=function(key,...args){return original.call(this,prefix+String(key),...args)}}
 try{const saved=JSON.parse(localStorage.getItem('s5prod')||'[]');if(Array.isArray(saved)&&saved.some(x=>x?.code==='DM006')&&saved.some(x=>x?.code==='DM018')){for(const key of ['s5cat','s5prod','s5promo','s5nppHubHaiQuanLyV2'])localStorage.removeItem(key)}}catch(e){}

 const CHILD_SYNC_URL='"""+SYNC_URL+"""',CHILD_SYNC_KEY='"""+SYNC_KEY+"""';
 const CHILD_TOKEN='order-child:'+ORDER_TENANT_ID+':'+ORDER_CHILD_SYNC_PIN;
 const childJson=(obj,status=200)=>new Response(JSON.stringify(obj),{status,headers:{'content-type':'application/json','cache-control':'no-store'}});
 async function childRpc(name,payload){
   const r=await ORDER_NATIVE_FETCH_V159(CHILD_SYNC_URL+'/rest/v1/rpc/'+name,{method:'POST',headers:{'content-type':'application/json','apikey':CHILD_SYNC_KEY,'authorization':'Bearer '+CHILD_SYNC_KEY},body:JSON.stringify(payload||{}),cache:'no-store'});
   const raw=await r.text();let data=null;try{data=raw?JSON.parse(raw):null}catch(_){data=raw}
   if(!r.ok)throw new Error((data&&data.message)||raw||('HTTP '+r.status));
   return data
 }
 async function childGetEnvelope(){return await childRpc('manager_app_get_state',{p_app_id:ORDER_CHILD_APP_ID,p_pin:ORDER_CHILD_SYNC_PIN})}
 async function childGetState(){
   const e=await childGetEnvelope(),d=e&&typeof e==='object'&&'data'in e?e.data:e;
   return d&&typeof d==='object'?d:{}
 }
 async function childSaveState(state){return await childRpc('manager_app_save_state',{p_app_id:ORDER_CHILD_APP_ID,p_pin:ORDER_CHILD_SYNC_PIN,p_data:state})}
 function childAuthOk(headers){return String(headers.get('authorization')||'')==='Bearer '+CHILD_TOKEN}
 async function childApi(url,init){
   const method=String(init.method||'GET').toUpperCase(),headers=new Headers(init.headers||{}),path=url.pathname;
   let body={};if(init.body){try{body=typeof init.body==='string'?JSON.parse(init.body):init.body}catch(_){}}
   if(path==='/api/admin-state'){
     let state=await childGetState(),auth=state.__orderAuth||{};
     if(method==='POST'&&body.action==='login'){
       if(String(body.phone||'').trim()!==String(auth.phone||'').trim()||String(body.pin||'')!==String(auth.adminPin||''))return childJson({error:'Số điện thoại hoặc PIN không đúng'},401);
       return childJson({ok:true,token:CHILD_TOKEN})
     }
     if(!childAuthOk(headers))return childJson({error:'Phiên quản trị không hợp lệ'},401);
     if(method==='GET')return childJson({ok:true,state});
     if(body.action==='save'){
       const next=body.state&&typeof body.state==='object'?body.state:{};
       next.__orderAuth=auth;
       await childSaveState(next);return childJson({ok:true,state:next})
     }
     if(body.action==='change-pin'){
       if(String(body.currentPin||'')!==String(auth.adminPin||''))return childJson({error:'PIN hiện tại không đúng'},400);
       if(!/^\\d{4}$/.test(String(body.newPin||'')))return childJson({error:'PIN mới phải gồm đúng 4 số'},400);
       auth={...auth,adminPin:String(body.newPin)};state.__orderAuth=auth;await childSaveState(state);return childJson({ok:true})
     }
     return childJson({error:'Thao tác chưa hỗ trợ'},400)
   }
   if(path==='/api/catalog'){
     const state=await childGetState();return childJson({ok:true,state})
   }
   if(path==='/api/customers'){
     const state=await childGetState();state.customers=Array.isArray(state.customers)?state.customers:[];
     const phone=String(body.phone||body.customer?.phone||'').trim();
     if(body.action==='lookup'){return childJson({ok:true,customer:state.customers.find(c=>String(c.phone||'').trim()===phone)||null})}
     if(body.action==='register'&&body.customer){
       let c=state.customers.find(x=>String(x.phone||'').trim()===String(body.customer.phone||'').trim());
       if(c)Object.assign(c,body.customer);else{c={...body.customer};state.customers.push(c)}
       await childSaveState(state);return childJson({ok:true,customer:c})
     }
     return childJson({error:'Yêu cầu khách hàng không hợp lệ'},400)
   }
   if(path==='/api/orders'){
     const state=await childGetState();state.orders=Array.isArray(state.orders)?state.orders:[];
     if(body.action==='history'){
       const phone=String(body.phone||'').trim(),orders=state.orders.filter(o=>String(o.phone||o.customerPhone||'').trim()===phone).slice().reverse();
       return childJson({ok:true,orders})
     }
     if(body.order){
       const o={...body.order};let i=state.orders.findIndex(x=>String(x.id||'')===String(o.id||''));if(i>=0)state.orders[i]=o;else state.orders.push(o);
       if(body.customer){state.customers=Array.isArray(state.customers)?state.customers:[];let c=state.customers.find(x=>String(x.phone||'').trim()===String(body.customer.phone||'').trim());if(c)Object.assign(c,body.customer);else state.customers.push({...body.customer})}
       await childSaveState(state);return childJson({ok:true,order:o})
     }
     return childJson({error:'Yêu cầu đơn hàng không hợp lệ'},400)
   }
   if(path==='/api/tenant-usage'){
     const state=await childGetState(),raw=JSON.stringify(state),enc=new TextEncoder().encode(raw);
     return childJson({ok:true,usage:{tenant:ORDER_TENANT_ID,version:26,appBytes:0,databaseBytes:enc.byteLength,imageBytes:0,counts:{products:(state.products||[]).length,customers:(state.customers||[]).length,orders:(state.orders||[]).length}}})
   }
   return null
 }
 window.fetch=async(input,init={})=>{
   try{
     const raw=typeof input==='string'?input:input.url,url=new URL(raw,location.origin);
     if(url.origin===location.origin&&url.pathname.startsWith('/api/')){
       const headers=new Headers(init.headers||(typeof input==='object'?input.headers:undefined));headers.set('x-order-tenant',ORDER_TENANT_ID);init={...init,headers};
       if(ORDER_CHILD_SYNC_PIN){const handled=await childApi(url,init);if(handled)return handled}
     }
   }catch(e){console.warn('Order child API fallback:',e)}
   return ORDER_NATIVE_FETCH_V159(input,init)
 };
}
</script>"""
    s2,n=re.subn(pattern,repl,s,count=1,flags=re.S)
    if n!=1:
        raise SystemExit(f"{p}: không thay được fetch child block")
    s=s2

    # Propagate child storage keys into shared customer links
    old2="""function orderEntryLink(source='link'){let url=new URL('/dat-hang?v=154&source='+source+'&onboard=1',location.origin);url.searchParams.set('tenant',ORDER_TENANT_ID);if(ORDER_CHILD_UNIT)url.searchParams.set('unit',ORDER_CHILD_UNIT);if(ORDER_CHILD_PHONE)url.searchParams.set('phone',ORDER_CHILD_PHONE);return url.href}"""
    new2="""function orderEntryLink(source='link'){let url=new URL('/dat-hang?v=154&source='+source+'&onboard=1',location.origin);url.searchParams.set('tenant',ORDER_TENANT_ID);if(ORDER_CHILD_UNIT)url.searchParams.set('unit',ORDER_CHILD_UNIT);if(ORDER_CHILD_PHONE)url.searchParams.set('phone',ORDER_CHILD_PHONE);if(ORDER_CHILD_SYNC_PIN){url.searchParams.set('appid',ORDER_CHILD_APP_ID);url.searchParams.set('syncpin',ORDER_CHILD_SYNC_PIN)}return url.href}"""
    if old2 in s:s=s.replace(old2,new2,1)

    old3="""if(ORDER_CHILD_PHONE)url.searchParams.set('phone',ORDER_CHILD_PHONE);url.searchParams.set('onboard','1');"""
    new3="""if(ORDER_CHILD_PHONE)url.searchParams.set('phone',ORDER_CHILD_PHONE);if(ORDER_CHILD_SYNC_PIN){url.searchParams.set('appid',ORDER_CHILD_APP_ID);url.searchParams.set('syncpin',ORDER_CHILD_SYNC_PIN)}url.searchParams.set('onboard','1');"""
    s=s.replace(old3,new3,1)

    p.write_text(s,encoding="utf-8")
