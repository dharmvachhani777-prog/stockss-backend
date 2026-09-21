import joblib
import pandas as pd

from flask import Flask, request, jsonify
from flask_cors import CORS


# =========================================================
# FLASK APP
# =========================================================

app = Flask(__name__)

# Allow Vercel frontend to access this backend
CORS(app)


import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_PATH = os.path.join(BASE_DIR, "model.pkl")
COLUMNS_PATH = os.path.join(BASE_DIR, "columns.pkl")

RAW_DATA_PATH = os.path.join(BASE_DIR, "data", "Nifty50_Raw.csv")
CLEAN_DATA_PATH = os.path.join(BASE_DIR, "data", "Nifty50_Cleaned.csv")


# =========================================================
# LOAD MODEL
# =========================================================

model = joblib.load(MODEL_PATH)

columns = joblib.load(COLUMNS_PATH)


# =========================================================
# NIFTY 50 COMPANIES
# =========================================================

companies = {

    "ADANIENT.NS": "Adani Enterprises",
    "ADANIPORTS.NS": "Adani Ports",
    "APOLLOHOSP.NS": "Apollo Hospitals",
    "ASIANPAINT.NS": "Asian Paints",
    "AXISBANK.NS": "Axis Bank",

    "BAJAJ-AUTO.NS": "Bajaj Auto",
    "BAJFINANCE.NS": "Bajaj Finance",
    "BAJAJFINSV.NS": "Bajaj Finserv",
    "BEL.NS": "Bharat Electronics",
    "BHARTIARTL.NS": "Bharti Airtel",

    "BPCL.NS": "Bharat Petroleum",
    "CIPLA.NS": "Cipla",
    "COALINDIA.NS": "Coal India",
    "DRREDDY.NS": "Dr. Reddy's Labs",
    "EICHERMOT.NS": "Eicher Motors",

    "GRASIM.NS": "Grasim Industries",
    "HCLTECH.NS": "HCL Technologies",
    "HDFCBANK.NS": "HDFC Bank",
    "HDFCLIFE.NS": "HDFC Life Insurance",
    "HEROMOTOCO.NS": "Hero MotoCorp",

    "HINDALCO.NS": "Hindalco Industries",
    "HINDUNILVR.NS": "Hindustan Unilever",
    "ICICIBANK.NS": "ICICI Bank",
    "INDUSINDBK.NS": "IndusInd Bank",
    "INFY.NS": "Infosys",

    "ITC.NS": "ITC Limited",
    "JIOFIN.NS": "Jio Financial Services",
    "JSWSTEEL.NS": "JSW Steel",
    "KOTAKBANK.NS": "Kotak Mahindra Bank",
    "LT.NS": "Larsen & Toubro",

    "M&M.NS": "Mahindra & Mahindra",
    "MARUTI.NS": "Maruti Suzuki",
    "NESTLEIND.NS": "Nestle India",
    "NTPC.NS": "NTPC Limited",
    "ONGC.NS": "ONGC",

    "POWERGRID.NS": "Power Grid Corp",
    "RELIANCE.NS": "Reliance Industries",
    "SBIN.NS": "State Bank of India",
    "SHRIRAMFIN.NS": "Shriram Finance",
    "SUNPHARMA.NS": "Sun Pharma",

    "TATACONSUM.NS": "Tata Consumer Products",
    "TATAMOTORS.NS": "Tata Motors",
    "TATASTEEL.NS": "Tata Steel",
    "TCS.NS": "Tata Consultancy Services",
    "TECHM.NS": "Tech Mahindra",

    "TITAN.NS": "Titan Company",
    "TRENT.NS": "Trent Limited",
    "ULTRACEMCO.NS": "UltraTech Cement",
    "WIPRO.NS": "Wipro"
}


# =========================================================
# HOME / API CHECK
# =========================================================

@app.route("/", methods=["GET"])
def home():

    return jsonify({
        "message": "NIFTY 50 Stock Prediction API is running",
        "status": "success"
    })


# =========================================================
# GET COMPANIES
# =========================================================

@app.route("/companies", methods=["GET"])
def get_companies():

    return jsonify(companies)


