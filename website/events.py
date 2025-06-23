from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file
from flask_login.utils import login_required, current_user
from werkzeug.utils import secure_filename
from . import db
from datetime import date, datetime
import os
import io
import qrcode
import base64

from .forms import CommentForm, EventForm, BookingForm, EventEditForm
from .models import Event, Comment, Booking
from .qr_utils import generate_qr_code_base64  # Add at the top with other imports

bp = Blueprint('event', __name__, url_prefix='/events')

EVENT_GENRES = ["Country", "Electronic", "Funk", "Hip Hop", "Jazz", "House", "Pop", "Rap", "Rock"]

@bp.route('/<int:id>')
def show(id):
    event = Event.query.filter_by(id=id).first()
    comment_form = CommentForm()
    booking_form = BookingForm()

    if event is None:
        flash(f"Could not find an event!", "warning")
        return redirect(url_for("main.index"))

    return render_template('events/show.html', comment_form=comment_form, booking_form=booking_form, 
        event=event, id=id, display_edit_button=login_user_is_creator(current_user, event.created_by))

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    event_form = EventForm()
    if event_form.validate_on_submit():
        event = Event(
            event_name=event_form.event_name.data,
            artist_name=event_form.artist_name.data,
            status=event_form.status.data,
            genre=event_form.genre.data,
            date=event_form.date.data,
            time=event_form.time.data,
            location=event_form.location.data,
            description=event_form.description.data,
            image=check_event_img_file(event_form),
            price=event_form.price.data,
            num_tickets=event_form.num_tickets.data,
            created_by=current_user.id
        )
        if event.num_tickets == 0:
            event.status = "Booked"

        db.session.add(event)
        db.session.commit()
        flash(f'Successfully created new event', 'success')
        return redirect(url_for('event.show', id=event.id))

    return render_template('events/create.html', form=event_form)

@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    event = Event.query.filter_by(id=id).first()
    if not login_user_is_creator(current_user, event.created_by):
        flash('You must be the creator of the event to edit the details!', 'warning')
        return redirect(url_for('event.show', id=event.id))
    
    event_edit_form = EventEditForm(obj=event)

    if event_edit_form.validate_on_submit():
        event.event_name = event_edit_form.event_name.data
        event.artist_name = event_edit_form.artist_name.data
        event.status = event_edit_form.status.data
        event.genre = event_edit_form.genre.data
        event.date = event_edit_form.date.data
        event.time = event_edit_form.time.data
        event.location = event_edit_form.location.data
        event.description = event_edit_form.description.data
        event.price = event_edit_form.price.data
        event.num_tickets = event_edit_form.num_tickets.data

        if event_edit_form.image.data and hasattr(event_edit_form.image.data, 'filename'):
            filename = event_edit_form.image.data.filename
            if filename:
                event.image = check_event_img_file(event_edit_form)

        db.session.commit()
        flash('Successfully updated event details', 'success')
        return redirect(url_for('event.show', id=event.id))

    return render_template('events/edit.html', form=event_edit_form, id=id, event=event)

@bp.route("/<int:id>/delete")
@login_required
def delete(id):
    event = Event.query.filter_by(id=id).first()
    if not login_user_is_creator(current_user, event.created_by):
        flash('You must be the creator of the event to delete it!', 'warning')
        return redirect(url_for('event.show', id=event.id))

    Event.query.filter_by(id=id).delete()
    db.session.commit()
    flash(f'Successfully deleted event', 'success')
    return redirect(url_for('main.index'))

@bp.route('/<int:id>/comment', methods=['GET', 'POST'])
@login_required
def comment(id):
    comment_form = CommentForm()
    if comment_form.validate_on_submit():
        comment = Comment(
            text=comment_form.text.data,
            user_id=current_user.id,
            event_id=id,
            posted_at=datetime.now()
        )
        db.session.add(comment)
        db.session.commit()
        flash("Comment posted successfully", "success")

    return redirect(url_for("event.show", id=id))

@bp.route('/my-bookings')
@login_required
def my_bookings():
    today = date.today()
    user_bookings = Booking.query.filter_by(user_id=current_user.id).all()
    
    current_bookings = []
    past_bookings = []

    for booking in user_bookings:
        if booking.event:
            if booking.event.date >= today:
                current_bookings.append(booking)
            else:
                past_bookings.append(booking)

    return render_template('events/booking.html', 
                          bookings=current_bookings, 
                          past_bookings=past_bookings)

@bp.route('/<int:booking_id>/ticket')
@login_required
def ticket_qr(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    if booking.user_id != current_user.id:
        flash("You are not authorized to view this ticket.", "danger")
        return redirect(url_for("main.index"))

    event = booking.event
    qr_data = f"Booking ID: {booking.id}\nEvent: {event.event_name}\nUser: {current_user.name}"
    qr_base64 = generate_qr_code_base64(qr_data)

    return render_template("events/qr_ticket.html", qr_code=qr_base64, booking=booking, event=event)

@bp.route('/<int:id>/booking', methods=['GET', 'POST'])
@login_required
def booking(id):
    event = Event.query.filter_by(id=id).first()
    if not event:
        flash("Event not found", "error")
        return redirect(url_for('main.index'))
        
    booking_form = BookingForm()

    if booking_form.validate_on_submit():
        ticket_order = booking_form.num_tickets.data

        if ticket_order <= 0:
            flash("Number of tickets must be greater than zero", "error")
            return redirect(url_for('event.show', id=id))
            
        if ticket_order > event.num_tickets:
            flash(f"Only {event.num_tickets} tickets left.", "error")
            return redirect(url_for('event.show', id=id))

        event.num_tickets -= ticket_order
        if event.num_tickets == 0:
            event.status = "Booked"

        booking = Booking(
            num_tickets=ticket_order,
            user_id=current_user.id,
            event_id=id,
            booking_date=datetime.now()
        )

        db.session.add(booking)
        db.session.commit()
        flash(f"{booking.num_tickets} tickets booked! Please proceed to payment.", 'success')
        return redirect(url_for('payment.checkout', booking_id=booking.id))


    elif request.method == "POST":
        comment_form = CommentForm()
        return render_template('events/show.html', 
            comment_form=comment_form, 
            booking_form=booking_form, 
            event=event, 
            id=id, 
            display_edit_button=login_user_is_creator(current_user, event.created_by),
            open_booking_modal=True)

    return redirect(url_for('event.show', id=id))


def check_event_img_file(form):
    fp = form.image.data
    filename = secure_filename(fp.filename)
    BASE_PATH = os.path.abspath(os.path.dirname(__file__))
    EVENT_IMG_PATH = os.path.join(BASE_PATH, 'static', 'img', 'events')

    os.makedirs(EVENT_IMG_PATH, exist_ok=True)
    upload_path = os.path.join(EVENT_IMG_PATH, filename)
    fp.save(upload_path)

    db_upload_path = f"img/events/{filename}"
    return db_upload_path

def login_user_is_creator(login_user, creator_id):
    try:
        return login_user.id == creator_id
    except:
        return False
