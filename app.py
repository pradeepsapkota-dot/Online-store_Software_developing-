import time

import streamlit as st

from product_operations import (
    get_all_products,
    get_categories,
    search_products,
    add_products,
    delete_products
)
from order_operations import (
    create_order,
    get_all_orders,
    get_order_details,
    update_order_status,
    record_payment,
    get_all_customers
)

STATUS_LIST = ["Pending", "Processing", "Shipped", "Delivered"]
PAYMENT_METHODS = ["Cash", "Card", "Online"]

st.set_page_config(page_title="Online Store", layout="centered")

if "cart" not in st.session_state:
    # list of (product_id, name, price, qty)
    st.session_state.cart = []

# ====================== SIDEBAR MENU ======================
st.sidebar.title("🛒 Online Store")
menu = st.sidebar.radio("Menu", ["Products", "Orders"])


# ====================== PRODUCTS PAGE ======================
def products_page():
    st.title("Products")

    tab1, tab2, tab3, tab4 = st.tabs([
        "All Products",
        "Search Products",
        "Add Product",
        "Delete Product"
    ])

    # ---------- All products ----------
    with tab1:
        st.subheader("All Products")

        products, error = get_all_products()
        categories, _ = get_categories()
        chosen = st.selectbox("Filter by category", [
                              "All"] + categories, key="filter_category")
        if chosen != "All":
            products = [p for p in products if p[2] == chosen]

        if error:
            st.error(error)
        elif products:
            low_stock_products = []
            for p in products:
                if p[4] < 8:
                    low_stock_products.append(p[1])
            if low_stock_products:
                st.warning("Low stock products: " +
                           ",".join(low_stock_products))
            table_data = [{
                "ID": p[0],
                "Name": p[1],
                "Category": p[2],
                "Price": f"€{float(p[3]):.2f}",
                "Stock": p[4]
            } for p in products]

            st.dataframe(table_data, width="stretch", hide_index=True)
        else:
            st.info("No product in the store yet")

    # ---------- Search products ----------
    with tab2:
        st.subheader("Search Products")

        search_type = st.radio(
            "Search by:", ["Name", "Category"], horizontal=True)

        if search_type == "Name":
            keyword = st.text_input("Enter product name")
            st.caption("Example: Wireless Mouse, Keyboard")
        else:
            categories, error = get_categories()
            if categories:
                keyword = st.selectbox("Choose category", categories)
            else:
                keyword = ""
                st.info("No categories available.")

        if st.button("Search"):
            if keyword.strip() == "":
                st.warning("Please enter a keyword to search.")
            else:
                results, error = search_products(keyword)

                if error:
                    st.error(error)
                elif results:
                    table_data = [{
                        "ID": p[0],
                        "Name": p[1],
                        "Category": p[2],
                        "Price": f"€{float(p[3]):.2f}",
                        "Stock": p[4]
                    } for p in results]

                    st.dataframe(table_data, width="stretch", hide_index=True)
                else:
                    st.info("No products found.")

    # ---------- Add product ----------
    with tab3:
        st.subheader("Add New Product")
        categories, _ = get_categories()
        NEW = "+ New category"

        with st.form("add_product_form", clear_on_submit=True):
            name = st.text_input("Product Name")
            chosen = st.selectbox(
                "Category", categories + [NEW], key="add_category")
            new_category = st.text_input("New category name")
            price = st.number_input(
                "Price (€)", min_value=0.0, value=10.0, step=0.1, format="%.2f")
            stock = st.number_input("Stock Quantity", min_value=0, step=1)

            submitted = st.form_submit_button("Add Product")

            if submitted:
                if chosen == NEW:
                    category = new_category.strip()
                    for c in categories:
                        if c.lower() == category.lower():
                            category = c
                            break
                else:
                    category = chosen
                if not name.strip() or not category.strip():
                    st.error("Product Name and Category are required.")
                else:
                    success, message = add_products(
                        name, category, price, stock)
                    if success:
                        st.success(message)
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(message)
    # ---------- Delete product ----------
    with tab4:
        st.subheader("Delete Product")
        st.warning("This action cannot be undone.")

        products, error = get_all_products()

        if error:
            st.error(error)
        elif products:
            product_options = {
                f"ID {p[0]} - {p[1]} (Stock: {p[4]})": p[0]
                for p in products
            }

            selected = st.selectbox(
                "Select product to delete", list(product_options.keys()))
            confirm = st.checkbox(
                "I confirm that I want to delete this product")

            if st.button("Delete Product"):
                if not confirm:
                    st.warning(
                        "Please tick the confirmation box before deleting.")
                else:
                    product_id = product_options[selected]
                    success, message = delete_products(product_id)

                    if success:
                        st.success(message)
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(message)
        else:
            st.info("No products available to delete.")


