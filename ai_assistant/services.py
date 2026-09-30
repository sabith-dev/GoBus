from django.conf import settings
import json


class AIService:
    @staticmethod
    def get_response(user_message, conversation_history=None):
        """Process user message and return AI response."""
        from .prompts import SYSTEM_PROMPT, FAQ_PROMPT

        message_lower = user_message.lower()

        # Simple keyword-based responses (can be replaced with actual AI API)
        if any(word in message_lower for word in ['hello', 'hi', 'hey']):
            return "Hello! Welcome to GoBus. How can I help you today?"

        if any(word in message_lower for word in ['search', 'find', 'bus', 'travel']):
            return "I'd be happy to help you search for buses! Please provide:\n- Source city\n- Destination city\n- Travel date\n\nOr you can use the search feature on our website."

        if any(word in message_lower for word in ['book', 'ticket', 'reserve']):
            return "To book a ticket:\n1. Search for your route\n2. Select a bus\n3. Choose your seats\n4. Enter passenger details\n5. Complete payment\n\nWould you like to start booking?"

        if any(word in message_lower for word in ['cancel', 'refund']):
            return "To cancel your booking:\n1. Go to My Bookings\n2. Select the booking\n3. Click Cancel\n\nRefund will be processed based on our cancellation policy."

        if any(word in message_lower for word in ['pay', 'payment', 'upi', 'card', 'wallet']):
            return "We accept multiple payment methods:\n- UPI (Google Pay, PhonePe, etc.)\n- Credit/Debit Cards\n- Net Banking\n- GoBus Wallet"

        if any(word in message_lower for word in ['wallet', 'balance', 'money']):
            return "You can check your wallet balance and add money from the Wallet section in your dashboard."

        if any(word in message_lower for word in ['referral', 'refer', 'friend']):
            return "Refer your friends to GoBus and earn rewards! Share your unique referral code from the Referral section in your dashboard."

        if any(word in message_lower for word in ['track', 'location', 'where']):
            return "You can track your bus in real-time from the Live Tracking section after booking."

        if any(word in message_lower for word in ['review', 'rating', 'feedback']):
            return "You can rate your journey and leave a review from the Reviews section after completing your trip."

        if any(word in message_lower for word in ['help', 'support', 'contact']):
            return "For support:\n- Email: support@gobus.com\n- Phone: 1800-XXX-XXXX\n- Or use this chat for quick help"

        if any(word in message_lower for word in ['thank', 'thanks']):
            return "You're welcome! Is there anything else I can help you with?"

        if any(word in message_lower for word in ['bye', 'goodbye']):
            return "Thank you for using GoBus! Have a safe journey! 🚌"

        return "I'm here to help! You can ask me about:\n- Searching for buses\n- Booking tickets\n- Cancellations\n- Payments\n- Wallet\n- Referrals\n- Live tracking\n\nWhat would you like to know?"

    @staticmethod
    def search_buses(source, destination, date):
        """Search for available buses."""
        from schedules.models import Schedule
        from datetime import datetime

        schedules = Schedule.objects.filter(
            route__origin__icontains=source,
            route__destination__icontains=destination,
            is_active=True
        )

        results = []
        for schedule in schedules:
            results.append({
                'bus_name': schedule.bus.bus_name,
                'bus_number': schedule.bus.bus_number,
                'departure': str(schedule.departure_time),
                'arrival': str(schedule.arrival_time),
                'fare': str(schedule.fare),
                'bus_type': schedule.bus.bus_type.name,
                'available_seats': schedule.bus.total_seats,
            })

        return results
