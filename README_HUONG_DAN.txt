5S SMART ORDER - BẢN GITHUB + NETLIFY

CẤU TRÚC QUAN TRỌNG:
netlify/functions/orders.mjs

KHÔNG đưa riêng orders.mjs ra ngoài thư mục này.
KHÔNG tải nguyên file ZIP vào GitHub.

CÁCH ĐƯA LÊN GITHUB:
1. Giải nén file ZIP này.
2. Mở thư mục 5S_SMART_ORDER_GITHUB_READY.
3. Dùng GitHub Desktop để đưa nguyên thư mục lên repository 5s-smart-order.
4. Commit to main và Push origin.

CÁCH NỐI NETLIFY:
1. Netlify > Add new project > Import an existing project.
2. Chọn GitHub và repository 5s-smart-order.
3. Branch: main.
4. Base directory: để trống.
5. Build command: để trống.
6. Publish directory: .
7. Deploy.

LINK SAU KHI DEPLOY:
- Đặt hàng: https://TEN-SITE.netlify.app/dat-hang
- Quản lý: https://TEN-SITE.netlify.app/quan-ly
- Kiểm tra API: https://TEN-SITE.netlify.app/api/orders

Khi API hoạt động, đường dẫn /api/orders sẽ hiện dữ liệu JSON thay vì báo 404.
