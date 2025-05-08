import os
import pickle
from abc import ABC, abstractmethod
from datetime import date, datetime
from enum import Enum
from typing import List, Optional


# Enum Types - These are specialized constants with string representations
# They provide type safety and better semantics than using strings directly
class RaceCategory(Enum):
    # Different race categories with pricing implications
    PREMIUM = "Premium"    # Premium races cost more
    STANDARD = "Standard"  # Standard races at regular price
    ECONOMY = "Economy"    # Economy races cost less


class OrderStatus(Enum):
    # Possible states for an order in the system
    PENDING = "Pending"      # Order created but not confirmed
    CONFIRMED = "Confirmed"  # Order has been confirmed and paid for
    CANCELLED = "Cancelled"  # Order has been cancelled


class PaymentMethod(Enum):
    # Payment methods accepted by the system
    CREDIT_CARD = "Credit Card"
    DEBIT_CARD = "Debit Card"
    DIGITAL_WALLET = "Digital Wallet"


# Abstract base class for tickets - defines the common interface for all ticket types
# Cannot be instantiated directly - must be extended by concrete ticket classes
class Ticket(ABC):
    def __init__(self, ticket_id: str, price: float, event_date: date, venue_section: str):
        # Private attributes with name mangling using double underscores
        self.__ticket_id = ticket_id          # Unique identifier for the ticket
        self.__price = price                  # Base price before any adjustments
        self.__event_date = event_date        # Date of the event
        self.__venue_section = venue_section  # Section of the venue (e.g., "Main Grandstand")
        self.__is_used = False                # Whether the ticket has been used
        self.__created_by = None              # Admin who created this ticket

    # Getter and setter methods to access private attributes (encapsulation)
    def get_ticket_id(self) -> str:
        return self.__ticket_id

    def set_ticket_id(self, ticket_id: str) -> None:
        self.__ticket_id = ticket_id

    def get_price(self) -> float:
        return self.__price

    def set_price(self, price: float) -> None:
        # Data validation - price cannot be negative
        if price < 0:
            raise ValueError("Price cannot be negative")
        self.__price = price

    def get_event_date(self) -> date:
        return self.__event_date

    def set_event_date(self, event_date: date) -> None:
        self.__event_date = event_date

    def get_venue_section(self) -> str:
        return self.__venue_section

    def set_venue_section(self, venue_section: str) -> None:
        self.__venue_section = venue_section

    def is_used(self) -> bool:
        return self.__is_used

    def set_used(self, is_used: bool) -> None:
        self.__is_used = is_used

    def get_created_by(self):
        return self.__created_by

    def set_created_by(self, admin) -> None:
        self.__created_by = admin

    # Abstract method that must be implemented by all subclasses
    # This is an example of the Template Method pattern
    @abstractmethod
    def calculate_price(self) -> float:
        """Calculate the final price of the ticket, must be implemented by subclasses"""
        pass

    # String representation of the ticket for user-friendly display
    def __str__(self) -> str:
        return f"Ticket ID: {self.__ticket_id}, Price: ${self.__price}, Date: {self.__event_date}, Section: {self.__venue_section}"


# Concrete implementation of Ticket for single race events
class SingleRaceTicket(Ticket):
    def __init__(self, ticket_id: str, price: float, event_date: date, venue_section: str,
                 race_name: str, race_category: RaceCategory):
        # Call the parent constructor first
        super().__init__(ticket_id, price, event_date, venue_section)
        # Additional attributes specific to single race tickets
        self.__race_name = race_name            # Name of the race (e.g., "Monaco Grand Prix")
        self.__race_category = race_category    # Category of the race (affects pricing)

    # Getters and setters for SingleRaceTicket specific attributes
    def get_race_name(self) -> str:
        return self.__race_name

    def set_race_name(self, race_name: str) -> None:
        self.__race_name = race_name

    def get_race_category(self) -> RaceCategory:
        return self.__race_category

    def set_race_category(self, race_category: RaceCategory) -> None:
        self.__race_category = race_category

    # Implementation of the abstract method for calculating price
    # Different logic based on race category
    def calculate_price(self) -> float:
        """Calculate final price based on race category"""
        base_price = self.get_price()
        if self.__race_category == RaceCategory.PREMIUM:
            return base_price * 1.2  # 20% premium for premium races
        elif self.__race_category == RaceCategory.STANDARD:
            return base_price        # Standard price for standard races
        else:  # ECONOMY
            return base_price * 0.9  # 10% discount for economy races

    # Override the string representation to include race-specific info
    def __str__(self) -> str:
        return f"{super().__str__()}, Race: {self.__race_name}, Category: {self.__race_category.value}"


