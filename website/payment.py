import os
import stripe
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

bp = Blueprint('payment', __name__, url_prefix='/payment')

@bp.route('/checkout/<int:booking_id>')
@login_required
def checkout(booking_id):
    from .models import Booking
    from . import db
    stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

    print("DEBUG: Stripe Secret Key =", stripe.api_key)  # Confirm it's set

    booking = Booking.query.get_or_404(booking_id)
    event = booking.event
    if not event:
        flash("Event not found.", "error")
        return redirect(url_for("main.index"))

    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'unit_amount': event.price * 100,
                    'product_data': {
                        'name': f"{event.event_name} Ticket",
                    },
                },
                'quantity': booking.num_tickets,
            }],
            mode='payment',
            success_url=url_for('payment.success', _external=True),
            cancel_url=url_for('event.show', id=event.id, _external=True),
        )
        return redirect(session.url, code=303)
    except Exception as e:
        flash(f"Error creating Stripe session: {str(e)}", "danger")
        return redirect(url_for("event.show", id=event.id))

@bp.route('/success')
def success():
    flash("Payment successful!", "success")
    return render_template("payment/success.html")
