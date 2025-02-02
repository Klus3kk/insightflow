from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS 
import datetime
from models import db, ABTest, ABTestGroup, ABTestResult

app = Flask(__name__)
CORS(app)

# PostgreSQL configuration
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://insightuser:cluesec@localhost/insightflow"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize the database
db.init_app(app)

# Create the database tables
with app.app_context():
    db.create_all()


# Database model for user events
class UserEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50), nullable=False)
    event_type = db.Column(db.String(50), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)


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

"""
A/B Tests routes
"""
@app.route("/create-ab-test", methods=["POST"])
def create_ab_test():
    """ Creates a new A/B test experiment. """
    data = request.json
    if not data or "name" not in data:
        return jsonify({"error": "Test name is required"}), 400
    
    new_test = ABTest(name=data["name"], description=data.get("description"))
    db.session.add(new_test)
    db.session.commit()
    
    return jsonify({"message": "A/B test created successfully!", "test_id": new_test.id}), 201

@app.route("/assign-user/<test_id>/<user_id>", methods=["POST"])
def assign_user(test_id, user_id):
    """ Randomly assigns a user to an A/B test group (A or B). """
    import random
    test = ABTest.query.get(test_id)
    if not test:
        return jsonify({"error": "Test not found"}), 404

    group = "A" if random.random() < 0.5 else "B"
    assignment = ABTestGroup(test_id=test_id, user_id=user_id, group=group)
    db.session.add(assignment)
    db.session.commit()

    return jsonify({"message": f"User {user_id} assigned to group {group}"}), 201

@app.route("/log-ab-test-result", methods=["POST"])
def log_ab_test_result():
    """ Logs the result of an A/B test interaction. """
    data = request.json
    if not data or "test_id" not in data or "user_id" not in data or "event_type" not in data:
        return jsonify({"error": "Missing fields"}), 400

    new_result = ABTestResult(
        test_id=data["test_id"],
        user_id=data["user_id"],
        event_type=data["event_type"],
    )
    db.session.add(new_result)
    db.session.commit()

    return jsonify({"message": "A/B test result logged!"}), 201

@app.route("/ab-test-results/<test_id>", methods=["GET"])
def get_ab_test_results(test_id):
    """ Retrieves A/B test results grouped by A/B group. """
    results = ABTestResult.query.filter_by(test_id=test_id).all()
    summary = {"A": 0, "B": 0}

    for result in results:
        user_group = ABTestGroup.query.filter_by(test_id=test_id, user_id=result.user_id).first()
        if user_group:
            summary[user_group.group] += 1

    return jsonify({"test_id": test_id, "group_A_results": summary["A"], "group_B_results": summary["B"]})

if __name__ == "__main__":
    app.run(debug=True)

