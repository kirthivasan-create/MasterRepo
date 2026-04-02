from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/")
def home():
    return "home"

@app.route("/offer-checker", methods=["POST"])
def offer_checker():
    data = request.get_json()
    active_offers = data.get("active_offers", [])
    recommended_offers = data.get("recommended_offers", [])
    result = compare_offers(active_offers, recommended_offers)
    return jsonify(result)

def compare_offers(active_offers, recommended_offers):
    # Example logic: find matching offers by ID (adjust as needed)
    matches = []
    for rec in recommended_offers:
        for act in active_offers:
            if rec.get("id") == act.get("id"):
                matches.append(rec)
    return {"matches": matches}

if __name__ == "__main__":
    app.run(debug=True)