import os
import pickle
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import date, datetime, timedelta
import random
from enum import Enum
from typing import List, Optional

# Import the shared path configuration
from grand_prix_shared_path import SHARED_DATA_PATH


# Enum Types
class RaceCategory(Enum):
    PREMIUM = "Premium"
    STANDARD = "Standard"
    ECONOMY = "Economy"


class OrderStatus(Enum):
    PENDING = "Pending"
    CONFIRMED = "Confirmed"
    CANCELLED = "Cancelled"


class PaymentMethod(Enum):
    CREDIT_CARD = "Credit Card"
    DEBIT_CARD = "Debit Card"
    DIGITAL_WALLET = "Digital Wallet"


# Abstract Ticket Class
class Ticket:
    def __init__(self, ticket_id: str, price: float, event_date: date, venue_section: str):
        self.__ticket_id = ticket_id  # Private attribute
        self.__price = price  # Private attribute
        self.__event_date = event_date  # Private attribute
        self.__venue_section = venue_section  # Private attribute
        self.__is_used = False  # Private attribute
        self.__created_by = None  # Private attribute for admin reference

    # Getters and setters
    def get_ticket_id(self) -> str:
        return self.__ticket_id

    def set_ticket_id(self, ticket_id: str) -> None:
        self.__ticket_id = ticket_id

    def get_price(self) -> float:
        return self.__price

    def set_price(self, price: float) -> None:
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

    def calculate_price(self) -> float:
        """Calculate the final price of the ticket, must be implemented by subclasses"""
        return self.__price

    def __str__(self) -> str:
        return f"Ticket ID: {self.__ticket_id}, Price: ${self.__price}, Date: {self.__event_date}, Section: {self.__venue_section}"


# SingleRaceTicket Class
class SingleRaceTicket(Ticket):
    def __init__(self, ticket_id: str, price: float, event_date: date, venue_section: str,
                 race_name: str, race_category: RaceCategory):
        super().__init__(ticket_id, price, event_date, venue_section)
        self.__race_name = race_name  # Private attribute
        self.__race_category = race_category  # Private attribute using enum

    # Getters and setters
    def get_race_name(self) -> str:
        return self.__race_name

    def set_race_name(self, race_name: str) -> None:
        self.__race_name = race_name

    def get_race_category(self) -> RaceCategory:
        return self.__race_category

    def set_race_category(self, race_category: RaceCategory) -> None:
        self.__race_category = race_category

    def calculate_price(self) -> float:
        """Calculate final price based on race category"""
        base_price = self.get_price()
        if self.__race_category == RaceCategory.PREMIUM:
            return base_price * 1.2  # 20% premium
        elif self.__race_category == RaceCategory.STANDARD:
            return base_price
        else:  # ECONOMY
            return base_price * 0.9  # 10% discount

    def __str__(self) -> str:
        return f"{super().__str__()}, Race: {self.__race_name}, Category: {self.__race_category.value}"


# SeasonTicket Class
class SeasonTicket(Ticket):
    def __init__(self, ticket_id: str, price: float, event_date: date, venue_section: str,
                 season_year: int, included_races: List[str], race_dates: List[date] = None):
        # For SeasonTicket, event_date represents season start date
        super().__init__(ticket_id, price, event_date, venue_section)
        self.__season_year = season_year  # Private attribute
        self.__included_races = included_races  # Private attribute
        self.__race_dates = race_dates if race_dates else []  # Private attribute

    # Getters and setters
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

    def calculate_price(self) -> float:
        """Calculate final price based on number of included races"""
        base_price = self.get_price()
        num_races = len(self.__included_races)

        if num_races >= 15:
            return base_price * 0.7  # 30% discount for 15+ races
        elif num_races >= 10:
            return base_price * 0.8  # 20% discount for 10-14 races
        elif num_races >= 5:
            return base_price * 0.9  # 10% discount for 5-9 races
        else:
            return base_price  # No discount for less than 5 races

    def __str__(self) -> str:
        races_str = ", ".join(self.__included_races) if self.__included_races else "None"
        return f"{super().__str__()}, Year: {self.__season_year}, Races: {races_str}"


# User Class
class User:
    def __init__(self, user_id: str, username: str, password: str, email: str, phone_number: str = None):
        self.__user_id = user_id  # Private attribute
        self.__username = username  # Private attribute
        self.__password = password  # Private attribute
        self.__email = email  # Private attribute
        self.__phone_number = phone_number  # Private attribute
        self.__orders = []  # Private attribute for bidirectional relationship

    # Getters and setters
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
        if len(password) < 6:
            raise ValueError("Password must be at least 6 characters long")
        self.__password = password

    def get_email(self) -> str:
        return self.__email

    def set_email(self, email: str) -> None:
        if '@' not in email:
            raise ValueError("Invalid email format")
        self.__email = email

    def get_phone_number(self) -> Optional[str]:
        return self.__phone_number

    def set_phone_number(self, phone_number: str) -> None:
        self.__phone_number = phone_number

    def get_orders(self) -> List:
        return self.__orders

    def add_order(self, order) -> None:
        self.__orders.append(order)

    def verify_password(self, password: str) -> bool:
        return self.__password == password

    def __str__(self) -> str:
        return f"User: {self.__username} ({self.__email})"


# Admin Class
class Admin(User):
    def __init__(self, user_id: str, username: str, password: str, email: str,
                 admin_level: int, department: str, phone_number: str = None):
        super().__init__(user_id, username, password, email, phone_number)
        self.__admin_level = admin_level  # Private attribute
        self.__department = department  # Private attribute

    # Getters and setters
    def get_admin_level(self) -> int:
        return self.__admin_level

    def set_admin_level(self, admin_level: int) -> None:
        if admin_level < 1 or admin_level > 3:
            raise ValueError("Admin level must be between 1 and 3")
        self.__admin_level = admin_level

    def get_department(self) -> str:
        return self.__department

    def set_department(self, department: str) -> None:
        self.__department = department

    def create_ticket(self, ticket_type: str, ticket_id: str, price: float, event_date: date,
                      venue_section: str, **kwargs) -> Ticket:
        """Create a new ticket of the specified type"""
        ticket = None

        if ticket_type == "SingleRace":
            race_name = kwargs.get('race_name', '')
            if not race_name:
                raise ValueError("Race name is required for SingleRaceTicket")

            race_category = kwargs.get('race_category', RaceCategory.STANDARD)
            ticket = SingleRaceTicket(ticket_id, price, event_date, venue_section, race_name, race_category)

        elif ticket_type == "Season":
            season_year = kwargs.get('season_year', event_date.year)
            included_races = kwargs.get('included_races', [])
            race_dates = kwargs.get('race_dates', [])

            ticket = SeasonTicket(ticket_id, price, event_date, venue_section,
                                  season_year, included_races, race_dates)
        else:
            raise ValueError(f"Invalid ticket type: {ticket_type}")

        # Set the admin as creator
        ticket.set_created_by(self)

        return ticket

    def __str__(self) -> str:
        return f"Admin: {self.get_username()}, Level: {self.__admin_level}, Department: {self.__department}"


