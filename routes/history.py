from flask import Blueprint, render_template
from flask_login import login_required

from models.paper import Paper

history = Blueprint("history", __name__)


@history.route("/history")
@login_required
def history_page():
    # Each database record represents one generated paper.
    # Keep the records separate so every row can download its own PDF.
    papers = Paper.query.order_by(Paper.id.desc()).all()

    return render_template("history.html", papers=papers)
