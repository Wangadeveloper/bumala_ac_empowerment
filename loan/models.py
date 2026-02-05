from . import db
from flask_login import UserMixin

# ---------------- USER ----------------
class User(UserMixin, db.Model):
    __tablename__ = 'user_login'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False, unique=True)
    profile_completed = db.Column(db.Boolean, default=False)

    profile = db.relationship('UserProfile', back_populates='user', uselist=False)

    @property
    def full_names(self):
        return self.profile.full_names if self.profile else None

    @property
    def phone_no(self):
        return self.profile.phone_no if self.profile else None

    @property
    def country(self):
        return self.profile.country if self.profile else None

    @property
    def location(self):
        return self.profile.location if self.profile else None

    def __repr__(self):
        return f"<User {self.username}, email {self.email}>"

# ---------------- USER PROFILE ----------------
class UserProfile(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    
    # Personal Information
    full_names = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    phone_no = db.Column(db.String(20), nullable=False)
    country = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)

    # Financial / SACCO Info
    savings_category = db.Column(db.String(50), nullable=True)
    payment_level = db.Column(db.String(10), nullable=True)
    goals = db.Column(db.Text, nullable=True)

    # Foreign key to User
    user_id = db.Column(db.Integer, db.ForeignKey('user_login.id'), nullable=False, unique=True)
    user = db.relationship('User', back_populates='profile')

    def __repr__(self):
        return f"<UserProfile {self.full_names}>"

# ---------------- CONTRIBUTIONS ----------------
class Contribution(db.Model):
    __tablename__ = 'contributions'

    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Integer, nullable=False)
    transaction_code = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), default="Pending")
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    user_id = db.Column(db.Integer, db.ForeignKey('user_login.id'), nullable=False)

    def __repr__(self):
        return f"<Contribution {self.amount} - {self.status}>"

# ---------------- LOANS ----------------
class Loan(db.Model):
    __tablename__ = 'loans'

    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Integer, nullable=False)
    purpose = db.Column(db.String(200))
    status = db.Column(db.String(20), default="Pending")
    repaid_amount = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    user_id = db.Column(db.Integer, db.ForeignKey('user_login.id'), nullable=False)

    def __repr__(self):
        return f"<Loan {self.amount} - {self.status}>"

# ---------------- PEER TO PEER ADVICE ----------------
class PeerToPeerAdvice(db.Model):
    __tablename__ = 'peer_to_peer_advice'

    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user_login.id'), nullable=False)
    user = db.relationship('User')
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    def __repr__(self):
        return f"<Advice by user {self.user_id}>"