# Order Class
class Order:
    def __init__(self, order_id: str, order_date: date, status: OrderStatus = OrderStatus.PENDING,
                 total_amount: float = 0.0, payment_method: PaymentMethod = None):
        self.__order_id = order_id  # Private attribute
        self.__order_date = order_date  # Private attribute
        self.__status = status  # Private attribute using enum
        self.__total_amount = total_amount  # Private attribute
        self.__payment_method = payment_method  # Private attribute using enum
        self.__tickets = []  # Private attribute for composition relationship
        self.__user_id = None  # Private attribute to reference the user

    # Getters and setters
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

    # Methods to manage tickets
    def add_ticket(self, ticket: Ticket) -> None:
        """Add a ticket to the order"""
        if self.__status == OrderStatus.CONFIRMED:
            raise ValueError("Cannot add tickets to a confirmed order")

        self.__tickets.append(ticket)
        self.__total_amount = self.calculate_total()

    def remove_ticket(self, ticket_id: str) -> bool:
        """Remove a ticket from the order"""
        if self.__status == OrderStatus.CONFIRMED:
            return False

        for i, ticket in enumerate(self.__tickets):
            if ticket.get_ticket_id() == ticket_id:
                self.__tickets.pop(i)
                self.__total_amount = self.calculate_total()
                return True

        return False

    def get_tickets(self) -> List[Ticket]:
        """Get all tickets in the order"""
        return self.__tickets

    def calculate_total(self) -> float:
        """Calculate the total amount of the order"""
        return sum(ticket.calculate_price() for ticket in self.__tickets)

    def confirm_order(self) -> bool:
        """Confirm the order if conditions are met"""
        if not self.__tickets:
            return False

        if not self.__payment_method:
            return False

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

        self.__status = OrderStatus.CANCELLED
        return True

    def __str__(self) -> str:
        return (f"Order #{self.__order_id}, Status: {self.__status.value}, "
                f"Total: ${self.__total_amount:.2f}, Tickets: {len(self.__tickets)}")


# BookingSystem Class with Pickle Persistence
class BookingSystem:
    def __init__(self, name: str, version: str):
        self.__name = name  # Private attribute
        self.__version = version  # Private attribute
        self._database = None  # Protected attribute
        self._log_file = os.path.join(SHARED_DATA_PATH, "booking_system.log")  # Protected attribute

        # Track last modification times
        self._last_mod_times = {}

        # Aggregation relationships
        self.__users = {}  # username -> User
        self.__admins = {}  # username -> Admin (also in users)
        self.__tickets = {}  # ticket_id -> Ticket
        self.__orders = {}  # order_id -> Order
        self.__races = {}  # race_id -> race details
        self.__seasons = {}  # season_id -> season details

        # Data directory
        self._data_dir = SHARED_DATA_PATH
        if not os.path.exists(self._data_dir):
            os.makedirs(self._data_dir)

        # Load data from files if they exist
        self.load_data()

        # Create sample races and seasons if none exist
        if not self.__races:
            self._create_sample_races()
        if not self.__seasons:
            self._create_sample_seasons()

    def _create_sample_races(self):
        """Create sample races data"""
        races = {
            "R001": {
                "name": "Monaco Grand Prix",
                "date": date.today() + timedelta(days=30),
                "venue": "Circuit de Monaco",
                "price": 300.0,
                "category": RaceCategory.PREMIUM
            },
            "R002": {
                "name": "British Grand Prix",
                "date": date.today() + timedelta(days=60),
                "venue": "Silverstone Circuit",
                "price": 250.0,
                "category": RaceCategory.STANDARD
            },
            "R003": {
                "name": "Italian Grand Prix",
                "date": date.today() + timedelta(days=90),
                "venue": "Monza Circuit",
                "price": 200.0,
                "category": RaceCategory.ECONOMY
            },
            "R004": {
                "name": "Abu Dhabi Grand Prix",
                "date": date.today() + timedelta(days=120),
                "venue": "Yas Marina Circuit",
                "price": 280.0,
                "category": RaceCategory.PREMIUM
            },
            "R005": {
                "name": "Singapore Grand Prix",
                "date": date.today() + timedelta(days=150),
                "venue": "Marina Bay Street Circuit",
                "price": 270.0,
                "category": RaceCategory.STANDARD
            },
        }

        self.__races = races

        # Save to file
        with open(os.path.join(self._data_dir, 'races.pkl'), 'wb') as f:
            pickle.dump(races, f)

    def _create_sample_seasons(self):
        """Create sample seasons data"""
        current_year = date.today().year

        races = list(self.__races.keys())
        race_names = [self.__races[race_id]["name"] for race_id in races]
        race_dates = [self.__races[race_id]["date"] for race_id in races]

        seasons = {
            "S2025": {
                "year": current_year,
                "name": f"{current_year} Grand Prix Season",
                "start_date": date.today(),
                "end_date": date.today() + timedelta(days=180),
                "races": races,
                "race_names": race_names,
                "race_dates": race_dates,
                "price": 1200.0
            }
        }

        self.__seasons = seasons

        # Save to file
        with open(os.path.join(self._data_dir, 'seasons.pkl'), 'wb') as f:
            pickle.dump(seasons, f)

    # Getters and setters
    def get_name(self) -> str:
        return self.__name

    def set_name(self, name: str) -> None:
        self.__name = name

    def get_version(self) -> str:
        return self.__version

    def set_version(self, version: str) -> None:
        self.__version = version

    def get_races(self):
        return self.__races

    def get_seasons(self):
        return self.__seasons

    # File operations
    def save_data(self) -> bool:
        """Save all system data to pickle files"""
        try:
            # Save users
            with open(os.path.join(self._data_dir, 'users.pkl'), 'wb') as f:
                pickle.dump(self.__users, f)

            # Save admins
            with open(os.path.join(self._data_dir, 'admins.pkl'), 'wb') as f:
                pickle.dump(self.__admins, f)

            # Save tickets
            with open(os.path.join(self._data_dir, 'tickets.pkl'), 'wb') as f:
                pickle.dump(self.__tickets, f)

            # Save orders
            with open(os.path.join(self._data_dir, 'orders.pkl'), 'wb') as f:
                pickle.dump(self.__orders, f)

            # Save races
            with open(os.path.join(self._data_dir, 'races.pkl'), 'wb') as f:
                pickle.dump(self.__races, f)

            # Save seasons
            with open(os.path.join(self._data_dir, 'seasons.pkl'), 'wb') as f:
                pickle.dump(self.__seasons, f)

            self._write_log("All data saved successfully")
            return True
        except Exception as e:
            self._write_log(f"Error saving data: {e}")
            return False

    def load_data(self) -> bool:
        """Load all system data from pickle files if they've been modified since last load"""
        try:
            files_to_check = [
                ('users.pkl', self.__users),
                ('admins.pkl', self.__admins),
                ('tickets.pkl', self.__tickets),
                ('orders.pkl', self.__orders),
                ('races.pkl', self.__races),
                ('seasons.pkl', self.__seasons)
            ]

            any_loaded = False

            for filename, data_dict in files_to_check:
                file_path = os.path.join(self._data_dir, filename)

                # Check if file exists and has been modified
                if os.path.exists(file_path):
                    mod_time = os.path.getmtime(file_path)
                    last_mod_time = self._last_mod_times.get(filename, 0)

                    # If file has been modified since last load
                    if mod_time > last_mod_time:
                        self._write_log(f"File {filename} has been modified, reloading...")
                        with open(file_path, 'rb') as f:
                            data = pickle.load(f)

                        # For users and admins, need special handling to preserve references
                        if filename == 'users.pkl':
                            # Update but preserve admin references
                            admin_usernames = list(self.__admins.keys())
                            self.__users.clear()
                            self.__users.update(data)
                            # Ensure admins reference is maintained
                            self.__admins = {username: self.__users[username] for username in admin_usernames
                                             if username in self.__users}
                        elif filename == 'admins.pkl' and not self.__admins:
                            # Only load admins if we don't have any
                            self.__admins.update(data)
                        else:
                            # For other data, just replace the dictionary
                            data_dict.clear()
                            data_dict.update(data)

                        # Update last modification time
                        self._last_mod_times[filename] = mod_time
                        any_loaded = True
                        self._write_log(f"Loaded {len(data)} items from {filename}")

            return True
        except Exception as e:
            self._write_log(f"Error loading data: {e}")
            import traceback
            traceback.print_exc()
            return False

    # Protected methods
    def _connect_database(self) -> bool:
        """Connect to the database (protected method)"""
        # Simulate database connection
        self._database = "connected"
        self._write_log("Database connected")
        return True

    def _write_log(self, message: str) -> None:
        """Write to the log file (protected method)"""
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_message = f"[{timestamp}] {message}\n"

            with open(self._log_file, 'a') as f:
                f.write(log_message)

            # Print to console as well
            print(f"LOG: {message}")
        except Exception as e:
            print(f"Error writing to log file: {e}")
            print(f"LOG: {message}")

    # User management
    def create_user(self, user_id: str, username: str, password: str, email: str, phone_number: str = None) -> User:
        """Create a new user"""
        if username in self.__users:
            raise ValueError(f"Username '{username}' already exists")

        user = User(user_id, username, password, email, phone_number)
        self.__users[username] = user
        self._write_log(f"Created user: {username}")

        # Save changes to file
        self.save_data()

        return user

    def get_user(self, username: str) -> Optional[User]:
        """Get a user by username"""
        return self.__users.get(username)

    # Ticket management
    def register_ticket(self, ticket: Ticket) -> None:
        """Register a ticket in the system"""
        ticket_id = ticket.get_ticket_id()
        if ticket_id in self.__tickets:
            raise ValueError(f"Ticket ID '{ticket_id}' already exists")

        self.__tickets[ticket_id] = ticket
        self._write_log(f"Registered ticket: {ticket_id}")

        # Save changes to file
        self.save_data()

    def get_ticket(self, ticket_id: str) -> Optional[Ticket]:
        """Get a ticket by ID"""
        return self.__tickets.get(ticket_id)

    def get_all_tickets(self):
        """Return all tickets"""
        return self.__tickets

    # Order management
    def create_order(self, user: User) -> Order:
        """Create a new order for a user"""
        # Generate a unique order ID
        order_id = f"ORD-{len(self.__orders) + 1}"
        order = Order(order_id, date.today())
        order.set_user_id(user.get_username())

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
        return self.__orders.get(order_id)

    def get_all_orders(self):
        """Return all orders"""
        return self.__orders

    def update_order(self, order: Order) -> None:
        """Update an existing order in the system"""
        order_id = order.get_order_id()
        if order_id not in self.__orders:
            raise ValueError(f"Order '{order_id}' does not exist")

        self.__orders[order_id] = order
        self._write_log(f"Updated order: {order_id}")

        # Save changes to file
        self.save_data()

    def __str__(self) -> str:
        return (f"BookingSystem: {self.__name} v{self.__version}, "
                f"Users: {len(self.__users)}, Orders: {len(self.__orders)}, "
                f"Tickets: {len(self.__tickets)}")


