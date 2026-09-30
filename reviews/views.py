from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Review, ReviewReply
from .forms import ReviewForm, ReviewReplyForm


@login_required
def review_list_view(request):
    reviews = Review.objects.filter(is_approved=True)
    return render(request, 'reviews/list.html', {'reviews': reviews})


@login_required
def review_create_view(request, booking_id):
    from bookings.models import Booking
    booking = get_object_or_404(Booking, booking_id=booking_id, passenger=request.user)
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.booking = booking
            review.bus = booking.schedule.bus
            review.agency = booking.schedule.bus.agency
            review.save()
            messages.success(request, 'Review submitted!')
            return redirect('reviews:review_list')
    else:
        form = ReviewForm()
    return render(request, 'reviews/create.html', {'form': form, 'booking': booking})


@login_required
def review_detail_view(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    replies = review.replies.all()
    if request.method == 'POST':
        form = ReviewReplyForm(request.POST)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.review = review
            reply.replied_by = request.user
            reply.save()
            messages.success(request, 'Reply added!')
            return redirect('reviews:review_detail', review_id=review.id)
    else:
        form = ReviewReplyForm()
    return render(request, 'reviews/detail.html', {'review': review, 'replies': replies, 'form': form})
