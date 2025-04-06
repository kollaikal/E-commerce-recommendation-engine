# app.py
import streamlit as st
import json
import hashlib
import logging
from services.llm_service import LLMService  # Adjust the path if needed

logging.basicConfig(level=logging.INFO)

# Initialize the LLM service
llm_service = LLMService()

def load_products() -> list:
    """Load the product catalog from a JSON file."""
    with open("data/products.json", "r") as f:
        return json.load(f)

def filter_products(products: list, preferences: dict) -> list:
    """
    Filter the product catalog based on user preferences.
    - Price Range: "all", "0-50", "50-100", "100+"
    - Categories: list of categories
    - Brands: list of brands
    """
    filtered = products

    # Filter by price range
    price_range = preferences.get("priceRange", "all")
    if price_range != "all":
        if price_range == "0-50":
            filtered = [p for p in filtered if p.get("price", 0) <= 50]
        elif price_range == "50-100":
            filtered = [p for p in filtered if 50 < p.get("price", 0) <= 100]
        elif price_range == "100+":
            filtered = [p for p in filtered if p.get("price", 0) > 100]

    # Filter by categories if any are selected
    selected_categories = preferences.get("categories", [])
    if selected_categories:
        filtered = [p for p in filtered if p.get("category") in selected_categories]

    # Filter by brands if any are selected
    selected_brands = preferences.get("brands", [])
    if selected_brands:
        filtered = [p for p in filtered if p.get("brand") in selected_brands]

    return filtered

# Load products
all_products = load_products()

st.title("AI-Powered Product Recommendation Engine")
st.write("Get personalized product recommendations using Replicate's meta-llama-3-8b-instruct model.")

# Sidebar: User Preferences
st.sidebar.header("User Preferences")
price_range = st.sidebar.selectbox("Select Price Range", options=["all", "0-50", "50-100", "100+"])
categories = st.sidebar.multiselect("Select Categories", options=list({p["category"] for p in all_products}))
brands = st.sidebar.multiselect("Select Brands", options=list({p["brand"] for p in all_products}))

preferences = {
    "priceRange": price_range,
    "categories": categories,
    "brands": brands
}

# Filter products for catalog display based on preferences
filtered_products = filter_products(all_products, preferences)

# Browsing history stored in session state
if "browsing_history" not in st.session_state:
    st.session_state["browsing_history"] = []
browsing_history = st.session_state["browsing_history"]

st.header("Product Catalog")
if filtered_products:
    for product in filtered_products:
        col1, col2 = st.columns([3, 1])
        with col1:
            st.subheader(product["name"])
            st.write(f"Category: {product['category']} | Brand: {product['brand']} | Price: ${product['price']}")
        with col2:
            if st.button("View", key=product["id"]):
                if product["id"] not in browsing_history:
                    browsing_history.append(product["id"])
                    st.session_state["browsing_history"] = browsing_history
                st.success(f"Added {product['name']} to browsing history.")
else:
    st.write("No products match your current filters.")

st.header("Browsing History")
if browsing_history:
    history_products = [p for p in all_products if p["id"] in browsing_history]
    for hp in history_products:
        st.write(f"{hp['name']} ({hp['id']})")
    if st.button("Clear History"):
        st.session_state["browsing_history"] = []
        st.success("Browsing history cleared.")
else:
    st.write("No browsing history yet. Click 'View' on a product to add it.")

st.header("Recommendations")
if st.button("Get Recommendations"):
    with st.spinner("Generating recommendations..."):
        # Use the full product list for LLM recommendations or use filtered_products based on design choice.
        # Here, I'm using the full list to allow the LLM to potentially recommend products not currently visible.
        result = llm_service.generate_recommendations(preferences, browsing_history, all_products)
    if "error" in result:
        st.error("Error generating recommendations: " + result["error"])
    else:
        recs = result["recommendations"]
        if not recs:
            st.warning("No recommendations returned.")
        else:
            for rec in recs:
                prod = rec["product"]
                st.subheader(prod["name"])
                st.write(f"**Category:** {prod['category']}")
                st.write(f"**Brand:** {prod['brand']} | **Price:** ${prod['price']}")
                st.write(f"**Explanation:** {rec['explanation']}")
                st.write(f"**Confidence Score:** {rec['confidence_score']}")
