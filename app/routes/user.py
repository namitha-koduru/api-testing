from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user

from app.models.workshop import Workshop, WorkshopStatus
from app.models.meeting import Meeting, MeetingStatus
from app.models.registration import Registration
from app.models.payment import Payment
from app.services.registration_service import RegistrationService
from app.services.auth_service import AuthService

user_bp = Blueprint("user", __name__)


def _user_only(f):
    """Decorator: redirect admins to admin panel."""
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if current_user.is_admin:
            return redirect(url_for("admin.dashboard"))
        return f(*args, **kwargs)
    return decorated


@user_bp.route("/")
@login_required
@_user_only
def dashboard():
    registrations = RegistrationService.get_user_registrations(current_user.id)
    upcoming = [r for r in registrations if r.event_start_time and r.status.value in ("pending", "confirmed")]
    payments = Payment.query.filter_by(user_id=current_user.id).order_by(Payment.created_at.desc()).limit(5).all()
    workshops = Workshop.query.filter_by(status=WorkshopStatus.UPCOMING).order_by(Workshop.start_time).limit(4).all()
    meetings = Meeting.query.filter_by(status=MeetingStatus.UPCOMING).order_by(Meeting.start_time).limit(4).all()
    return render_template(
        "user/dashboard.html",
        registrations=registrations,
        upcoming=upcoming,
        recent_payments=payments,
        workshops=workshops,
        meetings=meetings,
    )


@user_bp.route("/workshops")
@login_required
@_user_only
def workshops():
    q = request.args.get("q", "")
    query = Workshop.query
    if q:
        query = query.filter(Workshop.title.ilike(f"%{q}%"))
    items = query.order_by(Workshop.start_time).all()
    return render_template("user/workshops.html", workshops=items, q=q)


@user_bp.route("/workshops/<int:workshop_id>")
@login_required
@_user_only
def workshop_detail(workshop_id):
    workshop = Workshop.query.get_or_404(workshop_id)
    existing_reg = Registration.query.filter_by(
        user_id=current_user.id, workshop_id=workshop_id
    ).first()
    return render_template("user/workshop_detail.html", workshop=workshop, existing_reg=existing_reg)


@user_bp.route("/meetings")
@login_required
@_user_only
def meetings():
    q = request.args.get("q", "")
    query = Meeting.query
    if q:
        query = query.filter(Meeting.title.ilike(f"%{q}%"))
    items = query.order_by(Meeting.start_time).all()
    return render_template("user/meetings.html", meetings=items, q=q)


@user_bp.route("/meetings/<int:meeting_id>")
@login_required
@_user_only
def meeting_detail(meeting_id):
    meeting = Meeting.query.get_or_404(meeting_id)
    existing_reg = Registration.query.filter_by(
        user_id=current_user.id, meeting_id=meeting_id
    ).first()
    return render_template("user/meeting_detail.html", meeting=meeting, existing_reg=existing_reg)


@user_bp.route("/registrations")
@login_required
@_user_only
def registrations():
    regs = RegistrationService.get_user_registrations(current_user.id)
    return render_template("user/registrations.html", registrations=regs)


@user_bp.route("/payments")
@login_required
@_user_only
def payments():
    pays = Payment.query.filter_by(user_id=current_user.id).order_by(Payment.created_at.desc()).all()
    return render_template("user/payments.html", payments=pays)


@user_bp.route("/payment/success")
@login_required
@_user_only
def payment_success():
    registration_id = request.args.get("registration_id")
    reg = None
    if registration_id:
        reg = Registration.query.filter_by(id=registration_id, user_id=current_user.id).first()
    return render_template("user/payment_success.html", registration=reg)


@user_bp.route("/payment/failed")
@login_required
@_user_only
def payment_failed():
    return render_template("user/payment_failed.html")


@user_bp.route("/profile", methods=["GET", "POST"])
@login_required
@_user_only
def profile():
    if request.method == "POST":
        action = request.form.get("action")
        if action == "update_profile":
            data = {
                "first_name": request.form.get("first_name", "").strip(),
                "last_name": request.form.get("last_name", "").strip(),
                "phone": request.form.get("phone", "").strip(),
            }
            try:
                AuthService.update_profile(current_user, data)
                flash("Profile updated successfully.", "success")
            except Exception as e:
                flash(str(e), "danger")
        elif action == "change_password":
            try:
                AuthService.change_password(
                    current_user,
                    request.form.get("old_password", ""),
                    request.form.get("new_password", ""),
                )
                flash("Password changed successfully.", "success")
            except ValueError as e:
                flash(str(e), "danger")
        return redirect(url_for("user.profile"))
    return render_template("user/profile.html")
