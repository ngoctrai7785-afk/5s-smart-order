import { getStore } from "@netlify/blobs";

const headers = {"content-type":"application/json; charset=utf-8", "cache-control":"no-store"};
const reply = (data, status=200) => new Response(JSON.stringify(data), {status, headers});

export default async (req) => {
  if (req.method === "OPTIONS") return new Response(null, {status: 204, headers});

  const store = getStore({name:"5s-smart-order", consistency:"strong"});
  const tenant = String(req.headers.get("x-order-tenant") || "npp1").toLowerCase().replace(/[^a-z0-9_-]+/g,"-").slice(0,48) || "npp1";
  const key = tenant === "npp1" ? "shared-data-v1" : "shared-data-v1-" + tenant;
  let data = await store.get(key, {type:"json", consistency:"strong"});
  if (!data) data = {orders:[], customers:[], messages:[]};
  data.orders = data.orders || [];
  data.customers = data.customers || [];
  data.messages = data.messages || [];

  if (req.method === "GET") return reply(data);
  if (req.method !== "POST") return reply({error:"Method not allowed"}, 405);

  try {
    const body = await req.json();
    if (body.action === "createOrder") {
      const order = body.order;
      const customer = body.customer;
      if (!order?.id || !customer?.id) return reply({error:"Thiếu dữ liệu đơn hàng"}, 400);
      data.orders = (data.orders || []).filter(x => x.id !== order.id);
      data.orders.unshift(order);
      data.customers = data.customers || [];
      const i = data.customers.findIndex(x => x.id === customer.id || (customer.phone && x.phone === customer.phone));
      if (i >= 0) data.customers[i] = {...data.customers[i], ...customer};
      else data.customers.unshift(customer);
    } else if (body.action === "updateOrder") {
      const i = (data.orders || []).findIndex(x => x.id === body.id);
      if (i < 0) return reply({error:"Không tìm thấy đơn"}, 404);
      data.orders[i] = {...data.orders[i], ...body.patch};
    } else if (body.action === "updateCustomer") {
      const i = (data.customers || []).findIndex(x => x.id === body.id);
      if (i < 0) return reply({error:"Không tìm thấy khách"}, 404);
      data.customers[i] = {...data.customers[i], ...body.patch};
    } else if (body.action === "sendMessage") {
      const m = body.message || {};
      if (!m.id || !m.customerId || !m.sender || !String(m.text || "").trim()) return reply({error:"Thiếu dữ liệu tin nhắn"}, 400);
      const clean = {
        id:String(m.id).slice(0,80),
        customerId:String(m.customerId).slice(0,80),
        customerName:String(m.customerName||"").slice(0,120),
        customerPhone:String(m.customerPhone||"").slice(0,30),
        orderId:String(m.orderId||"").slice(0,80),
        sender:m.sender === "admin" ? "admin" : "customer",
        text:String(m.text||"").trim().slice(0,1200),
        createdAt:m.createdAt || new Date().toISOString(),
        readByCustomer:m.sender === "customer",
        readByAdmin:m.sender === "admin"
      };
      data.messages.push(clean);
      if (data.messages.length > 5000) data.messages = data.messages.slice(-5000);
    } else if (body.action === "markMessagesRead") {
      const customerId = String(body.customerId || "");
      const reader = body.reader === "admin" ? "admin" : "customer";
      if (!customerId) return reply({error:"Thiếu khách hàng"}, 400);
      data.messages.forEach(m => {
        if (String(m.customerId) !== customerId) return;
        if (reader === "admin" && m.sender === "customer") m.readByAdmin = true;
        if (reader === "customer" && m.sender === "admin") m.readByCustomer = true;
      });
    } else {
      return reply({error:"Thao tác không hợp lệ"}, 400);
    }
    await store.setJSON(key, data);
    return reply({ok:true, ...data});
  } catch (error) {
    return reply({error:error?.message || "Lỗi máy chủ"}, 500);
  }
};

export const config = { path: "/api/orders" };
