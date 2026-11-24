# Business rules
- Active seller: a seller with at least 10 distinct delivered orders.
- Best-selling product: the product with the most order_items rows in delivered orders (units sold).
- Order payment total: SUM(payment_value) per order_id from order_payments. Never add payments by joining to order_items, because that double counts.
- High-value order: an order whose total payment value is over 500.
- Fast delivery: delivered within 7 days of purchase.
- Repeat customer: a customer_unique_id with more than one order.
- Cancellation rate: canceled orders divided by all orders.