from datetime import date
import os
from grand_prix_classes import (
    BookingSystem, User, Admin, SingleRaceTicket, SeasonTicket,
    RaceCategory, OrderStatus, PaymentMethod
)


def main():
    """Main function to demonstrate the Grand Prix Experience Ticket Booking System"""
    # Create a booking system
    system = BookingSystem("Grand Prix Experience", "1.0")

    try:
        print("\n" + "=" * 80)
        print("GRAND PRIX EXPERIENCE TICKET BOOKING SYSTEM DEMO")
        print("=" * 80 + "\n")

        # 1. User Creation or Retrieval
        print("-" * 80)
        print("1. CREATING/RETRIEVING USERS")
        print("-" * 80)

        # Create or get a regular user
        username = "test_user"
        user = system.get_user(username)
        if user is None:
            user = system.create_user(
                "USR-TEST",
                username,
                "password123",
                "test@example.com",
                "555-1234"
            )
            print(f"Regular User Created: {user}")
        else:
            print(f"Regular User Retrieved: {user}")

        # Create or get an admin
        admin_username = "test_admin"
        admin = system.get_admin(admin_username)
        if admin is None:
            admin = system.create_admin(
                "ADM-TEST",
                admin_username,
                "admin123",
                "admin@example.com",
                2,  # Admin level
                "Operations",  # Department
                "555-5678"
            )
            print(f"Admin User Created: {admin}")
        else:
            print(f"Admin User Retrieved: {admin}")
        print()

        # 2. Ticket Creation
        print("-" * 80)
        print("2. CREATING/RETRIEVING TICKETS")
        print("-" * 80)

        # Create or get a single race ticket
        single_ticket_id = "TKT-TEST-1"
        single_ticket = system.get_ticket(single_ticket_id)
        if single_ticket is None:
            # Admin creates tickets
            single_ticket = admin.create_ticket(
                "SingleRace",
                single_ticket_id,
                200.0,
                date(2025, 6, 15),
                "Main Grandstand",
                race_name="Monaco Grand Prix",
                race_category=RaceCategory.PREMIUM
            )
            system.register_ticket(single_ticket)
            print(f"Single Race Ticket Created: {single_ticket}")
        else:
            print(f"Single Race Ticket Retrieved: {single_ticket}")

        print(f"Base Price: ${single_ticket.get_price():.2f}")
        print(f"Calculated Price: ${single_ticket.calculate_price():.2f}")
        print()

        # Create or get a season ticket
        season_ticket_id = "TKT-TEST-2"
        season_ticket = system.get_ticket(season_ticket_id)
        if season_ticket is None:
            # Create a season ticket
            season_ticket = admin.create_ticket(
                "Season",
                season_ticket_id,
                1000.0,
                date(2025, 1, 1),  # Season start date
                "VIP Lounge",
                season_year=2025,
                included_races=["Monaco", "Silverstone", "Monza", "Singapore", "Abu Dhabi"],
                race_dates=[
                    date(2025, 5, 25),  # Monaco
                    date(2025, 7, 7),  # Silverstone
                    date(2025, 9, 1),  # Monza
                    date(2025, 9, 21),  # Singapore
                    date(2025, 12, 1)  # Abu Dhabi
                ]
            )
            system.register_ticket(season_ticket)
            print(f"Season Ticket Created: {season_ticket}")
        else:
            print(f"Season Ticket Retrieved: {season_ticket}")

        print(f"Base Price: ${season_ticket.get_price():.2f}")
        print(f"Calculated Price (with discount): ${season_ticket.calculate_price():.2f}")
        print()

        # 3. Order Processing
        print("-" * 80)
        print("3. PROCESSING ORDERS")
        print("-" * 80)

        # Create a new order for this demo
        order = system.create_order(user)
        print(f"New Order Created: {order}")

        # Add tickets to the order
        order.add_ticket(single_ticket)
        print(f"Added Single Race Ticket to order.")
        print(f"Order Status: {order}")
        system.update_order(order)  # Save the updated order

        order.add_ticket(season_ticket)
        print(f"Added Season Ticket to order.")
        print(f"Order Status: {order}")
        system.update_order(order)  # Save the updated order
        print()

        # Process payment and confirm order
        print("Setting payment method to Credit Card...")
        order.set_payment_method(PaymentMethod.CREDIT_CARD)

        print("Attempting to confirm order...")
        if order.confirm_order():
            print(f"SUCCESS: Order confirmed!")
            print(f"Final Order Status: {order}")
            system.update_order(order)  # Save the confirmed order
        else:
            print("ERROR: Could not confirm order.")
        print()

        # Try to cancel the order
        print("Attempting to cancel confirmed order...")
        if order.cancel_order():
            print("SUCCESS: Order cancelled.")
            system.update_order(order)  # Save the cancelled order
        else:
            print("NOTICE: Could not cancel order (already confirmed).")
        print()

        # 4. System Status and Data Persistence
        print("-" * 80)
        print("4. SYSTEM STATUS AND DATA PERSISTENCE")
        print("-" * 80)

        # Check user's orders
        print(f"User {user.get_username()} has {len(user.get_orders())} orders in their history.")

        # Print the booking system status
        print(f"System Status: {system}")

        # Show that data is saved
        print("\nAll data has been saved to the following files:")
        print(f"- {os.path.join(system._data_dir, 'users.pkl')}")
        print(f"- {os.path.join(system._data_dir, 'admins.pkl')}")
        print(f"- {os.path.join(system._data_dir, 'tickets.pkl')}")
        print(f"- {os.path.join(system._data_dir, 'orders.pkl')}")
        print(f"- {system._log_file}")

        print("\nYou can restart the application and the data will be loaded from these files.")
        print("\n" + "=" * 80)
        print("DEMONSTRATION COMPLETED SUCCESSFULLY")
        print("=" * 80)

    except ValueError as e:
        print(f"\nERROR: {e}")
        print("\nDemonstration terminated due to an error.")


# Execute the main function if this script is run directly
if __name__ == "__main__":
    main()