# =========================================================
# PREDICTION
# =========================================================

@app.route("/predict", methods=["POST"])
def predict():

    try:

        # -------------------------------------------------
        # GET JSON DATA FROM VERCEL
        # -------------------------------------------------

        data = request.get_json()

        if not data:
            return jsonify({
                "success": False,
                "message": "No data received"
            }), 400


        # -------------------------------------------------
        # GET FORM VALUES
        # -------------------------------------------------

        ticker = data.get("ticker")

        open_price = float(data.get("open"))
        high = float(data.get("high"))
        low = float(data.get("low"))
        close = float(data.get("close"))
        volume = float(data.get("volume"))


        # -------------------------------------------------
        # CHECK COMPANY
        # -------------------------------------------------

        if ticker not in companies:

            return jsonify({
                "success": False,
                "message": "Invalid NIFTY 50 company"
            }), 400


        # =================================================
        # CREATE INPUT DATAFRAME
        # =================================================

        input_data = pd.DataFrame(
            0,
            index=[0],
            columns=columns
        )


        # =================================================
        # PUT USER VALUES
        # =================================================

        input_data["Open"] = open_price

        input_data["High"] = high

        input_data["Low"] = low

        input_data["Close"] = close

        input_data["Volume"] = volume


        # =================================================
        # ONE-HOT ENCODE TICKER
        # =================================================

        ticker_column = "Ticker_" + ticker


        if ticker_column not in input_data.columns:

            return jsonify({
                "success": False,
                "message": "Selected ticker is not present in trained model"
            }), 400


        input_data[ticker_column] = 1


        # =================================================
        # MAKE PREDICTION
        # =================================================

        prediction = model.predict(input_data)


        # =================================================
        # GET FIVE PREDICTIONS
        # =================================================

        tomorrow_price = prediction[0][0]

        week_price = prediction[0][1]

        month_price = prediction[0][2]

        two_month_price = prediction[0][3]

        six_month_price = prediction[0][4]


        # =================================================
        # RETURN JSON TO VERCEL
        # =================================================

        return jsonify({

            "success": True,

            "company": companies[ticker],

            "ticker": ticker,

            "input": {
                "open": open_price,
                "high": high,
                "low": low,
                "close": close,
                "volume": volume
            },

            "prediction": {

                "tomorrow": round(
                    float(tomorrow_price), 2
                ),

                "one_week": round(
                    float(week_price), 2
                ),

                "one_month": round(
                    float(month_price), 2
                ),

                "two_month": round(
                    float(two_month_price), 2
                ),

                "six_month": round(
                    float(six_month_price), 2
                )
            }

        })


    # =====================================================
    # ERROR HANDLING
    # =====================================================

    except Exception as e:

        return jsonify({

            "success": False,

            "message": str(e)

        }), 500


# =========================================================
# EDA METRICS
# =========================================================

def get_eda_metrics():

    raw_df = pd.read_csv(
        RAW_DATA_PATH
    )

    clean_df = pd.read_csv(
        CLEAN_DATA_PATH
    )

    raw_records = len(raw_df)

    final_records = len(clean_df)

    rows_removed = (
        raw_records -
        final_records
    )

    if raw_records > 0:

        pct_removed = (
            rows_removed /
            raw_records
        ) * 100

    else:

        pct_removed = 0


    return {

        "raw_records": raw_records,

        "rows_removed": rows_removed,

        "pct_removed": f"{pct_removed:.2f}%",

        "final_records": final_records

    }


# =========================================================
# EDA API
# =========================================================

@app.route("/data-insights", methods=["GET"])
def data_insights():

    try:

        metrics = get_eda_metrics()

        return jsonify({

            "success": True,

            "data": metrics

        })


    except Exception as e:

        return jsonify({

            "success": False,

            "message": str(e)

        }), 500


# =========================================================
# MODEL INFORMATION
# =========================================================

@app.route("/model-info", methods=["GET"])
def model_info():

    return jsonify({

        "success": True,

        "model": "XGBoost",

        "prediction_periods": [

            "1 Day",

            "1 Week",

            "1 Month",

            "2 Months",

            "6 Months"

        ],

        "companies": len(companies)

    })


# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )