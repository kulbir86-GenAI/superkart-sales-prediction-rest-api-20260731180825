
import pandas as pd
import joblib

from flask import Flask, request, jsonify


# =====================================================
# Initialize Flask App
# =====================================================

superkart_api = Flask("superkart_sales_app")


# =====================================================
# Load Trained Model
# =====================================================

model = joblib.load("forecast_superkart_sales_model.joblib")


# =====================================================
# Model Input Columns
# =====================================================

MODEL_COLUMNS = [
    "Product_Weight",
    "Product_Sugar_Content",
    "Product_Allocated_Area",
    "Product_MRP",
    "Store_Size",
    "Store_Location_City_Type",
    "Store_Type",
    "Product_Id_char",
    "Store_Age_Years",
    "Product_Type_Category"
]


# =====================================================
# Home Endpoint
# =====================================================

@superkart_api.route("/", methods=["GET"])
def home():

    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>SuperKart Sales API</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                text-align: center;
                padding: 50px;
                background-color: #f4f4f4;
            }

            h1 {
                color: #333;
                font-size: 3em;
            }

            p {
                color: #666;
                font-size: 1.5em;
                margin-top: 20px;
            }
        </style>
    </head>

    <body>
        <h1>Welcome to SuperKart Sales Prediction API.</h1>
        <p>Use /v1/predict for online prediction.</p>
        <p>Use /v1/predictbatch for batch prediction.</p>
    </body>
    </html>
    """

    return html


# =====================================================
# Online Prediction Endpoint
# =====================================================

@superkart_api.route("/v1/predict", methods=["POST"])
def predict_sales():

    try:

        # Get JSON request
        data = request.get_json()

        if not data:
            return jsonify({
                "error": "JSON request body is required."
            }), 400


        # Check required fields
        missing_columns = [
            column for column in MODEL_COLUMNS
            if column not in data
        ]

        if missing_columns:
            return jsonify({
                "error": f"Missing fields: {missing_columns}"
            }), 400


        # Create model input
        sample = {
            "Product_Weight": data["Product_Weight"],
            "Product_Sugar_Content": data["Product_Sugar_Content"],
            "Product_Allocated_Area": data["Product_Allocated_Area"],
            "Product_MRP": data["Product_MRP"],
            "Store_Size": data["Store_Size"],
            "Store_Location_City_Type": data["Store_Location_City_Type"],
            "Store_Type": data["Store_Type"],
            "Product_Id_char": data["Product_Id_char"],
            "Store_Age_Years": data["Store_Age_Years"],
            "Product_Type_Category": data["Product_Type_Category"]
        }


        # Convert to DataFrame
        input_data = pd.DataFrame([sample])


        # Ensure model column order
        input_data = input_data[MODEL_COLUMNS]


        # Make prediction
        prediction = model.predict(input_data)[0]


        # Return prediction
        return jsonify({
            "Predicted Sales": round(float(prediction), 2)
        })


    except Exception as ex:

        return jsonify({
            "error": str(ex)
        }), 500


# =====================================================
# Batch Prediction Endpoint
# =====================================================

@superkart_api.route("/v1/predictbatch", methods=["POST"])
def predict_batch():

    try:

        # Check CSV file
        if "file" not in request.files:
            return jsonify({
                "error": "CSV file is required."
            }), 400


        file = request.files["file"]


        if file.filename == "":
            return jsonify({
                "error": "No file selected."
            }), 400


        # Read CSV
        input_data = pd.read_csv(file)


        # Check required columns
        missing_columns = [
            column for column in MODEL_COLUMNS
            if column not in input_data.columns
        ]


        if missing_columns:
            return jsonify({
                "error": f"Missing columns: {missing_columns}"
            }), 400


        # Keep only required model columns
        # and maintain correct column order
        input_data = input_data[MODEL_COLUMNS]


        # Optional Product Sugar Content cleaning
        input_data["Product_Sugar_Content"] = (
            input_data["Product_Sugar_Content"]
            .replace({"reg": "Regular"})
        )


        # Make batch predictions
        predictions = model.predict(input_data)


        # Convert predictions to standard float
        predictions = [
            round(float(prediction), 2)
            for prediction in predictions
        ]


        # Prepare response
        result = []


        for index, prediction in enumerate(predictions):

            result.append({
                "Record_No": index + 1,
                "Predicted_Sales": prediction
            })


        # Return results
        return jsonify({
            "Total_Records": len(result),
            "Predictions": result
        })


    except Exception as ex:

        return jsonify({
            "error": str(ex)
        }), 500


# =====================================================
# Run Flask App
# =====================================================

if __name__ == "__main__":

    superkart_api.run(
        host="0.0.0.0",
        port=7860,
        debug=True
    )