# Another concrete implementation of Ticket for season passes
class SeasonTicket(Ticket):
    def __init__(self, ticket_id: str, price: float, event_date: date, venue_section: str,
                 season_year: int, included_races: List[str], race_dates: List[date] = None):
        # For SeasonTicket, event_date represents season start date
        super().__init__(ticket_id, price, event_date, venue_section)
        # Additional attributes specific to season tickets
        self.__season_year = season_year        # Year of the season (e.g., 2023)
        self.__included_races = included_races  # List of races included in this season ticket
        self.__race_dates = race_dates if race_dates else []  # Optional dates for races

    # Getters and setters for SeasonTicket specific attributes
    def get_season_year(self) -> int:
        return self.__season_year

    def set_season_year(self, season_year: int) -> None:
        self.__season_year = season_year

    def get_included_races(self) -> List[str]:
        return self.__included_races

    def set_included_races(self, included_races: List[str]) -> None:
        self.__included_races = included_races

    def get_race_dates(self) -> List[date]:
        return self.__race_dates

    def set_race_dates(self, race_dates: List[date]) -> None:
        self.__race_dates = race_dates

    # Implementation of the abstract method for calculating price
    # Different logic based on number of included races
    def calculate_price(self) -> float:
        """Calculate final price based on number of included races"""
        base_price = self.get_price()
        num_races = len(self.__included_races)

        # Discount tiers based on number of races
        if num_races >= 15:
            return base_price * 0.7  # 30% discount for 15+ races
        elif num_races >= 10:
            return base_price * 0.8  # 20% discount for 10-14 races
        elif num_races >= 5:
            return base_price * 0.9  # 10% discount for 5-9 races
        else:
            return base_price  # No discount for less than 5 races

    # Override the string representation to include season-specific info
    def __str__(self) -> str:
        races_str = ", ".join(self.__included_races) if self.__included_races else "None"
        return f"{super().__str__()}, Year: {self.__season_year}, Races: {races_str}"


# Base User class - represents a regular user of the system
class User:
    def __init__(self, user_id: str, username: str, password: str, email: str, phone_number: str = None):
        # Private attributes with name mangling
        self.__user_id = user_id                # Unique identifier for the user
        self.__username = username              # Username for login
        self.__password = password              # Password (would be hashed in a real system)
        self.__email = email                    # Email address
        self.__phone_number = phone_number      # Optional phone number
        self.__orders = []                      # List of orders placed by this user

    # Getters and setters for User attributes
    def get_user_id(self) -> str:
        return self.__user_id

    def set_user_id(self, user_id: str) -> None:
        self.__user_id = user_id

    def get_username(self) -> str:
        return self.__username

    def set_username(self, username: str) -> None:
        self.__username = username

    def get_password(self) -> str:
        return self.__password

    def set_password(self, password: str) -> None:
        # Data validation - password must be at least 6 characters
        if len(password) < 6:
            raise ValueError("Password must be at least 6 characters long")
        self.__password = password

    def get_email(self) -> str:
        return self.__email

    def set_email(self, email: str) -> None:
        # Data validation - email must contain @
        if '@' not in email:
            raise ValueError("Invalid email format")
        self.__email = email

    def get_phone_number(self) -> Optional[str]:
        return self.__phone_number

    def set_phone_number(self, phone_number: str) -> None:
        self.__phone_number = phone_number

    def get_orders(self) -> List:
        return self.__orders

    # Add an order to this user's history - part of bidirectional relationship
    def add_order(self, order) -> None:
        self.__orders.append(order)

    # Check if provided password matches stored password
    def verify_password(self, password: str) -> bool:
        return self.__password == password

    # String representation of the user
    def __str__(self) -> str:
        return f"User: {self.__username} ({self.__email})"


