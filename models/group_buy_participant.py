from models import db
from datetime import datetime

class GroupBuyParticipant(db.Model):
    __tablename__ = 'group_buy_participants'

    id = db.Column(db.Integer, primary_key=True)
    group_buy_id = db.Column(db.Integer, db.ForeignKey('group_buys.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('_user.id'), nullable=False)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship
    group_buy = db.relationship("GroupBuy", backref="participants")
    user = db.relationship("User", backref="joined_group_buys")

    def get_participant_count(self):
        # Returns the number of users participating in this group buy using a database count.
        return len(self.participants)