# GUI Classes for Customer Application
class LoginPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        # Configure the frame
        self.configure(bg="#2c3e50")

        # Title
        title_label = tk.Label(self, text="Grand Prix Experience", font=("Arial", 24, "bold"), bg="#2c3e50",
                               fg="#ecf0f1")
        title_label.pack(pady=20)

        # Subtitle
        subtitle_label = tk.Label(self, text="Customer Ticket Portal", font=("Arial", 16), bg="#2c3e50", fg="#ecf0f1")
        subtitle_label.pack(pady=5)

        # Create a frame for login
        login_frame = tk.Frame(self, bg="#34495e", padx=20, pady=20, bd=2, relief=tk.GROOVE)
        login_frame.pack(pady=20, padx=50, fill="both", expand=True)

        # Username
        tk.Label(login_frame, text="Username:", bg="#34495e", fg="#ecf0f1", font=("Arial", 12)).pack(anchor="w",
                                                                                                     pady=(10, 5))
        self.username_entry = tk.Entry(login_frame, font=("Arial", 12), width=30, bg="#000000")
        self.username_entry.pack(fill="x", pady=5)

        # Password
        tk.Label(login_frame, text="Password:", bg="#34495e", fg="#ecf0f1", font=("Arial", 12)).pack(anchor="w",
                                                                                                     pady=(10, 5))
        self.password_entry = tk.Entry(login_frame, show="*", font=("Arial", 12), width=30, bg="#000000")
        self.password_entry.pack(fill="x", pady=5)

        # Login button
        login_button = tk.Button(login_frame, text="Login", command=self.login, bg="#3498db", fg="gray",
                                 font=("Arial", 12, "bold"), padx=15, pady=5)
        login_button.pack(pady=15)

        # Register link
        register_frame = tk.Frame(login_frame, bg="#34495e")
        register_frame.pack(pady=10)
        tk.Label(register_frame, text="Don't have an account?", bg="#34495e", fg="#ecf0f1").pack(side=tk.LEFT)
        register_link = tk.Label(register_frame, text="Register", fg="#3498db", cursor="hand2", bg="#34495e")
        register_link.pack(side=tk.LEFT, padx=5)
        register_link.bind("<Button-1>", lambda e: self.controller.show_frame(RegisterPage))

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if not username or not password:
            messagebox.showerror("Error", "Username and password are required")
            return

        # Check if user exists
        user = self.controller.booking_system.get_user(username)

        if not user or not user.verify_password(password):
            messagebox.showerror("Error", "Invalid username or password")
            return

        # Check if user is admin
        if isinstance(user, Admin):
            messagebox.showerror("Error", "Admin accounts must use the Admin Portal")
            return

        # Set current user
        self.controller.current_user = user

        # Clear fields
        self.username_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)

        # Go to customer dashboard
        self.controller.show_frame(CustomerDashboard)
        self.controller.frames[CustomerDashboard].refresh_user_info()


class RegisterPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        # Configure the frame
        self.configure(bg="#2c3e50")

        # Title
        title_label = tk.Label(self, text="Register New Account", font=("Arial", 24, "bold"), bg="#2c3e50",
                               fg="#ecf0f1")
        title_label.pack(pady=20)

        # Create a frame for registration form
        register_frame = tk.Frame(self, bg="#34495e", padx=20, pady=20, bd=2, relief=tk.GROOVE)
        register_frame.pack(pady=20, padx=50, fill="both", expand=True)

        # Username
        tk.Label(register_frame, text="Username:", bg="#34495e", fg="#ecf0f1", font=("Arial", 12)).pack(anchor="w",
                                                                                                        pady=(10, 5))
        self.username_entry = tk.Entry(register_frame, font=("Arial", 12), width=30, bg="#000000")
        self.username_entry.pack(fill="x", pady=5)

        # Password
        tk.Label(register_frame, text="Password:", bg="#34495e", fg="#ecf0f1", font=("Arial", 12)).pack(anchor="w",
                                                                                                        pady=(10, 5))
        self.password_entry = tk.Entry(register_frame, show="*", font=("Arial", 12), width=30, bg="#000000")
        self.password_entry.pack(fill="x", pady=5)

        # Email
        tk.Label(register_frame, text="Email:", bg="#34495e", fg="#ecf0f1", font=("Arial", 12)).pack(anchor="w",
                                                                                                     pady=(10, 5))
        self.email_entry = tk.Entry(register_frame, font=("Arial", 12), width=30, bg="#000000")
        self.email_entry.pack(fill="x", pady=5)

        # Phone
        tk.Label(register_frame, text="Phone (optional):", bg="#34495e", fg="#ecf0f1", font=("Arial", 12)).pack(
            anchor="w", pady=(10, 5))
        self.phone_entry = tk.Entry(register_frame, font=("Arial", 12), width=30, bg="#000000")
        self.phone_entry.pack(fill="x", pady=5)

        # Register button
        register_button = tk.Button(register_frame, text="Register", command=self.register, bg="#2ecc71", fg="gray",
                                    font=("Arial", 12, "bold"), padx=15, pady=5)
        register_button.pack(pady=15)

        # Back to login
        back_button = tk.Button(register_frame, text="Back to Login", command=lambda: controller.show_frame(LoginPage),
                                bg="#7f8c8d", fg="gray", font=("Arial", 10), padx=10, pady=3)
        back_button.pack(pady=10)

    def register(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        email = self.email_entry.get()
        phone = self.phone_entry.get() if self.phone_entry.get() else None

        # Validate input
        if not username or not password or not email:
            messagebox.showerror("Error", "Username, password, and email are required")
            return

        if '@' not in email:
            messagebox.showerror("Error", "Invalid email format")
            return

        if len(password) < 6:
            messagebox.showerror("Error", "Password must be at least 6 characters long")
            return

        # Check if username already exists
        if self.controller.booking_system.get_user(username):
            messagebox.showerror("Error", "Username already exists")
            return

        try:
            # Generate user ID
            user_id = f"USR-{random.randint(1000, 9999)}"

            # Create new user
            self.controller.booking_system.create_user(user_id, username, password, email, phone)

            messagebox.showinfo("Success", "Account created successfully. You can now login.")

            # Clear fields
            self.username_entry.delete(0, tk.END)
            self.password_entry.delete(0, tk.END)
            self.email_entry.delete(0, tk.END)
            self.phone_entry.delete(0, tk.END)

            # Go back to login page
            self.controller.show_frame(LoginPage)

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")


class CustomerDashboard(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        # Configure the frame
        self.configure(bg="#2c3e50")

        # Create header frame
        header_frame = tk.Frame(self, bg="#3498db", padx=15, pady=10)
        header_frame.pack(fill="x")

        # Title in header
        title_label = tk.Label(header_frame, text="Customer Dashboard", font=("Arial", 18, "bold"), bg="#3498db",
                               fg="gray")
        title_label.pack(side=tk.LEFT)

        # User info in header
        self.user_info_label = tk.Label(header_frame, text="Welcome, User", font=("Arial", 12), bg="#3498db",
                                        fg="gray")
        self.user_info_label.pack(side=tk.RIGHT)

        # Logout button in header
        logout_button = tk.Button(header_frame, text="Logout", command=self.logout, bg="#e74c3c", fg="gray",
                                  font=("Arial", 10), padx=10, pady=2)
        logout_button.pack(side=tk.RIGHT, padx=10)

        # Create main content frame
        content_frame = tk.Frame(self, bg="#2c3e50")
        content_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Create tabs
        tabControl = ttk.Notebook(content_frame)

        # Tab 1: Buy Tickets
        self.tab1 = tk.Frame(tabControl, bg="#34495e")
        tabControl.add(self.tab1, text="Buy Tickets")

        # Tab 2: My Orders
        self.tab2 = tk.Frame(tabControl, bg="#34495e")
        tabControl.add(self.tab2, text="My Orders")

        # Tab 3: My Profile
        self.tab3 = tk.Frame(tabControl, bg="#34495e")
        tabControl.add(self.tab3, text="My Profile")

        tabControl.pack(expand=1, fill="both")

        # Initialize tab contents
        self.init_buy_tickets_tab()
        self.init_my_orders_tab()
        self.init_my_profile_tab()

    def init_buy_tickets_tab(self):
        # Create two frames for ticket options
        ticket_frame = tk.Frame(self.tab1, bg="#34495e", padx=20, pady=20)
        ticket_frame.pack(fill="both", expand=True)

        # Title for the tab
        tab_title = tk.Label(ticket_frame, text="Purchase Tickets", font=("Arial", 16, "bold"), bg="#34495e",
                             fg="#ecf0f1")
        tab_title.grid(row=0, column=0, columnspan=2, pady=10, sticky="w")

        # Choose ticket type
        tk.Label(ticket_frame, text="Select Ticket Type:", font=("Arial", 12), bg="#34495e", fg="#ecf0f1").grid(row=1,
                                                                                                                column=0,
                                                                                                                pady=5,
                                                                                                                sticky="w")
        self.ticket_type_var = tk.StringVar(value="Single Race")
        ticket_type_menu = ttk.Combobox(ticket_frame, textvariable=self.ticket_type_var,
                                        values=["Single Race", "Season Package"], state="readonly", width=30)
        ticket_type_menu.grid(row=1, column=1, pady=5, sticky="w")
        ticket_type_menu.bind("<<ComboboxSelected>>", self.update_ticket_options)

        # Frame for single race options
        self.single_race_frame = tk.Frame(ticket_frame, bg="#34495e")
        self.single_race_frame.grid(row=2, column=0, columnspan=2, sticky="we")

        # Frame for season package options
        self.season_frame = tk.Frame(ticket_frame, bg="#34495e")
        self.season_frame.grid(row=2, column=0, columnspan=2, sticky="we")

        # Hide season frame initially
        self.season_frame.grid_remove()

        # Initialize single race options
        self.init_single_race_options()

        # Initialize season package options
        self.init_season_package_options()

        # Order Summary Frame
        summary_frame = tk.LabelFrame(ticket_frame, text="Order Summary", font=("Arial", 12, "bold"), bg="#2c3e50",
                                      fg="#ecf0f1", padx=15, pady=15)
        summary_frame.grid(row=3, column=0, columnspan=2, pady=20, sticky="we")

        # Selected tickets
        tk.Label(summary_frame, text="Selected Tickets:", font=("Arial", 11, "bold"), bg="#2c3e50", fg="#ecf0f1").grid(
            row=0, column=0, sticky="w")
        self.selected_tickets_var = tk.StringVar(value="None")
        tk.Label(summary_frame, textvariable=self.selected_tickets_var, font=("Arial", 11), bg="#2c3e50",
                 fg="#ecf0f1").grid(row=0, column=1, sticky="w")

        # Total price
        tk.Label(summary_frame, text="Total Price:", font=("Arial", 11, "bold"), bg="#2c3e50", fg="#ecf0f1").grid(row=1,
                                                                                                                  column=0,
                                                                                                                  sticky="w")
        self.total_price_var = tk.StringVar(value="$0.00")
        tk.Label(summary_frame, textvariable=self.total_price_var, font=("Arial", 11), bg="#2c3e50", fg="#ecf0f1").grid(
            row=1, column=1, sticky="w")

        # Payment method
        tk.Label(summary_frame, text="Payment Method:", font=("Arial", 11, "bold"), bg="#2c3e50", fg="#ecf0f1").grid(
            row=2, column=0, sticky="w")
        self.payment_method_var = tk.StringVar(value="Credit Card")
        payment_method_menu = ttk.Combobox(summary_frame, textvariable=self.payment_method_var,
                                           values=["Credit Card", "Debit Card", "Digital Wallet"],
                                           state="readonly", width=15)
        payment_method_menu.grid(row=2, column=1, sticky="w")

        # Purchase button
        purchase_button = tk.Button(summary_frame, text="Complete Purchase", command=self.complete_purchase,
                                    bg="#2ecc71", fg="gray", font=("Arial", 12, "bold"), padx=15, pady=5)
        purchase_button.grid(row=3, column=0, columnspan=2, pady=(15, 5))

    def init_single_race_options(self):
        # Clear any existing widgets
        for widget in self.single_race_frame.winfo_children():
            widget.destroy()

        # Get races from booking system
        races = self.controller.booking_system.get_races()

        # Race selection
        tk.Label(self.single_race_frame, text="Select Race:", font=("Arial", 11), bg="#34495e", fg="#ecf0f1").grid(
            row=0, column=0, pady=5, sticky="w")
        self.race_var = tk.StringVar()
        race_options = []

        # Create list of race options
        for race_id, race_data in races.items():
            race_name = race_data["name"]
            race_date = race_data["date"].strftime("%d %b %Y")
            race_price = race_data["price"]
            race_category = race_data["category"].value

            race_options.append(f"{race_name} - {race_date} - ${race_price} ({race_category})")

        if race_options:
            self.race_var.set(race_options[0])

        race_menu = ttk.Combobox(self.single_race_frame, textvariable=self.race_var, values=race_options,
                                 state="readonly", width=40)
        race_menu.grid(row=0, column=1, pady=5, sticky="w")

        # Venue section
        tk.Label(self.single_race_frame, text="Venue Section:", font=("Arial", 11), bg="#34495e", fg="#ecf0f1").grid(
            row=1, column=0, pady=5, sticky="w")
        self.venue_section_var = tk.StringVar()
        self.venue_section_var.set("Main Grandstand")
        venue_section_menu = ttk.Combobox(self.single_race_frame, textvariable=self.venue_section_var,
                                          values=["Main Grandstand", "Paddock Club", "Turn 1", "Backstretch",
                                                  "Club Area"],
                                          state="readonly", width=20)
        venue_section_menu.grid(row=1, column=1, pady=5, sticky="w")

        # Quantity
        tk.Label(self.single_race_frame, text="Quantity:", font=("Arial", 11), bg="#000000", fg="#ecf0f1").grid(row=2,
                                                                                                                column=0,
                                                                                                                pady=5,
                                                                                                                sticky="w")
        self.quantity_var = tk.IntVar()
        self.quantity_var.set(1)
        quantity_spinbox = tk.Spinbox(self.single_race_frame, from_=1, to=10, textvariable=self.quantity_var, width=5,
                                      bg="#000000")
        quantity_spinbox.grid(row=2, column=1, pady=5, sticky="w")

        # Add to cart button
        add_button = tk.Button(self.single_race_frame, text="Add to Cart", command=self.add_single_race_to_cart,
                               bg="#3498db", fg="gray", font=("Arial", 11), padx=10, pady=3)
        add_button.grid(row=3, column=0, columnspan=2, pady=(10, 5), sticky="w")

    def init_season_package_options(self):
        # Clear any existing widgets
        for widget in self.season_frame.winfo_children():
            widget.destroy()

        # Get seasons from booking system
        seasons = self.controller.booking_system.get_seasons()

        # Season selection
        tk.Label(self.season_frame, text="Select Season:", font=("Arial", 11), bg="#34495e", fg="#ecf0f1").grid(row=0,
                                                                                                                column=0,
                                                                                                                pady=5,
                                                                                                                sticky="w")
        self.season_var = tk.StringVar()
        season_options = []

        # Create list of season options
        for season_id, season_data in seasons.items():
            season_name = season_data["name"]
            season_year = season_data["year"]
            season_price = season_data["price"]
            race_count = len(season_data["races"])

            season_options.append(f"{season_name} - {race_count} races - ${season_price}")

        if season_options:
            self.season_var.set(season_options[0])

        season_menu = ttk.Combobox(self.season_frame, textvariable=self.season_var, values=season_options,
                                   state="readonly", width=40)
        season_menu.grid(row=0, column=1, pady=5, sticky="w")

        # Venue section
        tk.Label(self.season_frame, text="Preferred Section:", font=("Arial", 11), bg="#34495e", fg="#ecf0f1").grid(
            row=1, column=0, pady=5, sticky="w")
        self.season_section_var = tk.StringVar()
        self.season_section_var.set("Main Grandstand")
        season_section_menu = ttk.Combobox(self.season_frame, textvariable=self.season_section_var,
                                           values=["Main Grandstand", "Paddock Club", "Turn 1", "Backstretch",
                                                   "Club Area"],
                                           state="readonly", width=20)
        season_section_menu.grid(row=1, column=1, pady=5, sticky="w")

        # Quantity
        tk.Label(self.season_frame, text="Quantity:", font=("Arial", 11), bg="#000000", fg="#ecf0f1").grid(row=2,
                                                                                                           column=0,
                                                                                                           pady=5,
                                                                                                           sticky="w")
        self.season_quantity_var = tk.IntVar()
        self.season_quantity_var.set(1)
        season_quantity_spinbox = tk.Spinbox(self.season_frame, from_=1, to=5, textvariable=self.season_quantity_var,
                                             width=5, bg="#000000")
        season_quantity_spinbox.grid(row=2, column=1, pady=5, sticky="w")

        # Add to cart button
        add_button = tk.Button(self.season_frame, text="Add to Cart", command=self.add_season_to_cart,
                               bg="#3498db", fg="gray", font=("Arial", 11), padx=10, pady=3)
        add_button.grid(row=3, column=0, columnspan=2, pady=(10, 5), sticky="w")

    def init_my_orders_tab(self):
        # Create frame for orders list
        orders_frame = tk.Frame(self.tab2, bg="#34495e", padx=20, pady=20)
        orders_frame.pack(fill="both", expand=True)

        # Title for the tab
        tab_title = tk.Label(orders_frame, text="My Orders", font=("Arial", 16, "bold"), bg="#34495e", fg="#ecf0f1")
        tab_title.pack(anchor="w", pady=10)

        # Create TreeView for orders
        columns = ("Order ID", "Date", "Status", "Total", "Tickets")
        self.orders_tree = ttk.Treeview(orders_frame, columns=columns, show="headings")

        # Define headings
        for col in columns:
            self.orders_tree.heading(col, text=col)

        # Set column widths
        self.orders_tree.column("Order ID", width=100)
        self.orders_tree.column("Date", width=100)
        self.orders_tree.column("Status", width=100)
        self.orders_tree.column("Total", width=100)
        self.orders_tree.column("Tickets", width=80)

        # Add scrollbar
        scrollbar = ttk.Scrollbar(orders_frame, orient="vertical", command=self.orders_tree.yview)
        self.orders_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.orders_tree.pack(fill="both", expand=True)

        # Add Double-click event to view order details
        self.orders_tree.bind("<Double-1>", self.view_order_details)

        # Refresh button
        refresh_button = tk.Button(orders_frame, text="Refresh Orders", command=self.refresh_orders,
                                   bg="#7f8c8d", fg="gray", font=("Arial", 11), padx=10, pady=3)
        refresh_button.pack(anchor="e", pady=10)

    def init_my_profile_tab(self):
        # Create frame for profile info
        profile_frame = tk.Frame(self.tab3, bg="#34495e", padx=20, pady=20)
        profile_frame.pack(fill="both", expand=True)

        # Title for the tab
        tab_title = tk.Label(profile_frame, text="My Profile", font=("Arial", 16, "bold"), bg="#34495e", fg="#ecf0f1")
        tab_title.pack(anchor="w", pady=10)

        # Create profile info form
        info_frame = tk.Frame(profile_frame, bg="#34495e")
        info_frame.pack(fill="x", padx=20, pady=20)

        # Username
        tk.Label(info_frame, text="Username:", font=("Arial", 12, "bold"), bg="#34495e", fg="#ecf0f1").grid(row=0,
                                                                                                            column=0,
                                                                                                            sticky="w",
                                                                                                            pady=5)
        self.username_label = tk.Label(info_frame, text="", font=("Arial", 12), bg="#000000", fg="#ecf0f1")
        self.username_label.grid(row=0, column=1, sticky="w", pady=5)

        # Email
        tk.Label(info_frame, text="Email:", font=("Arial", 12, "bold"), bg="#34495e", fg="#ecf0f1").grid(row=1,
                                                                                                         column=0,
                                                                                                         sticky="w",
                                                                                                         pady=5)
        self.email_var = tk.StringVar()
        self.email_entry = tk.Entry(info_frame, textvariable=self.email_var, font=("Arial", 12), width=30, bg="#000000")
        self.email_entry.grid(row=1, column=1, sticky="w", pady=5)

        # Phone
        tk.Label(info_frame, text="Phone:", font=("Arial", 12, "bold"), bg="#34495e", fg="#ecf0f1").grid(row=2,
                                                                                                         column=0,
                                                                                                         sticky="w",
                                                                                                         pady=5)
        self.phone_var = tk.StringVar()
        self.phone_entry = tk.Entry(info_frame, textvariable=self.phone_var, font=("Arial", 12), width=30, bg="#000000")
        self.phone_entry.grid(row=2, column=1, sticky="w", pady=5)

        # Password change section
        password_frame = tk.LabelFrame(profile_frame, text="Change Password", font=("Arial", 12, "bold"), bg="#34495e",
                                       fg="#ecf0f1", padx=15, pady=15)
        password_frame.pack(fill="x", padx=20, pady=10)

        # Current password
        tk.Label(password_frame, text="Current Password:", font=("Arial", 11), bg="#34495e", fg="#ecf0f1").grid(row=0,
                                                                                                                column=0,
                                                                                                                sticky="w",
                                                                                                                pady=5)
        self.current_password_var = tk.StringVar()
        self.current_password_entry = tk.Entry(password_frame, textvariable=self.current_password_var, show="*",
                                               font=("Arial", 11), width=20, bg="#000000")
        self.current_password_entry.grid(row=0, column=1, sticky="w", pady=5)

        # New password
        tk.Label(password_frame, text="New Password:", font=("Arial", 11), bg="#34495e", fg="#ecf0f1").grid(row=1,
                                                                                                            column=0,
                                                                                                            sticky="w",
                                                                                                            pady=5)
        self.new_password_var = tk.StringVar()
        self.new_password_entry = tk.Entry(password_frame, textvariable=self.new_password_var, show="*",
                                           font=("Arial", 11), width=20, bg="#000000")
        self.new_password_entry.grid(row=1, column=1, sticky="w", pady=5)

        # Confirm new password
        tk.Label(password_frame, text="Confirm New Password:", font=("Arial", 11), bg="#000000", fg="#ecf0f1").grid(
            row=2, column=0, sticky="w", pady=5)
        self.confirm_password_var = tk.StringVar()
        self.confirm_password_entry = tk.Entry(password_frame, textvariable=self.confirm_password_var, show="*",
                                               font=("Arial", 11), width=20, bg="#000000")
        self.confirm_password_entry.grid(row=2, column=1, sticky="w", pady=5)

        # Button frame
        button_frame = tk.Frame(profile_frame, bg="#34495e")
        button_frame.pack(fill="x", padx=20, pady=20)

        # Update profile button
        update_profile_button = tk.Button(button_frame, text="Update Profile", command=self.update_profile,
                                          bg="#2ecc71", fg="gray", font=("Arial", 12), padx=15, pady=5)
        update_profile_button.pack(side="left", padx=5)

        # Change password button
        change_password_button = tk.Button(button_frame, text="Change Password", command=self.change_password,
                                           bg="#3498db", fg="gray", font=("Arial", 12), padx=15, pady=5)
        change_password_button.pack(side="left", padx=5)

    def update_ticket_options(self, event=None):
        ticket_type = self.ticket_type_var.get()

        if ticket_type == "Single Race":
            self.season_frame.grid_remove()
            self.single_race_frame.grid()
        else:  # Season Package
            self.single_race_frame.grid_remove()
            self.season_frame.grid()

    def refresh_user_info(self):
        if not self.controller.current_user:
            return

        # Update user info in header
        self.user_info_label.config(text=f"Welcome, {self.controller.current_user.get_username()}")

        # Update profile tab info
        self.username_label.config(text=self.controller.current_user.get_username())
        self.email_var.set(self.controller.current_user.get_email())
        self.phone_var.set(self.controller.current_user.get_phone_number() or "")

        # Refresh orders
        self.refresh_orders()

    def refresh_orders(self):
        if not self.controller.current_user:
            return

        # Clear current tree
        for item in self.orders_tree.get_children():
            self.orders_tree.delete(item)

        # Get user's orders
        orders = self.controller.current_user.get_orders()

        # Add orders to tree
        for order in orders:
            order_id = order.get_order_id()
            order_date = order.get_order_date().strftime("%d-%m-%Y")
            order_status = order.get_status().value
            order_total = f"${order.get_total_amount():.2f}"
            ticket_count = len(order.get_tickets())

            self.orders_tree.insert("", "end", values=(order_id, order_date, order_status, order_total, ticket_count))

    def view_order_details(self, event):
        # Get selected item
        selected_item = self.orders_tree.selection()

        if not selected_item:
            return

        # Get order ID from selected item
        order_id = self.orders_tree.item(selected_item, "values")[0]

        # Get order from booking system
        order = self.controller.booking_system.get_order(order_id)

        if not order:
            messagebox.showerror("Error", "Order not found")
            return

        # Create order details window
        details_window = tk.Toplevel(self)
        details_window.title(f"Order Details - {order_id}")
        details_window.geometry("600x400")
        details_window.configure(bg="#34495e")

        # Order details
        tk.Label(details_window, text=f"Order ID: {order.get_order_id()}", font=("Arial", 14, "bold"), bg="#34495e",
                 fg="#ecf0f1").pack(anchor="w", padx=20, pady=(20, 10))
        tk.Label(details_window, text=f"Date: {order.get_order_date().strftime('%d %B %Y')}", font=("Arial", 12),
                 bg="#34495e", fg="#ecf0f1").pack(anchor="w", padx=20, pady=2)
        tk.Label(details_window, text=f"Status: {order.get_status().value}", font=("Arial", 12), bg="#34495e",
                 fg="#ecf0f1").pack(anchor="w", padx=20, pady=2)

        payment_method = "Not specified"
        if order.get_payment_method():
            payment_method = order.get_payment_method().value

        tk.Label(details_window, text=f"Payment Method: {payment_method}", font=("Arial", 12), bg="#34495e",
                 fg="#ecf0f1").pack(anchor="w", padx=20, pady=2)
        tk.Label(details_window, text=f"Total Amount: ${order.get_total_amount():.2f}", font=("Arial", 12),
                 bg="#34495e", fg="#ecf0f1").pack(anchor="w", padx=20, pady=2)

        # Tickets section
        tk.Label(details_window, text="Tickets:", font=("Arial", 14, "bold"), bg="#34495e", fg="#ecf0f1").pack(
            anchor="w", padx=20, pady=(20, 10))

        # Create frame for tickets
        tickets_frame = tk.Frame(details_window, bg="#34495e")
        tickets_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Create scrollable text widget for tickets
        tickets_text = tk.Text(tickets_frame, height=10, width=60, wrap="word", bg="#2c3e50", fg="#ecf0f1")
        tickets_text.pack(side="left", fill="both", expand=True)

        # Add scrollbar
        scrollbar = ttk.Scrollbar(tickets_frame, orient="vertical", command=tickets_text.yview)
        tickets_text.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        # Add tickets to text widget
        tickets = order.get_tickets()

        if not tickets:
            tickets_text.insert("end", "No tickets in this order")
        else:
            for i, ticket in enumerate(tickets):
                tickets_text.insert("end", f"Ticket {i + 1}: {ticket}\n\n")

        tickets_text.configure(state="disabled")  # Make read-only

        # Close button
        close_button = tk.Button(details_window, text="Close", command=details_window.destroy,
                                 bg="#000000", fg="gray", font=("Arial", 12), padx=15, pady=5)
        close_button.pack(pady=20)

    def add_single_race_to_cart(self):
        if not self.controller.current_user:
            messagebox.showerror("Error", "Please login first")
            return

        # Get selected race
        race_selection = self.race_var.get()

        if not race_selection:
            messagebox.showerror("Error", "Please select a race")
            return

        # Parse race selection to get race details
        race_name = race_selection.split(" - ")[0]
        race_date_str = race_selection.split(" - ")[1]
        race_price_str = race_selection.split(" - ")[2].split(" ")[0].replace("$", "")
        race_category_str = race_selection.split("(")[1].replace(")", "")

        # Get venue section and quantity
        venue_section = self.venue_section_var.get()
        quantity = self.quantity_var.get()

        # Update order summary
        self.selected_tickets_var.set(f"{quantity} x {race_name} ({venue_section})")

        # Calculate total price
        race_price = float(race_price_str)

        # Apply category multiplier
        if race_category_str == "Premium":
            race_price *= 1.2
        elif race_category_str == "Economy":
            race_price *= 0.9

        total_price = race_price * quantity
        self.total_price_var.set(f"${total_price:.2f}")

        # Show success message
        messagebox.showinfo("Success", f"Added {quantity} ticket(s) for {race_name} to cart")

    def add_season_to_cart(self):
        if not self.controller.current_user:
            messagebox.showerror("Error", "Please login first")
            return

        # Get selected season
        season_selection = self.season_var.get()

        if not season_selection:
            messagebox.showerror("Error", "Please select a season package")
            return

        # Parse season selection to get season details
        season_name = season_selection.split(" - ")[0]
        race_count = int(season_selection.split(" - ")[1].split(" ")[0])
        season_price_str = season_selection.split(" - ")[2].replace("$", "")

        # Get venue section and quantity
        venue_section = self.season_section_var.get()
        quantity = self.season_quantity_var.get()

        # Update order summary
        self.selected_tickets_var.set(f"{quantity} x Season: {season_name} ({venue_section})")

        # Calculate total price
        season_price = float(season_price_str)

        # Apply discount based on race count
        if race_count >= 15:
            season_price *= 0.7  # 30% discount
        elif race_count >= 10:
            season_price *= 0.8  # 20% discount
        elif race_count >= 5:
            season_price *= 0.9  # 10% discount

        total_price = season_price * quantity
        self.total_price_var.set(f"${total_price:.2f}")

        # Show success message
        messagebox.showinfo("Success", f"Added {quantity} season package(s) for {season_name} to cart")

    def complete_purchase(self):
        if not self.controller.current_user:
            messagebox.showerror("Error", "Please login first")
            return

        # Check if cart is empty
        if self.selected_tickets_var.get() == "None":
            messagebox.showerror("Error", "Your cart is empty")
            return

        # Get payment method
        payment_method_str = self.payment_method_var.get()

        # Map payment method string to enum
        payment_method_map = {
            "Credit Card": PaymentMethod.CREDIT_CARD,
            "Debit Card": PaymentMethod.DEBIT_CARD,
            "Digital Wallet": PaymentMethod.DIGITAL_WALLET
        }

        payment_method = payment_method_map.get(payment_method_str)

        # Create a new order
        try:
            order = self.controller.booking_system.create_order(self.controller.current_user)

            # Set payment method
            order.set_payment_method(payment_method)

            # Create tickets based on selection
            if "Season:" in self.selected_tickets_var.get():
                # Parse season selection
                parts = self.selected_tickets_var.get().split(" x ")
                quantity = int(parts[0])
                season_name = parts[1].split(" (")[0].replace("Season: ", "")
                venue_section = parts[1].split("(")[1].replace(")", "")

                # Find season in system
                seasons = self.controller.booking_system.get_seasons()
                season_data = None

                for season_id, data in seasons.items():
                    if data["name"] == season_name:
                        season_data = data
                        break

                if not season_data:
                    raise ValueError(f"Season {season_name} not found")

                # Create season tickets
                for i in range(quantity):
                    # Create a unique ticket ID
                    ticket_id = f"SEASON-{random.randint(10000, 99999)}"

                    # Create the ticket
                    season_ticket = SeasonTicket(
                        ticket_id,
                        season_data["price"],
                        season_data["start_date"],
                        venue_section,
                        season_data["year"],
                        season_data["race_names"],
                        season_data["race_dates"]
                    )

                    # Register the ticket in the system
                    self.controller.booking_system.register_ticket(season_ticket)

                    # Add the ticket to the order
                    order.add_ticket(season_ticket)
            else:
                # Parse race selection
                parts = self.selected_tickets_var.get().split(" x ")
                quantity = int(parts[0])
                race_name = parts[1].split(" (")[0]
                venue_section = parts[1].split("(")[1].replace(")", "")

                # Find race in system
                races = self.controller.booking_system.get_races()
                race_data = None

                for race_id, data in races.items():
                    if data["name"] == race_name:
                        race_data = data
                        break

                if not race_data:
                    raise ValueError(f"Race {race_name} not found")

                # Create single race tickets
                for i in range(quantity):
                    # Create a unique ticket ID
                    ticket_id = f"RACE-{random.randint(10000, 99999)}"

                    # Create the ticket
                    race_ticket = SingleRaceTicket(
                        ticket_id,
                        race_data["price"],
                        race_data["date"],
                        venue_section,
                        race_name,
                        race_data["category"]
                    )

                    # Register the ticket in the system
                    self.controller.booking_system.register_ticket(race_ticket)

                    # Add the ticket to the order
                    order.add_ticket(race_ticket)

            # Confirm the order
            if order.confirm_order():
                # Update the order in the system
                self.controller.booking_system.update_order(order)

                # Show success message
                messagebox.showinfo("Success", f"Purchase completed successfully!\nOrder ID: {order.get_order_id()}")

                # Reset cart
                self.selected_tickets_var.set("None")
                self.total_price_var.set("$0.00")

                # Refresh orders list
                self.refresh_orders()
            else:
                messagebox.showerror("Error", "Failed to confirm order")

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def update_profile(self):
        if not self.controller.current_user:
            return

        # Get values from entries
        email = self.email_var.get()
        phone = self.phone_var.get()

        # Validate email
        if not email or '@' not in email:
            messagebox.showerror("Error", "Invalid email format")
            return

        # Update user object
        try:
            self.controller.current_user.set_email(email)
            self.controller.current_user.set_phone_number(phone if phone else None)

            # Save changes
            self.controller.booking_system.save_data()

            messagebox.showinfo("Success", "Profile updated successfully")

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def change_password(self):
        if not self.controller.current_user:
            return

        # Get values from entries
        current_password = self.current_password_var.get()
        new_password = self.new_password_var.get()
        confirm_password = self.confirm_password_var.get()

        # Validate inputs
        if not current_password or not new_password or not confirm_password:
            messagebox.showerror("Error", "All password fields are required")
            return

        if not self.controller.current_user.verify_password(current_password):
            messagebox.showerror("Error", "Current password is incorrect")
            return

        if new_password != confirm_password:
            messagebox.showerror("Error", "New passwords do not match")
            return

        if len(new_password) < 6:
            messagebox.showerror("Error", "Password must be at least 6 characters long")
            return

        # Update password
        try:
            self.controller.current_user.set_password(new_password)

            # Save changes
            self.controller.booking_system.save_data()

            # Clear fields
            self.current_password_var.set("")
            self.new_password_var.set("")
            self.confirm_password_var.set("")

            messagebox.showinfo("Success", "Password changed successfully")

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def logout(self):
        # Reset user
        self.controller.current_user = None

        # Clear fields
        self.selected_tickets_var.set("None")
        self.total_price_var.set("$0.00")

        # Go back to login page
        self.controller.show_frame(LoginPage)


class CustomerApp(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)

        # Set window title and size
        self.title("Grand Prix Customer Portal")
        self.geometry("900x700")
        self.resizable(True, True)

        # Initialize booking system
        self.booking_system = BookingSystem("Grand Prix Experience", "1.0")

        # Current user
        self.current_user = None

        # Set up container for frames
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # Initialize frames
        self.frames = {}
        for F in (LoginPage, RegisterPage, CustomerDashboard):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        # Show login page first
        self.show_frame(LoginPage)

    def show_frame(self, cont):
        # Raise the selected frame
        frame = self.frames[cont]
        frame.tkraise()


# Run the application
if __name__ == "__main__":
    app = CustomerApp()
    app.mainloop()