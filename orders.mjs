import { getStore } from "@netlify/blobs";

const headers = {"content-type":"application/json; charset=utf-8", "cache-control":"no-store"};
const reply = (data, status=200) => new Response(JSON.stringify(data), {status, headers});

export default async (req) => {
  const store = getStore({name:"5s-smart-order", consistency:"strong"});
  const key = "shared-data-v1";
  let data = await store.get(key, {type:"json", consistency:"strong"});
  if (!data) data = {orders:[], customers:[]};

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
