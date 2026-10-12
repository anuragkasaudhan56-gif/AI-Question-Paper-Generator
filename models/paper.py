from models import db

class Paper(db.Model):
    __tablename__ = "papers"

    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(100), nullable=False)
    topic = db.Column(db.String(200), nullable=False)
    difficulty = db.Column(db.String(50), nullable=False)
    marks = db.Column(db.Integer, nullable=False)
    total_questions = db.Column(db.Integer, nullable=False)
    content = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f"<Paper {self.subject}>"