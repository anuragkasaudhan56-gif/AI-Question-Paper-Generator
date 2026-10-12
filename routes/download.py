from flask import Blueprint, send_file, abort, redirect, url_for
from flask_login import login_required

from models.paper import Paper
from services.pdf_service import create_pdf


download = Blueprint("download", __name__)


@download.route("/download")
@login_required
def download_latest_pdf():
    """Backward-compatible route: download the most recently generated paper."""
    paper = Paper.query.order_by(Paper.id.desc()).first()

    if not paper:
        abort(404, description="No question paper has been generated yet.")

    return _send_paper_pdf(paper)


@download.route("/download/<int:paper_id>")
@login_required
def download_pdf(paper_id):
    """Download the exact question paper selected by its database ID."""
    paper = Paper.query.get_or_404(paper_id)
    return _send_paper_pdf(paper)


def _send_paper_pdf(paper):
    # Use a unique filename for every paper so one PDF cannot overwrite another.
    safe_subject = "".join(
        char if char.isalnum() else "_"
        for char in paper.subject.strip()
    ).strip("_") or "Question_Paper"

    filename = f"question_paper_{paper.id}_{safe_subject}.pdf"
    filepath = create_pdf(paper.content, filename=filename)

    return send_file(
        filepath,
        as_attachment=True,
        download_name=filename,
        mimetype="application/pdf"
    )
