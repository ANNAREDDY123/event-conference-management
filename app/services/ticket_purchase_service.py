from fastapi import HTTPException, status

from app.models.notification import Notification, NotificationType
from app.models.ticket import TicketStatus
from app.models.ticket_purchase import (
    PaymentStatus,
    PurchaseStatus,
    TicketPurchase,
)
from app.repositories.ticket_purchase_repository import (
    TicketPurchaseRepository,
)
from app.schemas.ticket_purchase import (
    PaymentUpdate,
    TicketPurchaseCreate,
)


class TicketPurchaseService:

    def __init__(self, db):
        self.repository = TicketPurchaseRepository(db)

    # ============================================================
    # CREATE PURCHASE
    # ============================================================

    def create_purchase(
        self,
        purchase_data: TicketPurchaseCreate,
    ) -> TicketPurchase:

        ticket = self.repository.get_ticket(
            purchase_data.ticket_id
        )

        if not ticket:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ticket not found",
            )

        attendee = self.repository.get_attendee(
            purchase_data.attendee_id
        )

        if not attendee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Attendee not found",
            )

        event = self.repository.get_event(
            attendee.event_id
        )

        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Event not found",
            )

        if ticket.event_id != attendee.event_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ticket does not belong to attendee's event",
            )

        if ticket.status != TicketStatus.AVAILABLE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ticket is not available",
            )

        if purchase_data.quantity > ticket.available_quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Insufficient ticket quantity available",
            )

        total_amount = (
            ticket.price * purchase_data.quantity
        )

        purchase = TicketPurchase(
            ticket_id=ticket.id,
            attendee_id=attendee.id,
            quantity=purchase_data.quantity,
            total_amount=total_amount,
            payment_status=PaymentStatus.PENDING,
            purchase_status=PurchaseStatus.CONFIRMED,
        )

        ticket.available_quantity -= (
            purchase_data.quantity
        )

        if ticket.available_quantity == 0:
            ticket.status = TicketStatus.SOLD_OUT

        purchase = self.repository.create(
            purchase
        )

        # Purchase notification
        user = self.repository.get_user(
            attendee.user_id
        )

        if user:
            notification = Notification(
                user_id=user.id,
                title="Ticket Purchase Successful",
                message=(
                    f"Your ticket purchase for "
                    f"'{event.event_name}' was successful. "
                    f"Quantity: {purchase_data.quantity} "
                    f"ticket(s). "
                    f"Amount: {total_amount:.2f}."
                ),
                notification_type=NotificationType.TICKET_PURCHASE,
            )

            self.repository.create_notification(
                notification
            )

        return purchase

    # ============================================================
    # GET PURCHASE
    # ============================================================

    def get_purchase(
        self,
        purchase_id: int,
    ) -> TicketPurchase:

        purchase = self.repository.get_by_id(
            purchase_id
        )

        if not purchase:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ticket purchase not found",
            )

        return purchase

    # ============================================================
    # GET ALL PURCHASES
    # ============================================================

    def get_all_purchases(
        self,
    ) -> list[TicketPurchase]:

        return self.repository.get_all()

    # ============================================================
    # GET PURCHASES BY ATTENDEE
    # ============================================================

    def get_purchases_by_attendee(
        self,
        attendee_id: int,
    ) -> list[TicketPurchase]:

        attendee = self.repository.get_attendee(
            attendee_id
        )

        if not attendee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Attendee not found",
            )

        return self.repository.get_by_attendee(
            attendee_id
        )

    # ============================================================
    # GET PURCHASES BY TICKET
    # ============================================================

    def get_purchases_by_ticket(
        self,
        ticket_id: int,
    ) -> list[TicketPurchase]:

        ticket = self.repository.get_ticket(
            ticket_id
        )

        if not ticket:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ticket not found",
            )

        return self.repository.get_by_ticket(
            ticket_id
        )

    # ============================================================
    # UPDATE PAYMENT
    # ============================================================

    def update_payment(
        self,
        purchase_id: int,
        payment_data: PaymentUpdate,
    ) -> TicketPurchase:

        purchase = self.get_purchase(
            purchase_id
        )

        # A refunded purchase cannot receive another payment update.
        if purchase.payment_status == PaymentStatus.REFUNDED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Use the refund endpoint to process a refund",
            )

        # A successful payment cannot be completed again.
        if purchase.payment_status == PaymentStatus.SUCCESS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Payment has already been completed",
            )

        attendee = self.repository.get_attendee(
            purchase.attendee_id
        )

        if not attendee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Attendee not found",
            )

        purchase.payment_status = (
            payment_data.payment_status
        )

        if payment_data.payment_status == PaymentStatus.SUCCESS:

            purchase.payment_reference = (
                f"PAY-{purchase.id:06d}"
            )

            notification = Notification(
                user_id=attendee.user_id,
                title="Payment Successful",
                message=(
                    f"Payment for ticket purchase "
                    f"#{purchase.id} was successful. "
                    f"Amount: "
                    f"{purchase.total_amount:.2f}."
                ),
                notification_type=NotificationType.PAYMENT,
            )

            self.repository.create_notification(
                notification
            )

        elif payment_data.payment_status == PaymentStatus.FAILED:

            purchase.purchase_status = (
                PurchaseStatus.CANCELLED
            )

            ticket = self.repository.get_ticket(
                purchase.ticket_id
            )

            if ticket:
                ticket.available_quantity += (
                    purchase.quantity
                )

                if ticket.available_quantity > 0:
                    ticket.status = TicketStatus.AVAILABLE

            notification = Notification(
                user_id=attendee.user_id,
                title="Payment Failed",
                message=(
                    f"Payment for ticket purchase "
                    f"#{purchase.id} failed. "
                    f"Amount: "
                    f"{purchase.total_amount:.2f}."
                ),
                notification_type=NotificationType.PAYMENT,
            )

            self.repository.create_notification(
                notification
            )

        return self.repository.update(
            purchase
        )

    # ============================================================
    # REFUND PURCHASE
    # ============================================================

    def refund_purchase(
        self,
        purchase_id: int,
    ) -> TicketPurchase:

        purchase = self.get_purchase(
            purchase_id
        )

        # Only successfully paid purchases can be refunded.
        if purchase.payment_status != PaymentStatus.SUCCESS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only successfully paid purchases can be refunded",
            )

        ticket = self.repository.get_ticket(
            purchase.ticket_id
        )

        if not ticket:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ticket not found",
            )

        attendee = self.repository.get_attendee(
            purchase.attendee_id
        )

        if not attendee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Attendee not found",
            )

        event = self.repository.get_event(
            attendee.event_id
        )

        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Event not found",
            )

        ticket.available_quantity += (
            purchase.quantity
        )

        if ticket.available_quantity > 0:
            ticket.status = TicketStatus.AVAILABLE

        purchase.payment_status = (
            PaymentStatus.REFUNDED
        )

        purchase.purchase_status = (
            PurchaseStatus.CANCELLED
        )

        notification = Notification(
            user_id=attendee.user_id,
            title="Ticket Purchase Refunded",
            message=(
                f"Your payment for ticket purchase "
                f"#{purchase.id} for "
                f"'{event.event_name}' has been "
                f"refunded successfully. "
                f"Refund amount: "
                f"{purchase.total_amount:.2f}."
            ),
            notification_type=NotificationType.REFUND,
        )

        self.repository.create_notification(
            notification
        )

        return self.repository.update(
            purchase
        )