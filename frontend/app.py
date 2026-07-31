
import streamlit as st
import pandas as pd
import requests


# =====================================================
# Backend Configuration
# =====================================================

BACKEND_URL = "http://backend:7860"


# =====================================================
# Application Title
# =====================================================

st.title("🛒 SuperKart Sales Prediction")


# =====================================================
# Online Prediction
# =====================================================

st.subheader("Online Prediction")


# User Inputs

product_weight = st.number_input("Product Weight", min_value=0.0, value=12.66)

product_sugar_content = st.selectbox("Product Sugar Content", ["Low Sugar", "No Sugar", "Regular"])

product_allocated_area = st.number_input("Product Allocated Area", min_value=0.0, value=0.027)

product_mrp = st.number_input("Product MRP", min_value=0.0, value=117.08)

store_size = st.selectbox("Store Size", ["High", "Medium", "Small"])

store_location_city_type = st.selectbox("Store Location City Type", ["Tier 1", "Tier 2", "Tier 3"])

store_type = st.selectbox("Store Type", ["Departmental Store", "Food Mart", "Supermarket Type1", "Supermarket Type2"])

product_id_char = st.selectbox("Product ID Category", ["FD", "DR", "NC"])

store_age_years = st.number_input("Store Age Years", min_value=0, value=16, step=1)

product_type_category = st.selectbox("Product Type Category", ["Perishables", "Non Perishables"])


# =====================================================
# Prepare Input
# =====================================================

input_data = {
    "Product_Weight": product_weight,
    "Product_Sugar_Content": product_sugar_content,
    "Product_Allocated_Area": product_allocated_area,
    "Product_MRP": product_mrp,
    "Store_Size": store_size,
    "Store_Location_City_Type": store_location_city_type,
    "Store_Type": store_type,
    "Product_Id_char": product_id_char,
    "Store_Age_Years": store_age_years,
    "Product_Type_Category": product_type_category
}


# =====================================================
# Online Prediction Request
# =====================================================

if st.button("Predict", type="primary"):

    try:

        response = requests.post(
            f"{BACKEND_URL}/v1/predict",
            json=input_data,
            timeout=30
        )


        if response.status_code == 200:

            prediction = response.json()["Predicted Sales"]

            st.success(
                f"Predicted Sales: {prediction:.2f}"
            )


        else:

            st.error(
                f"API Error {response.status_code}: {response.text}"
            )


    except requests.exceptions.RequestException as ex:

        st.error(
            f"Unable to connect to backend: {ex}"
        )


# =====================================================
# Batch Prediction
# =====================================================

st.subheader("Batch Prediction")


uploaded_file = st.file_uploader(
    "Upload CSV file for batch prediction",
    type=["csv"]
)


if uploaded_file is not None:

    if st.button("Predict Batch", type="primary"):

        try:

            response = requests.post(
                f"{BACKEND_URL}/v1/predictbatch",
                files={"file": uploaded_file},
                timeout=60
            )


            if response.status_code == 200:

                result = response.json()

                st.success(
                    f"Batch predictions completed! Total Records: {result['Total_Records']}"
                )


                # Get predictions
                predictions = result["Predictions"]


                # Convert to DataFrame
                df = pd.DataFrame(predictions)


                # Display predictions
                st.dataframe(
                    df,
                    use_container_width=True
                )


                # Convert predictions to CSV
                csv = df.to_csv(
                    index=False
                ).encode("utf-8")


                # Download button
                st.download_button(
                    label="Download Predictions",
                    data=csv,
                    file_name="Predicted_Sales.csv",
                    mime="text/csv"
                )


            else:

                st.error(
                    f"API Error {response.status_code}: {response.text}"
                )


        except requests.exceptions.RequestException as ex:

            st.error(
                f"Unable to connect to backend: {ex}"
            )
