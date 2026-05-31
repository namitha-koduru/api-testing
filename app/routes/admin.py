from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from functools import wraps

from app.extensions import db
from app.models.user import User
from app.models.workshop import Workshop, WorkshopStatus
from app.models.meeting import Meeting, MeetingStatus
from app.models.registration import Registration
from app.models.payment import Payment, PaymentStatus

admin_bp = Blueprint("admin", __name__)


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash("Access denied. Admin privileges required.", "danger")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated


@admin_bp.route("/")
@login_required
@admin_required
def dashboard():
    total_users = User.query.count()
    total_workshops = Workshop.query.count()
    total_meetings = Meeting.query.count()
    total_registrations = Registration.query.count()
    total_revenue = db.session.query(db.func.sum(Payment.amount)).filter_by(
        status=PaymentStatus.PAID
    ).scalar() or 0

    recent_registrations = Registration.query.order_by(Registration.created_at.desc()).limit(10).all()
    recent_payments = Payment.query.order_by(Payment.created_at.desc()).limit(10).all()

    return render_template(
        "admin/dashboard.html",
        total_users=total_users,
        total_workshops=total_workshops,
        total_meetings=total_meetings,
        total_registrations=total_registrations,
        total_revenue=float(total_revenue),
        recent_registrations=recent_registrations,
        recent_payments=recent_payments,
    )


# ─── Workshops ───────────────────────────────────────────────────────────────

@admin_bp.route("/workshops")
@login_required
@admin_required
def workshops():
    items = Workshop.query.order_by(Workshop.created_at.desc()).all()
    return render_template("admin/workshops.html", workshops=items)


@admin_bp.route("/workshops/create", methods=["GET", "POST"])
@login_required
@admin_required
def create_workshop():
    if request.method == "POST":
        from datetime import datetime
        try:
            price = float(request.form.get("price", 0) or 0)
            workshop = Workshop(
                title=request.form["title"].strip(),
                description=request.form.get("description", "").strip(),
                instructor_name=request.form.get("instructor_name", "").strip() or None,
                instructor_bio=request.form.get("instructor_bio", "").strip() or None,
                venue=request.form.get("venue", "").strip() or None,
                start_time=datetime.fromisoformat(request.form["start_time"]),
                end_time=datetime.fromisoformat(request.form["end_time"]),
                capacity=int(request.form.get("capacity", 50)),
                price=price,
                is_free=price <= 0,
                tags=request.form.get("tags", "").strip() or None,
                status=WorkshopStatus.UPCOMING,
                created_by=current_user.id,
            )
            db.session.add(workshop)
            db.session.commit()
            flash("Workshop created successfully.", "success")
            return redirect(url_for("admin.workshops"))
        except Exception as e:
            flash(f"Error: {e}", "danger")
    return render_template("admin/workshop_form.html", workshop=None)


@admin_bp.route("/workshops/<int:workshop_id>/edit", methods=["GET", "POST"])
@login_required
@admin_required
def edit_workshop(workshop_id):
    workshop = Workshop.query.get_or_404(workshop_id)
    if request.method == "POST":
        from datetime import datetime
        try:
            price = float(request.form.get("price", 0) or 0)
            workshop.title = request.form["title"].strip()
            workshop.description = request.form.get("description", "").strip()
            workshop.instructor_name = request.form.get("instructor_name", "").strip() or None
            workshop.instructor_bio = request.form.get("instructor_bio", "").strip() or None
            workshop.venue = request.form.get("venue", "").strip() or None
            workshop.start_time = datetime.fromisoformat(request.form["start_time"])
            workshop.end_time = datetime.fromisoformat(request.form["end_time"])
            workshop.capacity = int(request.form.get("capacity", 50))
            workshop.price = price
            workshop.is_free = price <= 0
            workshop.tags = request.form.get("tags", "").strip() or None
            workshop.status = WorkshopStatus(request.form.get("status", "upcoming"))
            db.session.commit()
            flash("Workshop updated successfully.", "success")
            return redirect(url_for("admin.workshops"))
        except Exception as e:
            flash(f"Error: {e}", "danger")
    return render_template("admin/workshop_form.html", workshop=workshop)