# Admin class extends User with additional capabilities
# Example of inheritance - Admin is a specialized type of User
class Admin(User):
    def __init__(self, user_id: str, username: str, password: str, email: str,
                 admin_level: int, department: str, phone_number: str = None):
        # Call the parent constructor first
        super().__init__(user_id, username, password, email, phone_number)
        # Additional attributes specific to admins
        self.__admin_level = admin_level    # Level of administrative access (1-3)
        self.__department = department      # Department the admin belongs to

    # Getters and setters for Admin specific attributes
    def get_admin_level(self) -> int:
        return self.__admin_level

    def set_admin_level(self, admin_level: int) -> None:
        # Data validation - admin level must be between 1 and 3
        if admin_level < 1 or admin_level > 3:
            raise ValueError("Admin level must be between 1 and 3")
        self.__admin_level = admin_level

    def get_department(self) -> str:
        return self.__department

    def set_department(self, department: str) -> None:
        self.__department = department

    # Factory method to create different types of tickets
    def create_ticket(self, ticket_type: str, ticket_id: str, price: float, event_date: date,
                      venue_section: str, **kwargs) -> Ticket:
        """Create a new ticket of the specified type"""
        ticket = None

        # Create appropriate ticket type based on ticket_type parameter
        if ticket_type == "SingleRace":
            # Get required parameters for SingleRaceTicket
            race_name = kwargs.get('race_name', '')
            if not race_name:
                raise ValueError("Race name is required for SingleRaceTicket")

            race_category = kwargs.get('race_category', RaceCategory.STANDARD)
            # Create the SingleRaceTicket
            ticket = SingleRaceTicket(ticket_id, price, event_date, venue_section, race_name, race_category)

        elif ticket_type == "Season":
            # Get parameters for SeasonTicket with defaults
            season_year = kwargs.get('season_year', event_date.year)
            included_races = kwargs.get('included_races', [])
            race_dates = kwargs.get('race_dates', [])

            # Create the SeasonTicket
            ticket = SeasonTicket(ticket_id, price, event_date, venue_section,
                                  season_year, included_races, race_dates)
        else:
            # Invalid ticket type
            raise ValueError(f"Invalid ticket type: {ticket_type}")

        # Set the admin as creator of this ticket
        ticket.set_created_by(self)

        return ticket

    # Override string representation to include admin-specific info
    def __str__(self) -> str:
        return f"Admin: {self.get_username()}, Level: {self.__admin_level}, Department: {self.__department}"


# Order class - represents an order in the booking system
class Order:
    def __init__(self, order_id: str, order_date: date, status: OrderStatus = OrderStatus.PENDING,
                 total_amount: float = 0.0, payment_method: PaymentMethod = None):
        # Private attributes
        self.__order_id = order_id              # Unique identifier for the order
        self.__order_date = order_date          # Date the order was created
        self.__status = status                  # Current status of the order
        self.__total_amount = total_amount      # Total amount to be paid
        self.__payment_method = payment_method  # Method of payment
        self.__tickets = []                     # Tickets included in this order
        self.__user_id = None                   # ID of the user who placed this order

    # Getters and setters for Order attributes
    def get_order_id(self) -> str:
        return self.__order_id

    def set_order_id(self, order_id: str) -> None:
        self.__order_id = order_id

    def get_order_date(self) -> date:
        return self.__order_date

    def set_order_date(self, order_date: date) -> None:
        self.__order_date = order_date

    def get_status(self) -> OrderStatus:
        return self.__status

    def set_status(self, status: OrderStatus) -> None:
        self.__status = status

    def get_total_amount(self) -> float:
        return self.__total_amount

    def set_total_amount(self, total_amount: float) -> None:
        # Data validation - total amount cannot be negative
        if total_amount < 0:
            raise ValueError("Total amount cannot be negative")
        self.__total_amount = total_amount

    def get_payment_method(self) -> Optional[PaymentMethod]:
        return self.__payment_method

    def set_payment_method(self, payment_method: PaymentMethod) -> None:
        self.__payment_method = payment_method

    def get_user_id(self) -> str:
        return self.__user_id

    def set_user_id(self, user_id: str) -> None:
        self.__user_id = user_id

    # Methods to manage tickets in the order
    def add_ticket(self, ticket: Ticket) -> None:
        """Add a ticket to the order"""
        # Cannot add tickets to a confirmed order
        if self.__status == OrderStatus.CONFIRMED:
            raise ValueError("Cannot add tickets to a confirmed order")

        # Add the ticket and update the total amount
        self.__tickets.append(ticket)
        self.__total_amount = self.calculate_total()

    def remove_ticket(self, ticket_id: str) -> bool:
        """Remove a ticket from the order"""
        # Cannot remove tickets from a confirmed order
        if self.__status == OrderStatus.CONFIRMED:
            return False

        # Find and remove the ticket with the matching ID
        for i, ticket in enumerate(self.__tickets):
            if ticket.get_ticket_id() == ticket_id:
                self.__tickets.pop(i)
                self.__total_amount = self.calculate_total()
                return True

        # Ticket not found
        return False

    def get_tickets(self) -> List[Ticket]:
        """Get all tickets in the order"""
        return self.__tickets

    def calculate_total(self) -> float:
        """Calculate the total amount of the order"""
        # Sum the prices of all tickets in the order
        # Uses polymorphism - each ticket type calculates its price differently
        return sum(ticket.calculate_price() for ticket in self.__tickets)

    def confirm_order(self) -> bool:
        """Confirm the order if conditions are met"""
        # Order must have tickets
        if not self.__tickets:
            return False

        # Order must have a payment method
        if not self.__payment_method:
            return False

        # Change order status to confirmed
        self.__status = OrderStatus.CONFIRMED
        return True

    def cancel_order(self) -> bool:
        """Cancel the order if possible"""
        # Check if any tickets are already used
        for ticket in self.__tickets:
            if ticket.is_used():
                return False

        # Check if any event dates have passed
        today = date.today()
        for ticket in self.__tickets:
            if ticket.get_event_date() < today:
                return False

        # Change order status to cancelled
        self.__status = OrderStatus.CANCELLED
        return True

    # String representation of the order
    def __str__(self) -> str:
        return (f"Order #{self.__order_id}, Status: {self.__status.value}, "
                f"Total: ${self.__total_amount:.2f}, Tickets: {len(self.__tickets)}")


