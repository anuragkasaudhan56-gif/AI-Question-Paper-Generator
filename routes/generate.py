
from flask import Blueprint, render_template, request
from flask_login import login_required, current_user

from services.ai_service import generate_question_paper
from models import db
from models.paper import Paper


generate = Blueprint("generate", __name__)


@generate.route("/generate", methods=["GET", "POST"])
@login_required
def generate_page():

    if request.method == "POST":

        # ==================================================
        # COLLEGE DETAILS
        # ==================================================

        college = request.form.get(
            "college",
            ""
        ).strip()

        university = request.form.get(
            "university",
            ""
        ).strip()

        exam = request.form.get(
            "exam",
            ""
        ).strip()

        exam_date = request.form.get(
            "date",
            ""
        ).strip()

        exam_time = request.form.get(
            "time",
            ""
        ).strip()

        # ==================================================
        # QUESTION PAPER DETAILS
        # ==================================================

        subject = request.form.get(
            "subject",
            ""
        ).strip()

        # IMPORTANT:
        # This field can contain multiple topics.
        #
        # Example:
        #
        # Integration
        # Differentiation
        # Matrices
        # Probability
        #
        # OR:
        #
        # Integration, Differentiation, Matrices, Probability

        topic = request.form.get(
            "topic",
            ""
        ).strip()

        difficulty = request.form.get(
            "difficulty",
            "Medium"
        ).strip()

        # ==================================================
        # MARKS
        # ==================================================

        try:

            marks = int(
                request.form.get(
                    "marks",
                    100
                )
            )

        except (
            TypeError,
            ValueError
        ):

            marks = 100

        # ==================================================
        # NUMBER OF QUESTIONS
        # ==================================================

        try:

            questions = int(
                request.form.get(
                    "questions",
                    10
                )
            )

        except (
            TypeError,
            ValueError
        ):

            questions = 10

        # ==================================================
        # VALIDATION
        # ==================================================

        if not subject:

            return render_template(
                "generate.html",
                error="Please enter a subject."
            )

        if not topic:

            return render_template(
                "generate.html",
                error="Please enter at least one topic."
            )

        if marks <= 0:

            return render_template(
                "generate.html",
                error="Maximum marks must be greater than 0."
            )

        if questions <= 0:

            return render_template(
                "generate.html",
                error="Number of questions must be greater than 0."
            )

        # ==================================================
        # GENERATE QUESTION PAPER
        # ==================================================

        try:

            paper_text = generate_question_paper(

                college=college,

                university=university,

                exam=exam,

                exam_date=exam_date,

                exam_time=exam_time,

                subject=subject,

                topic=topic,

                difficulty=difficulty,

                marks=marks,

                questions=questions

            )

        except Exception as e:

            return render_template(
                "generate.html",
                error=f"Unable to generate question paper: {str(e)}"
            )

        # ==================================================
        # SAVE PAPER
        # ==================================================

        paper = Paper(

            subject=subject,

            topic=topic,

            difficulty=difficulty,

            marks=marks,

            total_questions=questions,

            content=paper_text

        )

        db.session.add(
            paper
        )

        db.session.commit()

        # ==================================================
        # SHOW RESULT
        # ==================================================

        return render_template(

            "result.html",

            paper=paper_text,

            subject=subject,

            topic=topic,

            paper_id=paper.id

        )

    # ======================================================
    # GET REQUEST
    # ======================================================

    return render_template(
        "generate.html"
    )

