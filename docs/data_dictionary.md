# Olist data dictionary

- customers: one row per customer record. customer_id is unique per order; customer_unique_id identifies the same real person across orders.
- orders: one row per order. order_status values include delivered, shipped, canceled.
- order_items: one row per product in an order. Revenue = price. freight_value is shipping cost, excluded from revenue unless asked.
- order_payments: one order can have several payment rows. payment_value is the amount paid.
- order_reviews: review_score is 1 to 5.
- products: product_category_name is in Portuguese; join product_category_name_translation for English names.
- sellers: one row per seller, with seller_state.
- Delivery delay = order_delivered_customer_date - order_estimated_delivery_date.
- Round money results to 2 decimals.