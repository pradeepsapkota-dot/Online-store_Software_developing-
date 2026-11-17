import streamlit as st
import time
from product_operations import (
    get_all_products,
    search_products,
    add_products,
    delete_products
)

st.set_page_config(page_title="Online Store", layout="centered")
st.title("🛒 Online Store")
st.write("Welcome to the Online Store Application")

# Create tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "All Products",
    "Search Products",
    "Add Product",
    "Delete Product"
])

# ====================== ALL PRODUCTS ======================
with tab1:
    st.subheader("All Products")

    products = get_all_products()

    if products:
        table_data = [{
            "ID": p[0],
            "Name": p[1],
            "Category": p[2],
            "Price": f"€{float(p[3]):.2f}",
            "Stock": p[4]
        } for p in products]

        st.dataframe(table_data, width="stretch", hide_index=True)
    else:
        st.warning("No products found or database connection failed.")

# ====================== SEARCH PRODUCTS ======================
with tab2:
    st.subheader("Search Products")

    search_type = st.radio("Search by:", ["Name", "Category"], horizontal=True)

    if search_type == "Name":
        keyword = st.text_input("Enter product name")
        st.caption("Example: Wireless Mouse, Keyboard")
    else:
        keyword = st.text_input("Enter category")
        st.caption(
            "Available categories: Electronics, Accessories, Home, Stationery")

    if st.button("Search"):
        if keyword.strip() == "":
            st.warning("Please enter a keyword to search.")
        else:
            results = search_products(keyword)

            if results:
                table_data = [{
                    "ID": p[0],
                    "Name": p[1],
                    "Category": p[2],
                    "Price (£)": float(p[3]),
                    "Stock": p[4]
                } for p in results]

                st.dataframe(table_data, width="stretch", hide_index=True)
            else:
                st.info("No products found.")

# ====================== ADD PRODUCT ======================
with tab3:
    st.subheader("Add New Product")

    with st.form("add_product_form", clear_on_submit=True):
        name = st.text_input("Product Name")
        category = st.text_input("Category")
        price = st.number_input(
            "Price (€)", min_value=10.0, step=0.01, format="%.2f")
        stock = st.number_input("Stock Quantity", min_value=0, step=1)

        submitted = st.form_submit_button("Add Product")

        if submitted:
            if not name.strip() or not category.strip():
                st.error("Product Name and Category are required.")
            else:
                success = add_products(name, category, price, stock)
                if success == "Exists":
                    st.warning(f"{name.strip()} already exists in the store")
                elif success:
                    st.success("Product added successfully!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Failed to add product."
                             "Product is already listed")

# ====================== DELETE PRODUCT ======================
with tab4:
    st.subheader("Delete Product")
    st.warning("This action cannot be undone.")

    products = get_all_products()

    if products:
        product_options = {
            f"ID {p[0]} - {p[1]} (Stock: {p[4]})": p[0]
            for p in products
        }

        selected = st.selectbox(
            "Select product to delete", list(product_options.keys()))
        confirm = st.checkbox("I confirm that I want to delete this product")

        if st.button("Delete Product"):
            if not confirm:
                st.warning("Please tick the confirmation box before deleting.")
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