# ====================== ORDERS PAGE ======================
def orders_page():
    st.title("Orders")

    tab1, tab2, tab3 = st.tabs([
        "Create Order",
        "Order List",
        "Payments"
    ])

    # ---------- Create order ----------
    with tab1:
        st.subheader("Create Order")

        flash = st.session_state.pop("order_flash", None)
        if flash:
            st.success(flash)

        customers = get_all_customers()
        products, error = get_all_products()

        if not customers:
            st.warning("No customers found or database connection failed.")
        elif error:
            st.error(error)
        elif not products:
            st.warning("No products found or database connection failed.")
        else:
            customer_options = {
                f"ID {c[0]} - {c[1]} {c[2]}": c[0] for c in customers
            }
            customer_label = st.selectbox(
                "Customer", list(customer_options.keys()))
            customer_id = customer_options[customer_label]

            in_stock = [p for p in products if p[4] > 0]

            if not in_stock:
                st.info("All products are out of stock.")
            else:
                product_options = {
                    f"ID {p[0]} - {p[1]} (€{float(p[3]):.2f}, "
                    f"Stock: {p[4]})": p
                    for p in in_stock
                }
                product_label = st.selectbox(
                    "Product", list(product_options.keys()))
                product = product_options[product_label]

                quantity = st.number_input(
                    "Quantity", min_value=1, max_value=int(product[4]),
                    value=1, step=1)

                if st.button("Add to order"):
                    pid = int(product[0])
                    qty = int(quantity)

                    for i, line in enumerate(st.session_state.cart):
                        if line[0] == pid:
                            new_qty = line[3] + qty
                            if new_qty > product[4]:
                                st.error(
                                    f"Only {product[4]} units of "
                                    f"{product[1]} are in stock.")
                            else:
                                st.session_state.cart[i] = (
                                    pid, line[1], line[2], new_qty)
                                st.rerun()
                            break
                    else:
                        st.session_state.cart.append(
                            (pid, product[1], float(product[3]), qty))
                        st.rerun()

            st.markdown("#### Order items")

            if st.session_state.cart:
                cart_rows = [{
                    "Product ID": line[0],
                    "Product": line[1],
                    "Unit price": f"€{line[2]:.2f}",
                    "Quantity": line[3],
                    "Subtotal": f"€{line[2] * line[3]:.2f}"
                } for line in st.session_state.cart]

                st.dataframe(cart_rows, width="stretch", hide_index=True)

                total = sum(
                    line[2] * line[3] for line in st.session_state.cart)
                st.write(f"**Order total: €{total:.2f}**")

                col_a, col_b = st.columns(2)

                with col_a:
                    if st.button("Create Order", type="primary"):
                        items = [(line[0], line[3])
                                 for line in st.session_state.cart]
                        order_id = create_order(int(customer_id), items)

                        if order_id is None:
                            st.error(
                                "Order could not be created. Check the "
                                "stock and try again.")
                        else:
                            st.session_state.cart = []
                            st.session_state.order_flash = (
                                f"Order #{order_id} created successfully!")
                            st.rerun()

                with col_b:
                    if st.button("Clear order"):
                        st.session_state.cart = []
                        st.rerun()
            else:
                st.info("No products added to the order yet.")

    # ---------- Order list ----------
    with tab2:
        st.subheader("Order List")

        orders = get_all_orders()

        if orders:
            order_rows = [{
                "Order ID": o[0],
                "Customer": f"{o[2]} {o[3]}",
                "Date": o[4],
                "Status": o[5],
                "Total": f"€{float(o[6]):.2f}"
            } for o in orders]

            st.dataframe(order_rows, width="stretch", hide_index=True)

            st.markdown("#### Order details")

            order_ids = [o[0] for o in orders]
            selected_order = st.selectbox(
                "Select order", order_ids, key="details_order")

            details = get_order_details(selected_order)

            if details is None:
                st.error("Could not load order details.")
            else:
                order = details["order"]
                st.write(
                    f"**Customer:** {order[2]} {order[3]}  \n"
                    f"**Date:** {order[4]}  \n"
                    f"**Status:** {order[5]}  \n"
                    f"**Total:** €{float(order[6]):.2f}")

                item_rows = [{
                    "Product ID": i[1],
                    "Product": i[2],
                    "Quantity": i[3],
                    "Unit price": f"€{float(i[4]):.2f}",
                    "Subtotal": f"€{float(i[4]) * i[3]:.2f}"
                } for i in details["items"]]
                st.dataframe(item_rows, width="stretch", hide_index=True)

                payment = details["payment"]
                if payment:
                    st.write(
                        f"**Payment:** {payment[4]} · {payment[2]} · "
                        f"€{float(payment[1]):.2f} · {payment[3]}")
                else:
                    st.info("No payment recorded for this order yet.")

                st.markdown("#### Update order status")

                current_status = order[5]
                new_status = st.selectbox(
                    "New status", STATUS_LIST,
                    index=STATUS_LIST.index(current_status)
                    if current_status in STATUS_LIST else 0)

                if st.button("Update status"):
                    if update_order_status(selected_order, new_status):
                        st.success(
                            f"Order #{selected_order} is now {new_status}.")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("Could not update the order status.")
        elif orders is None:
            st.warning("Could not load orders. Database connection failed.")
        else:
            st.info("No orders yet.")

    # ---------- Payments ----------
    with tab3:
        st.subheader("Payments")

        orders = get_all_orders()

        if orders:
            payment_rows = []
            unpaid = []

            for o in orders:
                details = get_order_details(o[0])
                payment = details["payment"] if details else None

                payment_rows.append({
                    "Order ID": o[0],
                    "Customer": f"{o[2]} {o[3]}",
                    "Amount": f"€{float(o[6]):.2f}",
                    "Method": payment[2] if payment else "-",
                    "Payment status": payment[4] if payment else "Not paid",
                    "Order status": o[5]
                })

                if payment is None:
                    unpaid.append(o)

            st.dataframe(payment_rows, width="stretch", hide_index=True)

            st.markdown("#### Record payment")

            if unpaid:
                unpaid_options = {
                    f"Order #{o[0]} - {o[2]} {o[3]} "
                    f"(€{float(o[6]):.2f})": o[0]
                    for o in unpaid
                }
                order_label = st.selectbox(
                    "Unpaid order", list(unpaid_options.keys()))
                method = st.selectbox("Payment method", PAYMENT_METHODS)

                if st.button("Record payment"):
                    order_id = unpaid_options[order_label]

                    if record_payment(order_id, method):
                        st.success(
                            f"Payment recorded for order #{order_id}. "
                            "Pending orders are now Processing.")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("Could not record the payment.")
            else:
                st.info("All orders have been paid.")
        elif orders is None:
            st.warning("Could not load orders. Database connection failed.")
        else:
            st.info("No orders yet.")


# ====================== PAGE ROUTER ======================
if menu == "Products":
    products_page()
else:
    orders_page()
