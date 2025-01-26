from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS 
import datetime

app = Flask(__name__)
CORS(app)

# PostgreSQL configuration
app.config["SQLALCHEMY_DATABASE_URI"] = ""
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize the database
db = SQLAlchemy(app)

# Database model for user events
class UserEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50), nullable=False)
    event_type = db.Column(db.String(50), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)

# Create the database tables
with app.app_context():
    db.create_all()

# Routes
@app.route("/")
def home():
    return "<h1>Welcome to InsightDrift!</h1>"

@app.route("/log-event", methods=["POST"])
def log_event():
    """
    Endpoint to log a user event.
    Expects JSON payload with 'user_id' and 'event_type'.
    """
    data = request.json
    if not data or not data.get("user_id") or not data.get("event_type"):
        return jsonify({"error": "Invalid data"}), 400

    # Create a new event record
    user_event = UserEvent(user_id=data["user_id"], event_type=data["event_type"])
    db.session.add(user_event)
    db.session.commit()

    return jsonify({"message": "Event logged successfully"}), 201

@app.route("/events", methods=["GET"])
def get_events():
    """
    Endpoint to retrieve logged events with filtering and pagination.
    Query Parameters:
    - user_id: Filter by user ID (optional)
    - event_type: Filter by event type (optional)
    - page: Page number for pagination (default: 1)
    - per_page: Number of events per page (default: 10)
    """
    user_id = request.args.get("user_id")
    event_type = request.args.get("event_type")
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 10))

    query = UserEvent.query

    if user_id:
        query = query.filter_by(user_id=user_id)
    if event_type:
        query = query.filter_by(event_type=event_type)

    events = query.paginate(page=page, per_page=per_page, error_out=False)

    results = [
        {
            "id": e.id,
            "user_id": e.user_id,
            "event_type": e.event_type,
            "timestamp": e.timestamp.isoformat(),
        }
        for e in events.items
    ]

    return jsonify({
        "total": events.total,
        "page": events.page,
        "per_page": events.per_page,
        "results": results
    }), 200

@app.route("/clear-events", methods=["DELETE"])
def clear_events():
    """
    Endpoint to delete all events.
    Use with caution!
    """
    try:
        num_deleted = db.session.query(UserEvent).delete()
        db.session.commit()
        return jsonify({"message": f"{num_deleted} events cleared"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500



if __name__ == "__main__":
    app.run(debug=True)
