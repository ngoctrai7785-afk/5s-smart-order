export default function handler(req,res){
  const tenant=String(req.query.tenant||'npp1').replace(/[^a-zA-Z0-9_-]/g,'').slice(0,48)||'npp1';
  const unit=String(req.query.unit||'Ngọc Trai').slice(0,60);
  const account=String(req.query.account||'').slice(0,200);
  const q=new URLSearchParams({mode:'order',view:'customer',tenant,unit,installed:'1',appv:'full-catalog-20260921'});
  if(account)q.set('account',account);
  res.setHeader('content-type','application/manifest+json; charset=utf-8');
  res.setHeader('cache-control','no-store');
  res.status(200).json({
    name:unit+' - Đặt hàng',
    short_name:unit,
    description:'Smart Order - Đặt hàng nhanh',
    start_url:'/dat-hang?'+q.toString(),
    scope:'/',
    display:'standalone',
    background_color:'#ffffff',
    theme_color:'#082ca6',
    icons:[
      {src:'/ngoc-trai-icon-192.png',sizes:'192x192',type:'image/png'},
      {src:'/ngoc-trai-icon-512.png',sizes:'512x512',type:'image/png'}
    ]
  });
}