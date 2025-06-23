from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from .models import Event, Booking, Comment, User
from . import db
from datetime import datetime

main = Blueprint('main', __name__)

@main.route('/', methods=['GET'])
def index():
    if 'search-artist' in request.args or 'search-category' in request.args:
        artist = request.args.get('search-artist', "")
        category = request.args.get('search-category', "")

        if artist != "" and category == "":
            query_string = f"%{artist}%"
            events = Event.query.filter(Event.artist_name.like(query_string)).order_by(Event.id.desc()).all()
            return render_template('index.html', events=events)

        elif artist == "" and category != "":
            events = Event.query.filter_by(genre=category).order_by(Event.id.desc()).all()
            return render_template('index.html', events=events)

        elif artist != "" and category != "":
            query_string = f"%{artist}%"
            events = Event.query.filter(
                Event.artist_name.like(query_string)
            ).filter_by(genre=category).order_by(Event.id.desc()).all()
            return render_template('index.html', events=events)

    # Get all events for main display
    events = Event.query.order_by(Event.id.desc()).all()
    
    # Get newest events for featured section
    events_newest = Event.query.order_by(Event.id.desc()).limit(3).all()
    
    return render_template('index.html', events=events, events_newest=events_newest)


@main.route('/search')
def search():
    if request.args['search-artist'] != "" and request.args["search-category"] == "":
        query_string = f"%{request.args['search-artist']}%"
        events = Event.query.filter(Event.artist_name.like(query_string)).order_by(Event.id.desc()).all()
        return render_template('index.html', events=events)

    if request.args['search-artist'] == "" and request.args["search-category"] != "":
        events = Event.query.filter_by(genre=request.args["search-category"]).order_by(Event.id.desc()).all()
        return render_template('index.html', events=events)

    if request.args['search-artist'] != "" and request.args["search-category"] != "":
        query_string = f"%{request.args['search-artist']}%"
        events = Event.query.filter(
            Event.artist_name.like(query_string)
        ).filter_by(genre=request.args["search-category"]).order_by(Event.id.desc()).all()
        return render_template('index.html', events=events)

    return redirect(url_for('main.index'))


@main.route('/bookings')
@login_required
def bookings():
    # Get the current user's bookings
    user_bookings = Booking.query.filter_by(user_id=current_user.id).all()
    
    # Pass the bookings to the template
    return render_template('bookings.html', bookings=user_bookings)


@main.route('/profile')
@login_required
def profile():
    # Get the current user's details
    return render_template('profile.html', user=current_user)


@main.route('/update_profile', methods=['GET', 'POST'])
@login_required
def update_profile():
    if request.method == 'POST':
        # Get form data
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        address = request.form.get('address')
        
        # Update user information
        current_user.firstname = first_name
        current_user.lastname = last_name
        current_user.email = email
        current_user.phone = phone
        current_user.address = address
        
        # Commit changes to database
        db.session.commit()
        flash('Your profile has been updated successfully!', 'success')
        return redirect(url_for('main.profile'))
        
    # For GET request, show the form with current values
    return render_template('update_profile.html', user=current_user)


@main.route('/about')
def about():
    return render_template('about.html')


@main.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')
        flash('Thank you for your message! We will get back to you soon.', 'success')
        return redirect(url_for('main.contact'))
        
    return render_template('contact.html')