from flask import Flask
from flask_cors import CORS
from config import SECRET_KEY
from routes.auth import auth_bp
from routes.products import products_bp
from routes.categories import categories_bp
from routes.warehouses import warehouses_bp
from routes.stock import stock_bp
from routes.receipts import receipts_bp
from routes.deliveries import deliveries_bp
from routes.transfers import transfers_bp
from routes.adjustments import adjustments_bp
from routes.dashboard import dashboard_bp
from routes.ledger import ledger_bp

app = Flask(__name__)

app.config["SECRET_KEY"] = SECRET_KEY

CORS(app)

app.register_blueprint(auth_bp)
app.register_blueprint(products_bp)
app.register_blueprint(categories_bp)
app.register_blueprint(warehouses_bp)
app.register_blueprint(stock_bp)
app.register_blueprint(receipts_bp)
app.register_blueprint(deliveries_bp)
app.register_blueprint(transfers_bp)
app.register_blueprint(adjustments_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(ledger_bp)

@app.route("/")
def home():
    return {"message": "StockSense API is running"}


@app.route("/api/health")
def health():
    return {
        "status": "success",
        "message": "StockSense backend is connected"
    }


if __name__ == "__main__":
    app.run(debug=True)