@admin_bp.route("/workshops/<int:workshop_id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_workshop(workshop_id):
    workshop = Workshop.query.get_or_404(workshop_id)
    db.session.delete(workshop)
    db.session.commit()
    flash("Workshop deleted.", "success")
    return redirect(url_for("admin.workshops"))


# ─── Meetings ────────────────────────────────────────────────────────────────

@admin_bp.route("/meetings")
@login_required
@admin_required
def meetings():
    items = Meeting.query.order_by(Meeting.created_at.desc()).all()
    return render_template("admin/meetings.html", meetings=items)


@admin_bp.route("/meetings/create", methods=["GET", "POST"])
@login_required
@admin_required
def create_meeting():
    if request.method == "POST":
        from datetime import datetime
        try:
            price = float(request.form.get("price", 0) or 0)
            meeting = Meeting(
                title=request.form["title"].strip(),
                description=request.form.get("description", "").strip(),
                organizer_name=request.form.get("organizer_name", "").strip() or None,
                venue=request.form.get("venue", "").strip() or None,
                meeting_link=request.form.get("meeting_link", "").strip() or None,
                is_virtual=request.form.get("is_virtual") == "on",
                start_time=datetime.fromisoformat(request.form["start_time"]),
                end_time=datetime.fromisoformat(request.form["end_time"]),
                capacity=int(request.form.get("capacity", 100)),
                price=price,
                is_free=price <= 0,
                tags=request.form.get("tags", "").strip() or None,
                agenda=request.form.get("agenda", "").strip() or None,
                status=MeetingStatus.UPCOMING,
                created_by=current_user.id,
            )
            db.session.add(meeting)
            db.session.commit()
            flash("Meeting created successfully.", "success")
            return redirect(url_for("admin.meetings"))
        except Exception as e:
            flash(f"Error: {e}", "danger")
    return render_template("admin/meeting_form.html", meeting=None)


@admin_bp.route("/meetings/<int:meeting_id>/edit", methods=["GET", "POST"])
@login_required
@admin_required
def edit_meeting(meeting_id):
    meeting = Meeting.query.get_or_404(meeting_id)
    if request.method == "POST":
        from datetime import datetime
        try:
            price = float(request.form.get("price", 0) or 0)
            meeting.title = request.form["title"].strip()
            meeting.description = request.form.get("description", "").strip()
            meeting.organizer_name = request.form.get("organizer_name", "").strip() or None
            meeting.venue = request.form.get("venue", "").strip() or None
            meeting.meeting_link = request.form.get("meeting_link", "").strip() or None
            meeting.is_virtual = request.form.get("is_virtual") == "on"
            meeting.start_time = datetime.fromisoformat(request.form["start_time"])
            meeting.end_time = datetime.fromisoformat(request.form["end_time"])
            meeting.capacity = int(request.form.get("capacity", 100))
            meeting.price = price
            meeting.is_free = price <= 0
            meeting.tags = request.form.get("tags", "").strip() or None
            meeting.agenda = request.form.get("agenda", "").strip() or None
            meeting.status = MeetingStatus(request.form.get("status", "upcoming"))
            db.session.commit()
            flash("Meeting updated successfully.", "success")
            return redirect(url_for("admin.meetings"))
        except Exception as e:
            flash(f"Error: {e}", "danger")
    return render_template("admin/meeting_form.html", meeting=meeting)


@admin_bp.route("/meetings/<int:meeting_id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_meeting(meeting_id):
    meeting = Meeting.query.get_or_404(meeting_id)
    db.session.delete(meeting)
    db.session.commit()
    flash("Meeting deleted.", "success")
    return redirect(url_for("admin.meetings"))


# ─── Users ────────────────────────────────────────────────────────────────────

@admin_bp.route("/users")
@login_required
@admin_required
def users():
    items = User.query.order_by(User.created_at.desc()).all()
    return render_template("admin/users.html", users=items)


@admin_bp.route("/users/<int:user_id>/toggle", methods=["POST"])
@login_required
@admin_required
def toggle_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash("Cannot deactivate your own account.", "danger")
    else:
        user.is_active = not user.is_active
        db.session.commit()
        status = "activated" if user.is_active else "deactivated"
        flash(f"User {status}.", "success")
    return redirect(url_for("admin.users"))


# ─── Registrations ────────────────────────────────────────────────────────────

@admin_bp.route("/registrations")
@login_required
@admin_required
def registrations():
    items = Registration.query.order_by(Registration.created_at.desc()).all()
    return render_template("admin/registrations.html", registrations=items)


# ─── Payments ─────────────────────────────────────────────────────────────────

@admin_bp.route("/payments")
@login_required
@admin_required
def payments():
    items = Payment.query.order_by(Payment.created_at.desc()).all()
    return render_template("admin/payments.html", payments=items)
