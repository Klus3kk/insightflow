from flask_sqlalchemy import SQLAlchemy
import datetime

db = SQLAlchemy()

# A/B Test Experiments
class ABTest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable = False)
    description = db.Column(db.Text, nullable = True)
    created_at = db.Column(db.DateTime, default = datetime.datetime.utcnow)

class ABTestGroup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    test_id = db.Column(db.Integer, db.ForeignKey("ab_test.id"), nullable=False)
    user_id = db.Column(db.String(50), nullable=False)
    group = db.Column(db.String(1), nullable=False)  # "A" or "B"
    assigned_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

class ABTestResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    test_id = db.Column(db.Integer, db.ForeignKey("ab_test.id"), nullable=False)
    user_id = db.Column(db.String(50), nullable=False)
    event_type = db.Column(db.String(50), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)