# Main booking system class - manages users, tickets, and orders
class BookingSystem:
    def __init__(self, name: str, version: str):
        # System attributes
        self.__name = name                # Name of the booking system
        self.__version = version          # Version of the booking system
        self._database = None             # Protected attribute for database connection
        self._log_file = "booking_system.log"  # Protected attribute for log file

        # Collections to store entities - example of aggregation relationships
        self.__users = {}     # Dictionary mapping username -> User
        self.__admins = {}    # Dictionary mapping username -> Admin
        self.__tickets = {}   # Dictionary mapping ticket_id -> Ticket
        self.__orders = {}    # Dictionary mapping order_id -> Order

        # Create data directory if it doesn't exist
        self._data_dir = "data"
        if not os.path.exists(self._data_dir):
            os.makedirs(self._data_dir)

        # Load existing data from files
        self.load_data()

    # Getters and setters for BookingSystem attributes
    def get_name(self) -> str:
        return self.__name

    def set_name(self, name: str) -> None:
        self.__name = name

    def get_version(self) -> str:
        return self.__version

    def set_version(self, version: str) -> None:
        self.__version = version

    # File operations for data persistence
    def save_data(self) -> bool:
        """Save all system data to pickle files"""
        try:
            # Save users to users.pkl
            with open(os.path.join(self._data_dir, 'users.pkl'), 'wb') as f:
                pickle.dump(self.__users, f)

            # Save admins to admins.pkl
            with open(os.path.join(self._data_dir, 'admins.pkl'), 'wb') as f:
                pickle.dump(self.__admins, f)

            # Save tickets to tickets.pkl
            with open(os.path.join(self._data_dir, 'tickets.pkl'), 'wb') as f:
                pickle.dump(self.__tickets, f)

            # Save orders to orders.pkl
            with open(os.path.join(self._data_dir, 'orders.pkl'), 'wb') as f:
                pickle.dump(self.__orders, f)

            self._write_log("All data saved successfully")
            return True
        except Exception as e:
            self._write_log(f"Error saving data: {e}")
            return False

    def load_data(self) -> bool:
        """Load all system data from pickle files"""
        try:
            # Load users from users.pkl if it exists
            users_path = os.path.join(self._data_dir, 'users.pkl')
            if os.path.exists(users_path):
                with open(users_path, 'rb') as f:
                    self.__users = pickle.load(f)
                self._write_log(f"Loaded {len(self.__users)} users")

            # Load admins from admins.pkl if it exists
            admins_path = os.path.join(self._data_dir, 'admins.pkl')
            if os.path.exists(admins_path):
                with open(admins_path, 'rb') as f:
                    self.__admins = pickle.load(f)
                self._write_log(f"Loaded {len(self.__admins)} admins")
            else:
                # Create default admin if no admin data exists
                if not self.__admins:
                    self.create_admin(
                        "ADM-001",
                        "admin",
                        "admin123",
                        "admin@grandprix.com",
                        3,  # Highest level
                        "System Administration"
                    )
                    self._write_log("Created default admin account")

            # Load tickets from tickets.pkl if it exists
            tickets_path = os.path.join(self._data_dir, 'tickets.pkl')
            if os.path.exists(tickets_path):
                with open(tickets_path, 'rb') as f:
                    self.__tickets = pickle.load(f)
                self._write_log(f"Loaded {len(self.__tickets)} tickets")

            # Load orders from orders.pkl if it exists
            orders_path = os.path.join(self._data_dir, 'orders.pkl')
            if os.path.exists(orders_path):
                with open(orders_path, 'rb') as f:
                    self.__orders = pickle.load(f)
                self._write_log(f"Loaded {len(self.__orders)} orders")

            return True
        except Exception as e:
            self._write_log(f"Error loading data: {e}")
            return False

    # Protected methods (indicated by single underscore)
    def _connect_database(self) -> bool:
        """Connect to the database (protected method)"""
        # Simulate database connection - could be implemented with a real database
        self._database = "connected"
        self._write_log("Database connected")
        return True

    def _write_log(self, message: str) -> None:
        """Write to the log file (protected method)"""
        try:
            # Create a timestamp for the log entry
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_message = f"[{timestamp}] {message}\n"

            # Write to the log file
            with open(self._log_file, 'a') as f:
                f.write(log_message)

            # Print to console as well for debugging
            print(f"LOG: {message}")
        except Exception as e:
            print(f"Error writing to log file: {e}")
            print(f"LOG: {message}")

    # User management methods
    def create_user(self, user_id: str, username: str, password: str, email: str, phone_number: str = None) -> User:
        """Create a new user"""
        # Check if username already exists
        if username in self.__users:
            raise ValueError(f"Username '{username}' already exists")

        # Create a new User object
        user = User(user_id, username, password, email, phone_number)
        # Add to users dictionary
        self.__users[username] = user
        self._write_log(f"Created user: {username}")

        # Save changes to file
        self.save_data()

        return user

    def create_admin(self, user_id: str, username: str, password: str, email: str,
                     admin_level: int, department: str, phone_number: str = None) -> Admin:
        """Create a new admin"""
        # Check if username already exists
        if username in self.__users:
            raise ValueError(f"Username '{username}' already exists")

        # Create a new Admin object
        admin = Admin(user_id, username, password, email, admin_level, department, phone_number)
        # Add to both users and admins dictionaries
        self.__users[username] = admin
        self.__admins[username] = admin
        self._write_log(f"Created admin: {username}")

        # Save changes to file
        self.save_data()

        return admin

    def get_user(self, username: str) -> Optional[User]:
        """Get a user by username"""
        # Return the user if found, None otherwise
        return self.__users.get(username)

    def get_admin(self, username: str) -> Optional[Admin]:
        """Get an admin by username"""
        # Return the admin if found, None otherwise
        return self.__admins.get(username)

    # Ticket management methods
    def register_ticket(self, ticket: Ticket) -> None:
        """Register a ticket in the system"""
        ticket_id = ticket.get_ticket_id()
        # Check if ticket ID already exists
        if ticket_id in self.__tickets:
            raise ValueError(f"Ticket ID '{ticket_id}' already exists")

        # Add to tickets dictionary
        self.__tickets[ticket_id] = ticket
        self._write_log(f"Registered ticket: {ticket_id}")

        # Save changes to file
        self.save_data()

    def get_ticket(self, ticket_id: str) -> Optional[Ticket]:
        """Get a ticket by ID"""
        # Return the ticket if found, None otherwise
        return self.__tickets.get(ticket_id)

    # Order management methods
    def create_order(self, user: User) -> Order:
        """Create a new order for a user"""
        # Generate a unique order ID
        order_id = f"ORD-{len(self.__orders) + 1}"
        # Create a new Order object with today's date
        order = Order(order_id, date.today())
        # Set the user ID
        order.set_user_id(user.get_user_id())

        # Add order to the system
        self.__orders[order_id] = order

        # Add order to user's order history (bidirectional relationship)
        user.add_order(order)

        self._write_log(f"Created order: {order_id} for user: {user.get_username()}")

        # Save changes to file
        self.save_data()

        return order

    def get_order(self, order_id: str) -> Optional[Order]:
        """Get an order by ID"""
        # Return the order if found, None otherwise
        return self.__orders.get(order_id)

    def update_order(self, order: Order) -> None:
        """Update an existing order in the system"""
        order_id = order.get_order_id()
        # Check if order exists
        if order_id not in self.__orders:
            raise ValueError(f"Order '{order_id}' does not exist")

        # Update the order in the orders dictionary
        self.__orders[order_id] = order
        self._write_log(f"Updated order: {order_id}")

        # Save changes to file
        self.save_data()

    # String representation of the booking system
    def __str__(self) -> str:
        return (f"BookingSystem: {self.__name} v{self.__version}, "
                f"Users: {len(self.__users)}, Orders: {len(self.__orders)}, "
                f"Tickets: {len(self.__tickets)}")