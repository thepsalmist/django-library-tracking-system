import logging
from celery import shared_task
from .models import Loan
from django.core.mail import send_mail,send_mass_mail
from django.conf import settings
from django.utils import timezone


logger = logging.getLogger(__name__)

@shared_task
def send_loan_notification(loan_id):
    try:
        loan = Loan.objects.get(id=loan_id)
        member_email = loan.member.user.email
        book_title = loan.book.title
        send_mail(
            subject='Book Loaned Successfully',
            message=f'Hello {loan.member.user.username},\n\nYou have successfully loaned "{book_title}".\nPlease return it by the due date.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[member_email],
            fail_silently=False,
        )
    except Loan.DoesNotExist:
        pass

@shared_task
def check_overdue_loans():
    today = timezone.now().date()
    overdue_loans = (
        Loan.objects.filter(is_returned=False, due_date__lt=today)
        .values(
            "due_date",
            "member__user__username",
            "member__user__email",
            "book__title"
            )
        )

    overdue_loans_subject = "Overdue Book Notification"
    messages = []
    for loan in overdue_loans.iterator():
        days_overdue = (today-loan["due_date"]).days
        user_email = loan["member__user__email"]
        message_body = (
            f"Hello {loan['member__user__username']}, \n\n"
            f"This is a reminder that the book {loan['book__title']} \n\n"
            f"is {days_overdue} overdue \n\n"
            f"Please return the book as soon as possible"
        )
        messages.append(
            (overdue_loans_subject,
             message_body,
             settings.DEFAULT_FROM_EMAIL,
             [user_email]
            )
        )
    if not messages:
        logger.info("No overdue loans")
        return 0
    try:
        send_mass_mail(
            messages, fail_silently=False
            )
        logger.info("Sent %d overdue loan notifications", len(messages))
        return len(messages)
    except Exception as e:
        logger.error("Error sending overdue loan notifications: %s", e)
        return 0
