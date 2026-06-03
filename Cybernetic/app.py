from flask import Flask, render_template, request
import pickle
import pandas as pd

app = Flask(__name__)

# Load model and columns
model = pickle.load(open("cyber_model.pkl", "rb"))
columns = pickle.load(open("columns.pkl", "rb"))

# 🔧 Function to safely handle empty inputs
def get_value(field):
    val = request.form.get(field)
    return float(val) if val and val.strip() != "" else 0.0


@app.route('/')
def home():
    return render_template("index.html")


@app.route('/predict', methods=['POST'])
def predict():
    try:
        # ✅ Get user inputs safely
        data = {
            "duration": get_value("duration"),
            "src_bytes": get_value("src_bytes"),
            "dst_bytes": get_value("dst_bytes"),
            "count": get_value("count"),
            "failed_logins": get_value("failed_logins")
        }

        # ✅ Convert protocol to numeric
        protocol_map = {"TCP": 0, "UDP": 1, "ICMP": 2}
        data["protocol_type"] = protocol_map.get(request.form.get("protocol_type"), 0)

        # ✅ Create full input with 116 features
        full_input = pd.DataFrame(columns=columns)
        full_input.loc[0] = 0  # fill all features with 0

        # ✅ Fill only selected features from UI
        for key in data:
            if key in full_input.columns:
                full_input.at[0, key] = data[key]

        # ✅ Prediction
        prediction = model.predict(full_input)[0]

        result = "⚠️ Attack Detected" if prediction == 1 else "✅ Normal Traffic"

        return render_template("index.html", prediction=result)

    except Exception as e:
        return f"Error: {str(e)}"


if __name__ == "__main__":
    app.run(debug=True)