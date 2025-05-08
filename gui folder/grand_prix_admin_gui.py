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

            # Create default admin if no admin data exists
            if not self.__admins:
                if 'admin' not in self.__users:
                    self.create_admin(
                        "ADM-001",
                        "admin",
                        "admin123",
                        "admin@grandprix.com",
                        3,  # Highest level
                        "System Administration"
                    )
                    self._write_log("Created default admin account")
                    any_loaded = True

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

    def create_admin(self, user_id: str, username: str, password: str, email: str,
                     admin_level: int, department: str, phone_number: str = None) -> Admin:
        """Create a new admin"""
        if username in self.__users:
            raise ValueError(f"Username '{username}' already exists")

        admin = Admin(user_id, username, password, email, admin_level, department, phone_number)
        self.__users[username] = admin
        self.__admins[username] = admin
        self._write_log(f"Created admin: {username}")

        # Save changes to file
        self.save_data()

        return admin

    def get_user(self, username: str) -> Optional[User]:
        """Get a user by username"""
        return self.__users.get(username)

    def get_admin(self, username: str) -> Optional[Admin]:
        """Get an admin by username"""
        return self.__admins.get(username)

    def get_all_users(self):
        """Return all users"""
        return self.__users

    def get_all_admins(self):
        """Return all admins"""
        return self.__admins

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


# GUI Classes for Admin Application
class AdminLoginPage(tk.Frame):
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
        subtitle_label = tk.Label(self, text="Admin Management Portal", font=("Arial", 16), bg="#2c3e50", fg="#ecf0f1")
        subtitle_label.pack(pady=5)

        # Create a frame for login
        login_frame = tk.Frame(self, bg="#34495e", padx=20, pady=20, bd=2, relief=tk.GROOVE)
        login_frame.pack(pady=20, padx=50, fill="both", expand=True)

        # Username
        tk.Label(login_frame, text="Admin Username:", bg="#34495e", fg="#ecf0f1", font=("Arial", 12)).pack(anchor="w",
                                                                                                           pady=(10, 5))
        self.username_entry = tk.Entry(login_frame, font=("Arial", 12), width=30, bg="#000000")
        self.username_entry.pack(fill="x", pady=5)

        # Password
        tk.Label(login_frame, text="Admin Password:", bg="#34495e", fg="#ecf0f1", font=("Arial", 12)).pack(anchor="w",
                                                                                                           pady=(10, 5))
        self.password_entry = tk.Entry(login_frame, show="*", font=("Arial", 12), width=30, bg="#000000")
        self.password_entry.pack(fill="x", pady=5)

        # Login button
        login_button = tk.Button(login_frame, text="Login as Admin", command=self.admin_login, bg="#000000", fg="gray",
                                 font=("Arial", 12, "bold"), padx=15, pady=5)
        login_button.pack(pady=15)

        # Register link
        register_frame = tk.Frame(login_frame, bg="#34495e")
        register_frame.pack(pady=10)
        tk.Label(register_frame, text="New Admin?", bg="#34495e", fg="#ecf0f1").pack(side=tk.LEFT)
        register_link = tk.Label(register_frame, text="Register Admin Account", fg="#e74c3c", cursor="hand2",
                                 bg="#34495e")
        register_link.pack(side=tk.LEFT, padx=5)
        register_link.bind("<Button-1>", lambda e: self.controller.show_frame(AdminRegisterPage))

    def admin_login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if not username or not password:
            messagebox.showerror("Error", "Username and password are required")
            return

        # Check if admin exists
        admin = self.controller.booking_system.get_admin(username)

        if not admin or not admin.verify_password(password):
            messagebox.showerror("Error", "Invalid admin username or password")
            return

        # Set current user
        self.controller.current_user = admin

        # Clear fields
        self.username_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)

        # Go to admin dashboard
        self.controller.show_frame(AdminDashboard)
        self.controller.frames[AdminDashboard].refresh_dashboard()


class AdminRegisterPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        # Configure the frame
        self.configure(bg="#2c3e50")

        # Title
        title_label = tk.Label(self, text="Register Admin Account", font=("Arial", 24, "bold"), bg="#2c3e50",
                               fg="#ecf0f1")
        title_label.pack(pady=20)

        # Create a frame for registration form
        register_frame = tk.Frame(self, bg="#34495e", padx=20, pady=20, bd=2, relief=tk.GROOVE)
        register_frame.pack(pady=20, padx=50, fill="both", expand=True)

        # Admin code (to prevent unauthorized registrations)
        tk.Label(register_frame, text="Admin Registration Code:", bg="#34495e", fg="#ecf0f1", font=("Arial", 12)).pack(
            anchor="w", pady=(10, 5))
        self.admin_code_entry = tk.Entry(register_frame, show="*", font=("Arial", 12), width=30, bg="#000000")
        self.admin_code_entry.pack(fill="x", pady=5)

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

        # Admin Level
        tk.Label(register_frame, text="Admin Level (1-3):", bg="#000000", fg="#ecf0f1", font=("Arial", 12)).pack(
            anchor="w", pady=(10, 5))
        self.level_var = tk.IntVar(value=1)
        self.level_spinbox = tk.Spinbox(register_frame, from_=1, to=3, textvariable=self.level_var, width=5,
                                        bg="#000000")
        self.level_spinbox.pack(anchor="w", pady=5)

        # Department
        tk.Label(register_frame, text="Department:", bg="#000000", fg="#ecf0f1", font=("Arial", 12)).pack(anchor="w",
                                                                                                          pady=(10, 5))
        self.department_var = tk.StringVar(value="Ticket Sales")
        department_menu = ttk.Combobox(register_frame, textvariable=self.department_var,
                                       values=["Ticket Sales", "Customer Support", "System Administration",
                                               "Event Management"],
                                       state="readonly", width=20)
        department_menu.pack(anchor="w", pady=5)

        # Register button
        register_button = tk.Button(register_frame, text="Register Admin", command=self.register_admin, bg="#000000",
                                    fg="gray", font=("Arial", 12, "bold"), padx=15, pady=5)
        register_button.pack(pady=15)

        # Back to login
        back_button = tk.Button(register_frame, text="Back to Login",
                                command=lambda: controller.show_frame(AdminLoginPage), bg="#000000", fg="gray",
                                font=("Arial", 10), padx=10, pady=3)
        back_button.pack(pady=10)

    def register_admin(self):
        # Check admin code (simple solution, in production use a more secure approach)
        admin_code = self.admin_code_entry.get()
        if admin_code != "admin123":  # Simple code for this example
            messagebox.showerror("Error", "Invalid admin registration code")
            return

        username = self.username_entry.get()
        password = self.password_entry.get()
        email = self.email_entry.get()
        phone = self.phone_entry.get() if self.phone_entry.get() else None
        level = self.level_var.get()
        department = self.department_var.get()

        # Validate input
        if not username or not password or not email or not department:
            messagebox.showerror("Error", "Username, password, email, and department are required")
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
            # Generate admin ID
            admin_id = f"ADM-{random.randint(1000, 9999)}"

            # Create new admin
            self.controller.booking_system.create_admin(admin_id, username, password, email, level, department, phone)

            messagebox.showinfo("Success", "Admin account created successfully. You can now login.")

            # Clear fields
            self.admin_code_entry.delete(0, tk.END)
            self.username_entry.delete(0, tk.END)
            self.password_entry.delete(0, tk.END)
            self.email_entry.delete(0, tk.END)
            self.phone_entry.delete(0, tk.END)

            # Go back to login page
            self.controller.show_frame(AdminLoginPage)

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")


class AdminDashboard(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        # Configure the frame
        self.configure(bg="#2c3e50")

        # Create header frame
        header_frame = tk.Frame(self, bg="#e74c3c", padx=15, pady=10)
        header_frame.pack(fill="x")

        # Title in header
        title_label = tk.Label(header_frame, text="Admin Dashboard", font=("Arial", 18, "bold"), bg="#e74c3c",
                               fg="gray")
        title_label.pack(side=tk.LEFT)

        # Admin info in header
        self.admin_info_label = tk.Label(header_frame, text="Admin", font=("Arial", 12), bg="#000000", fg="gray")
        self.admin_info_label.pack(side=tk.RIGHT)

        # Logout button in header
        logout_button = tk.Button(header_frame, text="Logout", command=self.logout, bg="#000000", fg="gray",
                                  font=("Arial", 10), padx=10, pady=2)
        logout_button.pack(side=tk.RIGHT, padx=10)

        # Reload data button
        reload_button = tk.Button(header_frame, text="🔄 Reload Data", command=self.reload_data, bg="#000000",
                                  fg="gray", font=("Arial", 10), padx=10, pady=2)
        reload_button.pack(side=tk.RIGHT, padx=10)

        # Create main content frame
        content_frame = tk.Frame(self, bg="#2c3e50")
        content_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Create tabs
        tabControl = ttk.Notebook(content_frame)

        # Tab 1: Dashboard
        self.tab1 = tk.Frame(tabControl, bg="#34495e")
        tabControl.add(self.tab1, text="Dashboard")

        # Tab 2: Users
        self.tab2 = tk.Frame(tabControl, bg="#34495e")
        tabControl.add(self.tab2, text="Users")

        # Tab 3: Tickets
        self.tab3 = tk.Frame(tabControl, bg="#34495e")
        tabControl.add(self.tab3, text="Tickets")

        # Tab 4: Orders
        self.tab4 = tk.Frame(tabControl, bg="#34495e")
        tabControl.add(self.tab4, text="Orders")

        # Tab 5: Admin Management
        self.tab5 = tk.Frame(tabControl, bg="#34495e")
        tabControl.add(self.tab5, text="Admin Management")

        tabControl.pack(expand=1, fill="both")

        # Initialize tab contents
        self.init_dashboard_tab()
        self.init_users_tab()
        self.init_tickets_tab()
        self.init_orders_tab()
        self.init_admin_management_tab()

    def init_dashboard_tab(self):
        # Create a frame for dashboard
        dashboard_frame = tk.Frame(self.tab1, bg="#34495e", padx=20, pady=20)
        dashboard_frame.pack(fill="both", expand=True)

        # Welcome message
        welcome_label = tk.Label(dashboard_frame, text="Welcome to the Admin Dashboard", font=("Arial", 16, "bold"),
                                 bg="#34495e", fg="#ecf0f1")
        welcome_label.pack(pady=20)

        # Create dashboard cards
        cards_frame = tk.Frame(dashboard_frame, bg="#34495e")
        cards_frame.pack(fill="x", pady=20)

        # Users Card
        user_card = tk.Frame(cards_frame, bg="#3498db", padx=15, pady=15, width=200, height=100)
        user_card.grid(row=0, column=0, padx=10, pady=10)
        user_card.grid_propagate(False)

        tk.Label(user_card, text="Total Users", font=("Arial", 14, "bold"), bg="#3498db", fg="gray").pack(anchor="w")
        self.users_count_label = tk.Label(user_card, text="0", font=("Arial", 20, "bold"), bg="#3498db", fg="gray")
        self.users_count_label.pack(anchor="center", pady=10)

        # Tickets Card
        ticket_card = tk.Frame(cards_frame, bg="#2ecc71", padx=15, pady=15, width=200, height=100)
        ticket_card.grid(row=0, column=1, padx=10, pady=10)
        ticket_card.grid_propagate(False)

        tk.Label(ticket_card, text="Total Tickets", font=("Arial", 14, "bold"), bg="#2ecc71", fg="gray").pack(
            anchor="w")
        self.tickets_count_label = tk.Label(ticket_card, text="0", font=("Arial", 20, "bold"), bg="#2ecc71", fg="gray")
        self.tickets_count_label.pack(anchor="center", pady=10)

        # Orders Card
        order_card = tk.Frame(cards_frame, bg="#f39c12", padx=15, pady=15, width=200, height=100)
        order_card.grid(row=0, column=2, padx=10, pady=10)
        order_card.grid_propagate(False)

        tk.Label(order_card, text="Total Orders", font=("Arial", 14, "bold"), bg="#f39c12", fg="black").pack(anchor="w")
        self.orders_count_label = tk.Label(order_card, text="0", font=("Arial", 20, "bold"), bg="#f39c12", fg="black")
        self.orders_count_label.pack(anchor="center", pady=10)

        # Revenue Card
        revenue_card = tk.Frame(cards_frame, bg="#1abc9c", padx=15, pady=15, width=200, height=100)
        revenue_card.grid(row=0, column=3, padx=10, pady=10)
        revenue_card.grid_propagate(False)

        tk.Label(revenue_card, text="Total Revenue", font=("Arial", 14, "bold"), bg="#1abc9c", fg="gray").pack(
            anchor="w")
        self.revenue_label = tk.Label(revenue_card, text="$0.00", font=("Arial", 20, "bold"), bg="#1abc9c", fg="gray")
        self.revenue_label.pack(anchor="center", pady=10)

        # Recent Activity Section
        tk.Label(dashboard_frame, text="Recent Orders", font=("Arial", 14, "bold"), bg="#34495e", fg="#ecf0f1").pack(
            anchor="w", pady=(20, 10))

        # Create a frame for recent orders
        recent_orders_frame = tk.Frame(dashboard_frame, bg="#34495e")
        recent_orders_frame.pack(fill="both", expand=True)

        # Create TreeView for recent orders
        columns = ("Order ID", "Date", "User", "Status", "Total")
        self.recent_orders_tree = ttk.Treeview(recent_orders_frame, columns=columns, show="headings", height=5)

        # Define headings
        for col in columns:
            self.recent_orders_tree.heading(col, text=col)

        # Set column widths
        self.recent_orders_tree.column("Order ID", width=100)
        self.recent_orders_tree.column("Date", width=100)
        self.recent_orders_tree.column("User", width=150)
        self.recent_orders_tree.column("Status", width=100)
        self.recent_orders_tree.column("Total", width=100)

        # Add scrollbar
        scrollbar = ttk.Scrollbar(recent_orders_frame, orient="vertical", command=self.recent_orders_tree.yview)
        self.recent_orders_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.recent_orders_tree.pack(fill="both", expand=True)

        # Add Double-click event to view order details
        self.recent_orders_tree.bind("<Double-1>", self.view_recent_order_details)

        # Refresh button
        refresh_button = tk.Button(dashboard_frame, text="Refresh Dashboard", command=self.refresh_dashboard,
                                   bg="#7f8c8d", fg="gray", font=("Arial", 11), padx=10, pady=3)
        refresh_button.pack(anchor="e", pady=10)

    def init_users_tab(self):
        # Create a frame for users
        users_frame = tk.Frame(self.tab2, bg="#34495e", padx=20, pady=20)
        users_frame.pack(fill="both", expand=True)

        # Title
        tk.Label(users_frame, text="User Management", font=("Arial", 16, "bold"), bg="#34495e", fg="#ecf0f1").pack(
            anchor="w", pady=10)

        # Search frame
        search_frame = tk.Frame(users_frame, bg="#34495e")
        search_frame.pack(fill="x", pady=10)

        tk.Label(search_frame, text="Search Users:", font=("Arial", 11), bg="#000000", fg="#ecf0f1").pack(side=tk.LEFT)
        search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=search_var, font=("Arial", 11), width=20, bg="#000000")
        search_entry.pack(side=tk.LEFT, padx=10)

        search_button = tk.Button(search_frame, text="Search",
                                  command=lambda: self.search_users(search_var.get()),
                                  bg="#000000", fg="gray", font=("Arial", 10), padx=10, pady=2)
        search_button.pack(side=tk.LEFT, padx=5)

        clear_button = tk.Button(search_frame, text="Clear",
                                 command=lambda: [search_var.set(""), self.refresh_users()],
                                 bg="#000000", fg="gray", font=("Arial", 10), padx=10, pady=2)
        clear_button.pack(side=tk.LEFT, padx=5)

        # Create TreeView for users
        columns = ("ID", "Username", "Email", "Phone", "Orders")
        self.users_tree = ttk.Treeview(users_frame, columns=columns, show="headings")

        # Define headings
        for col in columns:
            self.users_tree.heading(col, text=col)

        # Set column widths
        self.users_tree.column("ID", width=80)
        self.users_tree.column("Username", width=150)
        self.users_tree.column("Email", width=200)
        self.users_tree.column("Phone", width=120)
        self.users_tree.column("Orders", width=80)

        # Add scrollbar
        scrollbar = ttk.Scrollbar(users_frame, orient="vertical", command=self.users_tree.yview)
        self.users_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.users_tree.pack(fill="both", expand=True)

        # Add Double-click event to view user details
        self.users_tree.bind("<Double-1>", self.view_user_details)

        # Button frame
        button_frame = tk.Frame(users_frame, bg="#34495e")
        button_frame.pack(fill="x", pady=10)

        # Refresh button
        refresh_button = tk.Button(button_frame, text="Refresh Users", command=self.refresh_users,
                                   bg="#7f8c8d", fg="gray", font=("Arial", 11), padx=10, pady=3)
        refresh_button.pack(side=tk.LEFT, padx=5)

        # Export users button
        export_button = tk.Button(button_frame, text="Export Users Data", command=self.export_users_data,
                                  bg="#f39c12", fg="gray", font=("Arial", 11), padx=10, pady=3)
        export_button.pack(side=tk.LEFT, padx=5)

    def init_tickets_tab(self):
        # Create a frame for tickets
        tickets_frame = tk.Frame(self.tab3, bg="#34495e", padx=20, pady=20)
        tickets_frame.pack(fill="both", expand=True)

        # Title
        tk.Label(tickets_frame, text="Ticket Management", font=("Arial", 16, "bold"), bg="#34495e", fg="#ecf0f1").pack(
            anchor="w", pady=10)

        # Create TreeView for tickets
        columns = ("ID", "Type", "Price", "Date", "Section", "Used")
        self.tickets_tree = ttk.Treeview(tickets_frame, columns=columns, show="headings")

        # Define headings
        for col in columns:
            self.tickets_tree.heading(col, text=col)

        # Set column widths
        self.tickets_tree.column("ID", width=100)
        self.tickets_tree.column("Type", width=150)
        self.tickets_tree.column("Price", width=80)
        self.tickets_tree.column("Date", width=100)
        self.tickets_tree.column("Section", width=150)
        self.tickets_tree.column("Used", width=80)

        # Add scrollbar
        scrollbar = ttk.Scrollbar(tickets_frame, orient="vertical", command=self.tickets_tree.yview)
        self.tickets_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.tickets_tree.pack(fill="both", expand=True)

        # Add Double-click event to view ticket details
        self.tickets_tree.bind("<Double-1>", self.view_ticket_details)

        # Button frame
        button_frame = tk.Frame(tickets_frame, bg="#34495e")
        button_frame.pack(fill="x", pady=10)

        # Refresh button
        refresh_button = tk.Button(button_frame, text="Refresh Tickets", command=self.refresh_tickets,
                                   bg="#7f8c8d", fg="gray", font=("Arial", 11), padx=10, pady=3)
        refresh_button.pack(side=tk.LEFT, padx=5)

    def init_orders_tab(self):
        # Create a frame for orders
        orders_frame = tk.Frame(self.tab4, bg="#34495e", padx=20, pady=20)
        orders_frame.pack(fill="both", expand=True)

        # Title
        tk.Label(orders_frame, text="Order Management", font=("Arial", 16, "bold"), bg="#34495e", fg="#ecf0f1").pack(
            anchor="w", pady=10)

        # Create TreeView for orders
        columns = ("ID", "Date", "User", "Status", "Payment", "Total", "Tickets")
        self.orders_tree = ttk.Treeview(orders_frame, columns=columns, show="headings")

        # Define headings
        for col in columns:
            self.orders_tree.heading(col, text=col)

        # Set column widths
        self.orders_tree.column("ID", width=80)
        self.orders_tree.column("Date", width=100)
        self.orders_tree.column("User", width=100)
        self.orders_tree.column("Status", width=100)
        self.orders_tree.column("Payment", width=120)
        self.orders_tree.column("Total", width=80)
        self.orders_tree.column("Tickets", width=80)

        # Add scrollbar
        scrollbar = ttk.Scrollbar(orders_frame, orient="vertical", command=self.orders_tree.yview)
        self.orders_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.orders_tree.pack(fill="both", expand=True)

        # Add Double-click event to view order details
        self.orders_tree.bind("<Double-1>", self.view_order_details)

        # Button frame
        button_frame = tk.Frame(orders_frame, bg="#34495e")
        button_frame.pack(fill="x", pady=10)

        # Refresh button
        refresh_button = tk.Button(button_frame, text="Refresh Orders", command=self.refresh_orders,
                                   bg="#7f8c8d", fg="gray", font=("Arial", 11), padx=10, pady=3)
        refresh_button.pack(side=tk.LEFT, padx=5)

    def init_admin_management_tab(self):
        # Create a frame for admin management
        admin_frame = tk.Frame(self.tab5, bg="#34495e", padx=20, pady=20)
        admin_frame.pack(fill="both", expand=True)

        # Title
        tk.Label(admin_frame, text="Admin Management", font=("Arial", 16, "bold"), bg="#34495e", fg="#ecf0f1").pack(
            anchor="w", pady=10)

        # Create TreeView for admins
        columns = ("ID", "Username", "Email", "Level", "Department", "Phone")
        self.admins_tree = ttk.Treeview(admin_frame, columns=columns, show="headings")

        # Define headings
        for col in columns:
            self.admins_tree.heading(col, text=col)

        # Set column widths
        self.admins_tree.column("ID", width=80)
        self.admins_tree.column("Username", width=120)
        self.admins_tree.column("Email", width=180)
        self.admins_tree.column("Level", width=60)
        self.admins_tree.column("Department", width=150)
        self.admins_tree.column("Phone", width=120)

        # Add scrollbar
        scrollbar = ttk.Scrollbar(admin_frame, orient="vertical", command=self.admins_tree.yview)
        self.admins_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.admins_tree.pack(fill="both", expand=True)

        # Button frame
        button_frame = tk.Frame(admin_frame, bg="#34495e")
        button_frame.pack(fill="x", pady=10)

        # Refresh button
        refresh_button = tk.Button(button_frame, text="Refresh Admins", command=self.refresh_admins,
                                   bg="#7f8c8d", fg="gray", font=("Arial", 11), padx=10, pady=3)
        refresh_button.pack(side=tk.LEFT, padx=5)

        # Add admin button
        add_admin_button = tk.Button(button_frame, text="Add New Admin", command=self.add_admin,
                                     bg="#000000", fg="gray", font=("Arial", 11), padx=10, pady=3)
        add_admin_button.pack(side=tk.LEFT, padx=5)

    def reload_data(self):
        """Force reload all data from disk"""
        # Reload all data from disk
        success = self.controller.booking_system.load_data()

        if success:
            messagebox.showinfo("Success", "Data reloaded successfully from disk")
            # Refresh all views
            self.refresh_dashboard()
            self.refresh_users()
            self.refresh_tickets()
            self.refresh_orders()
            self.refresh_admins()
        else:
            messagebox.showerror("Error", "Failed to reload data")

    def refresh_dashboard(self):
        # Reload data from disk first
        self.controller.booking_system.load_data()

        # Update admin info in header
        if self.controller.current_user and isinstance(self.controller.current_user, Admin):
            admin = self.controller.current_user
            self.admin_info_label.config(text=f"Admin: {admin.get_username()} (Level {admin.get_admin_level()})")

        # Get data from booking system
        users = self.controller.booking_system.get_all_users()
        tickets = self.controller.booking_system.get_all_tickets()
        orders = self.controller.booking_system.get_all_orders()

        # Filter out admins from users count
        customers = {username: user for username, user in users.items() if not isinstance(user, Admin)}

        # Update dashboard counts
        self.users_count_label.config(text=str(len(customers)))
        self.tickets_count_label.config(text=str(len(tickets)))
        self.orders_count_label.config(text=str(len(orders)))

        # Calculate total revenue
        total_revenue = sum(order.get_total_amount() for order in orders.values())
        self.revenue_label.config(text=f"${total_revenue:.2f}")

        # Clear recent orders tree
        for item in self.recent_orders_tree.get_children():
            self.recent_orders_tree.delete(item)

        # Get recent orders (last 5)
        recent_orders = list(orders.values())
        recent_orders.sort(key=lambda o: o.get_order_date(), reverse=True)
        recent_orders = recent_orders[:5]

        # Add recent orders to tree
        for order in recent_orders:
            order_id = order.get_order_id()
            order_date = order.get_order_date().strftime("%d-%m-%Y")
            user_id = order.get_user_id()
            user = users.get(user_id, "Unknown")
            username = user.get_username() if hasattr(user, 'get_username') else "Unknown"
            order_status = order.get_status().value
            order_total = f"${order.get_total_amount():.2f}"

            self.recent_orders_tree.insert("", "end",
                                           values=(order_id, order_date, username, order_status, order_total))

    def refresh_users(self):
        # Reload data from disk first
        self.controller.booking_system.load_data()

        # Clear current tree
        for item in self.users_tree.get_children():
            self.users_tree.delete(item)

        # Get users from booking system
        users = self.controller.booking_system.get_all_users()

        # Add users to tree (exclude admins)
        for username, user in users.items():
            if not isinstance(user, Admin):
                user_id = user.get_user_id()
                email = user.get_email()
                phone = user.get_phone_number() or "N/A"
                orders_count = len(user.get_orders())

                self.users_tree.insert("", "end", values=(user_id, username, email, phone, orders_count))

    def refresh_tickets(self):
        # Reload data from disk first
        self.controller.booking_system.load_data()

        # Clear current tree
        for item in self.tickets_tree.get_children():
            self.tickets_tree.delete(item)

        # Get tickets from booking system
        tickets = self.controller.booking_system.get_all_tickets()

        # Add tickets to tree
        for ticket_id, ticket in tickets.items():
            ticket_type = "Season" if isinstance(ticket, SeasonTicket) else "Single Race"
            price = f"${ticket.calculate_price():.2f}"
            date = ticket.get_event_date().strftime("%d-%m-%Y")
            section = ticket.get_venue_section()
            used = "Yes" if ticket.is_used() else "No"

            self.tickets_tree.insert("", "end", values=(ticket_id, ticket_type, price, date, section, used))

    def refresh_orders(self):
        # Reload data from disk first
        self.controller.booking_system.load_data()

        # Clear current tree
        for item in self.orders_tree.get_children():
            self.orders_tree.delete(item)

        # Get orders from booking system
        orders = self.controller.booking_system.get_all_orders()
        users = self.controller.booking_system.get_all_users()

        # Add orders to tree
        for order_id, order in orders.items():
            order_date = order.get_order_date().strftime("%d-%m-%Y")
            user_id = order.get_user_id()
            user = users.get(user_id, "Unknown")
            username = user.get_username() if hasattr(user, 'get_username') else "Unknown"
            order_status = order.get_status().value

            payment_method = "Not specified"
            if order.get_payment_method():
                payment_method = order.get_payment_method().value

            order_total = f"${order.get_total_amount():.2f}"
            ticket_count = len(order.get_tickets())

            self.orders_tree.insert("", "end", values=(
            order_id, order_date, username, order_status, payment_method, order_total, ticket_count))

    def refresh_admins(self):
        # Reload data from disk first
        self.controller.booking_system.load_data()

        # Clear current tree
        for item in self.admins_tree.get_children():
            self.admins_tree.delete(item)

        # Get admins from booking system
        admins = self.controller.booking_system.get_all_admins()

        # Add admins to tree
        for username, admin in admins.items():
            admin_id = admin.get_user_id()
            email = admin.get_email()
            level = admin.get_admin_level()
            department = admin.get_department()
            phone = admin.get_phone_number() or "N/A"

            self.admins_tree.insert("", "end", values=(admin_id, username, email, level, department, phone))

    def view_recent_order_details(self, event):
        # Get selected item
        selected_item = self.recent_orders_tree.selection()

        if not selected_item:
            return

        # Get order ID from selected item
        order_id = self.recent_orders_tree.item(selected_item, "values")[0]

        # Use existing view_order_details method
        self.view_order_details_by_id(order_id)

    def view_order_details(self, event):
        # Get selected item
        selected_item = self.orders_tree.selection()

        if not selected_item:
            return

        # Get order ID from selected item
        order_id = self.orders_tree.item(selected_item, "values")[0]

        # View order details
        self.view_order_details_by_id(order_id)

    def view_order_details_by_id(self, order_id):
        # Reload data from disk first
        self.controller.booking_system.load_data()

        # Get order from booking system
        order = self.controller.booking_system.get_order(order_id)

        if not order:
            messagebox.showerror("Error", "Order not found")
            return

        # Create order details window
        details_window = tk.Toplevel(self)
        details_window.title(f"Order Details - {order_id}")
        details_window.geometry("700x600")
        details_window.configure(bg="#34495e")

        # Order details
        tk.Label(details_window, text=f"Order ID: {order.get_order_id()}", font=("Arial", 14, "bold"), bg="#34495e",
                 fg="#ecf0f1").pack(anchor="w", padx=20, pady=(20, 10))
        tk.Label(details_window, text=f"Date: {order.get_order_date().strftime('%d %B %Y')}", font=("Arial", 12),
                 bg="#34495e", fg="#ecf0f1").pack(anchor="w", padx=20, pady=2)
        tk.Label(details_window, text=f"Status: {order.get_status().value}", font=("Arial", 12), bg="#34495e",
                 fg="#ecf0f1").pack(anchor="w", padx=20, pady=2)

        user_id = order.get_user_id()
        user = self.controller.booking_system.get_user(user_id)

        # Enhanced customer information section
        customer_frame = tk.LabelFrame(details_window, text="Customer Information", font=("Arial", 12, "bold"),
                                       bg="#2c3e50", fg="#ecf0f1", padx=15, pady=15)
        customer_frame.pack(fill="x", padx=20, pady=10)

        if user:
            tk.Label(customer_frame, text=f"Username: {user.get_username()}", font=("Arial", 11), bg="#2c3e50",
                     fg="#ecf0f1").pack(anchor="w", pady=2)
            tk.Label(customer_frame, text=f"User ID: {user.get_user_id()}", font=("Arial", 11), bg="#2c3e50",
                     fg="#ecf0f1").pack(anchor="w", pady=2)
            tk.Label(customer_frame, text=f"Email: {user.get_email()}", font=("Arial", 11), bg="#2c3e50",
                     fg="#ecf0f1").pack(anchor="w", pady=2)
            tk.Label(customer_frame, text=f"Phone: {user.get_phone_number() or 'Not provided'}", font=("Arial", 11),
                     bg="#2c3e50", fg="#ecf0f1").pack(anchor="w", pady=2)
        else:
            tk.Label(customer_frame, text=f"Customer: {user_id} (User not found)", font=("Arial", 11), bg="#2c3e50",
                     fg="#ecf0f1").pack(anchor="w", pady=2)

        # Payment Information
        payment_frame = tk.LabelFrame(details_window, text="Payment Information", font=("Arial", 12, "bold"),
                                      bg="#2c3e50", fg="#ecf0f1", padx=15, pady=15)
        payment_frame.pack(fill="x", padx=20, pady=10)

        payment_method = "Not specified"
        if order.get_payment_method():
            payment_method = order.get_payment_method().value

        tk.Label(payment_frame, text=f"Payment Method: {payment_method}", font=("Arial", 11), bg="#2c3e50",
                 fg="#ecf0f1").pack(anchor="w", pady=2)
        tk.Label(payment_frame, text=f"Total Amount: ${order.get_total_amount():.2f}", font=("Arial", 11), bg="#2c3e50",
                 fg="#ecf0f1").pack(anchor="w", pady=2)

        # Tickets section
        tk.Label(details_window, text="Purchased Tickets:", font=("Arial", 14, "bold"), bg="#34495e",
                 fg="#ecf0f1").pack(anchor="w", padx=20, pady=(20, 10))

        # Create frame for tickets
        tickets_frame = tk.Frame(details_window, bg="#34495e")
        tickets_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Create TreeView for tickets
        columns = ("Ticket ID", "Type", "Price", "Date", "Section", "Details")
        tickets_tree = ttk.Treeview(tickets_frame, columns=columns, show="headings", height=10)

        # Define headings
        for col in columns:
            tickets_tree.heading(col, text=col)

        # Set column widths
        tickets_tree.column("Ticket ID", width=100)
        tickets_tree.column("Type", width=100)
        tickets_tree.column("Price", width=80)
        tickets_tree.column("Date", width=100)
        tickets_tree.column("Section", width=120)
        tickets_tree.column("Details", width=150)

        # Add scrollbar
        scrollbar = ttk.Scrollbar(tickets_frame, orient="vertical", command=tickets_tree.yview)
        tickets_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        tickets_tree.pack(fill="both", expand=True)

        # Add tickets to tree
        tickets = order.get_tickets()

        if not tickets:
            tickets_tree.insert("", "end", values=("No tickets found", "", "", "", "", ""))
        else:
            for ticket in tickets:
                ticket_id = ticket.get_ticket_id()
                ticket_type = "Season" if isinstance(ticket, SeasonTicket) else "Single Race"
                ticket_price = f"${ticket.calculate_price():.2f}"
                ticket_date = ticket.get_event_date().strftime("%d-%m-%Y")
                ticket_section = ticket.get_venue_section()

                # Get additional details based on ticket type
                if isinstance(ticket, SingleRaceTicket):
                    details = f"{ticket.get_race_name()} ({ticket.get_race_category().value})"
                elif isinstance(ticket, SeasonTicket):
                    details = f"{ticket.get_season_year()} Season ({len(ticket.get_included_races())} races)"
                else:
                    details = "Standard Ticket"

                tickets_tree.insert("", "end",
                                    values=(ticket_id, ticket_type, ticket_price, ticket_date, ticket_section, details))

        # Add double-click event to view detailed ticket info
        tickets_tree.bind("<Double-1>", lambda e: self.view_ticket_from_order(e, tickets_tree, tickets))

        # Status update frame
        status_frame = tk.Frame(details_window, bg="#34495e")
        status_frame.pack(fill="x", padx=20, pady=10)

        tk.Label(status_frame, text="Update Status:", font=("Arial", 12, "bold"), bg="#34495e", fg="#ecf0f1").pack(
            side=tk.LEFT)

        status_var = tk.StringVar(value=order.get_status().value)
        status_menu = ttk.Combobox(status_frame, textvariable=status_var,
                                   values=[status.value for status in OrderStatus],
                                   state="readonly", width=15)
        status_menu.pack(side=tk.LEFT, padx=10)

        # Update button
        update_button = tk.Button(status_frame, text="Update Status",
                                  command=lambda: self.update_order_status(order, status_var.get(), details_window),
                                  bg="#3498db", fg="gray", font=("Arial", 11), padx=10, pady=3)
        update_button.pack(side=tk.LEFT, padx=5)

        # Export order details
        export_button = tk.Button(details_window, text="Export Order Details",
                                  command=lambda: self.export_order_details(order),
                                  bg="#f39c12", fg="gray", font=("Arial", 11), padx=10, pady=3)
        export_button.pack(pady=10)

        # Close button
        close_button = tk.Button(details_window, text="Close", command=details_window.destroy,
                                 bg="#7f8c8d", fg="gray", font=("Arial", 12), padx=15, pady=5)
        close_button.pack(pady=10)

    def view_ticket_from_order(self, event, tree, tickets):
        # Get selected item
        selected_item = tree.selection()

        if not selected_item:
            return

        # Get ticket ID from selected item
        ticket_id = tree.item(selected_item, "values")[0]

        if ticket_id == "No tickets found":
            return

        # Find the ticket in the list
        selected_ticket = None
        for ticket in tickets:
            if ticket.get_ticket_id() == ticket_id:
                selected_ticket = ticket
                break

        if not selected_ticket:
            messagebox.showerror("Error", "Ticket not found")
            return

        # Create ticket details window
        details_window = tk.Toplevel()
        details_window.title(f"Ticket Details - {ticket_id}")
        details_window.geometry("500x450")
        details_window.configure(bg="#34495e")

        # Ticket details
        tk.Label(details_window, text=f"Ticket ID: {selected_ticket.get_ticket_id()}", font=("Arial", 14, "bold"),
                 bg="#34495e", fg="#ecf0f1").pack(anchor="w", padx=20, pady=(20, 10))
        tk.Label(details_window, text=f"Price: ${selected_ticket.get_price():.2f}", font=("Arial", 12), bg="#34495e",
                 fg="#ecf0f1").pack(anchor="w", padx=20, pady=2)
        tk.Label(details_window, text=f"Calculated Price: ${selected_ticket.calculate_price():.2f}", font=("Arial", 12),
                 bg="#34495e", fg="#ecf0f1").pack(anchor="w", padx=20, pady=2)
        tk.Label(details_window, text=f"Date: {selected_ticket.get_event_date().strftime('%d %B %Y')}",
                 font=("Arial", 12), bg="#34495e", fg="#ecf0f1").pack(anchor="w", padx=20, pady=2)
        tk.Label(details_window, text=f"Section: {selected_ticket.get_venue_section()}", font=("Arial", 12),
                 bg="#34495e", fg="#ecf0f1").pack(anchor="w", padx=20, pady=2)
        tk.Label(details_window, text=f"Used: {'Yes' if selected_ticket.is_used() else 'No'}", font=("Arial", 12),
                 bg="#34495e", fg="#ecf0f1").pack(anchor="w", padx=20, pady=2)

        # Type-specific details
        if isinstance(selected_ticket, SingleRaceTicket):
            tk.Label(details_window, text="Ticket Type: Single Race", font=("Arial", 12, "bold"), bg="#34495e",
                     fg="#ecf0f1").pack(anchor="w", padx=20, pady=(20, 10))
            tk.Label(details_window, text=f"Race Name: {selected_ticket.get_race_name()}", font=("Arial", 12),
                     bg="#34495e", fg="#ecf0f1").pack(anchor="w", padx=20, pady=2)
            tk.Label(details_window, text=f"Race Category: {selected_ticket.get_race_category().value}",
                     font=("Arial", 12), bg="#34495e", fg="#ecf0f1").pack(anchor="w", padx=20, pady=2)
        elif isinstance(selected_ticket, SeasonTicket):
            tk.Label(details_window, text="Ticket Type: Season", font=("Arial", 12, "bold"), bg="#34495e",
                     fg="#ecf0f1").pack(anchor="w", padx=20, pady=(20, 10))
            tk.Label(details_window, text=f"Season Year: {selected_ticket.get_season_year()}", font=("Arial", 12),
                     bg="#34495e", fg="#ecf0f1").pack(anchor="w", padx=20, pady=2)

            # Create a frame for included races
            races_frame = tk.Frame(details_window, bg="#34495e")
            races_frame.pack(fill="x", padx=20, pady=5)

            tk.Label(races_frame, text="Included Races:", font=("Arial", 12), bg="#34495e", fg="#ecf0f1").pack(
                anchor="w")

            races_text = tk.Text(races_frame, height=8, width=40, wrap="word", bg="#2c3e50", fg="#ecf0f1")
            races_text.pack(fill="x", pady=5)

            included_races = selected_ticket.get_included_races()
            races_text.insert("end", ", ".join(included_races) if included_races else "None")
            races_text.configure(state="disabled")  # Make read-only

        # Toggle used status button
        toggle_button = tk.Button(details_window, text="Toggle Used Status",
                                  command=lambda: self.toggle_ticket_used_status(selected_ticket, details_window),
                                  bg="#2980b9", fg="gray", font=("Arial", 11), padx=10, pady=3)
        toggle_button.pack(pady=10)

        # Close button
        close_button = tk.Button(details_window, text="Close", command=details_window.destroy,
                                 bg="#7f8c8d", fg="gray", font=("Arial", 12), padx=15, pady=5)
        close_button.pack(pady=10)

    def toggle_ticket_used_status(self, ticket, window=None):
        """Toggle the used status of a ticket"""
        try:
            # Toggle used status
            current_status = ticket.is_used()
            ticket.set_used(not current_status)

            # Save changes
            self.controller.booking_system.save_data()

            new_status = "Used" if ticket.is_used() else "Unused"
            messagebox.showinfo("Success", f"Ticket status updated to {new_status}")

            # Close window if provided
            if window:
                window.destroy()

            # Refresh ticket lists
            self.refresh_tickets()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to update ticket status: {str(e)}")

    def update_order_status(self, order, new_status_value, window=None):
        # Map status string to enum
        status_map = {status.value: status for status in OrderStatus}
        new_status = status_map.get(new_status_value)

        if not new_status:
            messagebox.showerror("Error", "Invalid status")
            return

        # Update order status
        try:
            if new_status == OrderStatus.CONFIRMED:
                # Confirm the order
                if not order.confirm_order():
                    messagebox.showerror("Error", "Cannot confirm order. Ensure all requirements are met.")
                    return
            elif new_status == OrderStatus.CANCELLED:
                # Cancel the order
                if not order.cancel_order():
                    messagebox.showerror("Error",
                                         "Cannot cancel order. Some tickets may be used or events may have passed.")
                    return
            else:
                # Set status directly
                order.set_status(new_status)

            # Update the order in the system
            self.controller.booking_system.update_order(order)

            messagebox.showinfo("Success", f"Order status updated to {new_status.value}")

            # Close the window if provided
            if window:
                window.destroy()

            # Refresh order lists
            self.refresh_orders()
            self.refresh_dashboard()

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def view_user_details(self, event):
        # Reload data from disk first
        self.controller.booking_system.load_data()

        # Get selected item
        selected_item = self.users_tree.selection()

        if not selected_item:
            return

        # Get username from selected item
        username = self.users_tree.item(selected_item, "values")[1]

        # Get user from booking system
        user = self.controller.booking_system.get_user(username)

        if not user:
            messagebox.showerror("Error", "User not found")
            return

        # Create user details window
        details_window = tk.Toplevel(self)
        details_window.title(f"User Details - {username}")
        details_window.geometry("700x600")
        details_window.configure(bg="#34495e")

        # User details
        tk.Label(details_window, text=f"User ID: {user.get_user_id()}", font=("Arial", 14, "bold"), bg="#34495e",
                 fg="#ecf0f1").pack(anchor="w", padx=20, pady=(20, 10))
        tk.Label(details_window, text=f"Username: {user.get_username()}", font=("Arial", 12), bg="#34495e",
                 fg="#ecf0f1").pack(anchor="w", padx=20, pady=2)
        tk.Label(details_window, text=f"Email: {user.get_email()}", font=("Arial", 12), bg="#34495e",
                 fg="#ecf0f1").pack(anchor="w", padx=20, pady=2)
        tk.Label(details_window, text=f"Phone: {user.get_phone_number() or 'Not provided'}", font=("Arial", 12),
                 bg="#34495e", fg="#ecf0f1").pack(anchor="w", padx=20, pady=2)

        # Purchase Summary frame
        purchase_summary_frame = tk.LabelFrame(details_window, text="Purchase Summary", font=("Arial", 12, "bold"),
                                               bg="#2c3e50", fg="#ecf0f1", padx=15, pady=15)
        purchase_summary_frame.pack(fill="x", padx=20, pady=10)

        # Get user's orders
        orders = user.get_orders()
        total_orders = len(orders)

        # Calculate total spent and tickets
        total_spent = sum(order.get_total_amount() for order in orders)
        total_tickets = sum(len(order.get_tickets()) for order in orders)

        # Display summary
        tk.Label(purchase_summary_frame, text=f"Total Orders: {total_orders}", font=("Arial", 11), bg="#2c3e50",
                 fg="#ecf0f1").pack(anchor="w", pady=2)
        tk.Label(purchase_summary_frame, text=f"Total Tickets Purchased: {total_tickets}", font=("Arial", 11),
                 bg="#2c3e50", fg="#ecf0f1").pack(anchor="w", pady=2)
        tk.Label(purchase_summary_frame, text=f"Total Amount Spent: ${total_spent:.2f}", font=("Arial", 11),
                 bg="#2c3e50", fg="#ecf0f1").pack(anchor="w", pady=2)

        # Orders section
        tk.Label(details_window, text="Orders:", font=("Arial", 14, "bold"), bg="#34495e", fg="#ecf0f1").pack(
            anchor="w", padx=20, pady=(20, 10))

        # Create frame for orders
        orders_frame = tk.Frame(details_window, bg="#34495e")
        orders_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Create TreeView for orders
        columns = ("Order ID", "Date", "Status", "Total", "Tickets")
        orders_tree = ttk.Treeview(orders_frame, columns=columns, show="headings", height=10)

        # Define headings
        for col in columns:
            orders_tree.heading(col, text=col)

        # Set column widths
        orders_tree.column("Order ID", width=100)
        orders_tree.column("Date", width=100)
        orders_tree.column("Status", width=100)
        orders_tree.column("Total", width=100)
        orders_tree.column("Tickets", width=80)

        # Add scrollbar
        scrollbar = ttk.Scrollbar(orders_frame, orient="vertical", command=orders_tree.yview)
        orders_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        orders_tree.pack(fill="both", expand=True)

        # Add orders to tree
        orders = user.get_orders()

        if not orders:
            orders_tree.insert("", "end", values=("No orders found", "", "", "", ""))
        else:
            for order in orders:
                order_id = order.get_order_id()
                order_date = order.get_order_date().strftime("%d-%m-%Y")
                order_status = order.get_status().value
                order_total = f"${order.get_total_amount():.2f}"
                ticket_count = len(order.get_tickets())

                orders_tree.insert("", "end", values=(order_id, order_date, order_status, order_total, ticket_count))

        # Add Double-click event to view order details
        orders_tree.bind("<Double-1>", lambda e: self.view_order_from_user(e, orders_tree, orders))

        # Button frame
        button_frame = tk.Frame(details_window, bg="#34495e")
        button_frame.pack(fill="x", padx=20, pady=10)

        # Export user data button
        export_button = tk.Button(button_frame, text="Export User Data",
                                  command=lambda: self.export_user_data(user),
                                  bg="#f39c12", fg="gray", font=("Arial", 11), padx=10, pady=3)
        export_button.pack(side=tk.LEFT, padx=5)

        # Close button
        close_button = tk.Button(details_window, text="Close", command=details_window.destroy,
                                 bg="#7f8c8d", fg="gray", font=("Arial", 12), padx=15, pady=5)
        close_button.pack(side=tk.RIGHT, padx=20, pady=20)

    def view_order_from_user(self, event, tree, orders):
        # Get selected item
        selected_item = tree.selection()

        if not selected_item:
            return

        # Get order ID from selected item
        order_id = tree.item(selected_item, "values")[0]

        if order_id == "No orders found":
            return

        # Find the order in the list
        selected_order = None
        for order in orders:
            if order.get_order_id() == order_id:
                selected_order = order
                break

        if not selected_order:
            messagebox.showerror("Error", "Order not found")
            return

        # View order details
        self.view_order_details_by_id(order_id)

    def view_ticket_details(self, event):
        # Reload data from disk first
        self.controller.booking_system.load_data()

        # Get selected item
        selected_item = self.tickets_tree.selection()

        if not selected_item:
            return

        # Get ticket ID from selected item
        ticket_id = self.tickets_tree.item(selected_item, "values")[0]

        # Get ticket from booking system
        ticket = self.controller.booking_system.get_ticket(ticket_id)

        if not ticket:
            messagebox.showerror("Error", "Ticket not found")
            return

        # Create ticket details window
        details_window = tk.Toplevel(self)
        details_window.title(f"Ticket Details - {ticket_id}")
        details_window.geometry("500x450")
        details_window.configure(bg="#34495e")

        # Ticket details
        tk.Label(details_window, text=f"Ticket ID: {ticket.get_ticket_id()}", font=("Arial", 14, "bold"), bg="#34495e",
                 fg="#ecf0f1").pack(anchor="w", padx=20, pady=(20, 10))
        tk.Label(details_window, text=f"Price: ${ticket.get_price():.2f}", font=("Arial", 12), bg="#34495e",
                 fg="#ecf0f1").pack(anchor="w", padx=20, pady=2)
        tk.Label(details_window, text=f"Calculated Price: ${ticket.calculate_price():.2f}", font=("Arial", 12),
                 bg="#34495e", fg="#ecf0f1").pack(anchor="w", padx=20, pady=2)
        tk.Label(details_window, text=f"Date: {ticket.get_event_date().strftime('%d %B %Y')}", font=("Arial", 12),
                 bg="#34495e", fg="#ecf0f1").pack(anchor="w", padx=20, pady=2)
        tk.Label(details_window, text=f"Section: {ticket.get_venue_section()}", font=("Arial", 12), bg="#34495e",
                 fg="#ecf0f1").pack(anchor="w", padx=20, pady=2)
        tk.Label(details_window, text=f"Used: {'Yes' if ticket.is_used() else 'No'}", font=("Arial", 12), bg="#34495e",
                 fg="#ecf0f1").pack(anchor="w", padx=20, pady=2)

        # Type-specific details
        if isinstance(ticket, SingleRaceTicket):
            tk.Label(details_window, text="Ticket Type: Single Race", font=("Arial", 12, "bold"), bg="#34495e",
                     fg="#ecf0f1").pack(anchor="w", padx=20, pady=(20, 10))
            tk.Label(details_window, text=f"Race Name: {ticket.get_race_name()}", font=("Arial", 12), bg="#34495e",
                     fg="#ecf0f1").pack(anchor="w", padx=20, pady=2)
            tk.Label(details_window, text=f"Race Category: {ticket.get_race_category().value}", font=("Arial", 12),
                     bg="#34495e", fg="#ecf0f1").pack(anchor="w", padx=20, pady=2)
        elif isinstance(ticket, SeasonTicket):
            tk.Label(details_window, text="Ticket Type: Season", font=("Arial", 12, "bold"), bg="#34495e",
                     fg="#ecf0f1").pack(anchor="w", padx=20, pady=(20, 10))
            tk.Label(details_window, text=f"Season Year: {ticket.get_season_year()}", font=("Arial", 12), bg="#34495e",
                     fg="#ecf0f1").pack(anchor="w", padx=20, pady=2)

            # Create a frame for included races
            races_frame = tk.Frame(details_window, bg="#34495e")
            races_frame.pack(fill="x", padx=20, pady=5)

            tk.Label(races_frame, text="Included Races:", font=("Arial", 12), bg="#34495e", fg="#ecf0f1").pack(
                anchor="w")

            races_text = tk.Text(races_frame, height=8, width=40, wrap="word", bg="#2c3e50", fg="#ecf0f1")
            races_text.pack(fill="x", pady=5)

            included_races = ticket.get_included_races()
            races_text.insert("end", ", ".join(included_races) if included_races else "None")
            races_text.configure(state="disabled")  # Make read-only

        # Toggle used status button
        toggle_button = tk.Button(details_window, text="Toggle Used Status",
                                  command=lambda: self.toggle_ticket_used_status(ticket, details_window),
                                  bg="#2980b9", fg="gray", font=("Arial", 11), padx=10, pady=3)
        toggle_button.pack(pady=10)

        # Close button
        close_button = tk.Button(details_window, text="Close", command=details_window.destroy,
                                 bg="#7f8c8d", fg="gray", font=("Arial", 12), padx=15, pady=5)
        close_button.pack(pady=10)

    def add_admin(self):
        # Create add admin window
        add_window = tk.Toplevel(self)
        add_window.title("Add New Admin")
        add_window.geometry("400x450")
        add_window.configure(bg="#34495e")

        # Title
        tk.Label(add_window, text="Add New Admin", font=("Arial", 16, "bold"), bg="#34495e", fg="#ecf0f1").pack(pady=20)

        # Create form frame
        form_frame = tk.Frame(add_window, bg="#34495e", padx=20, pady=10)
        form_frame.pack(fill="x")

        # Username
        tk.Label(form_frame, text="Username:", font=("Arial", 12), bg="#000000", fg="#ecf0f1").grid(row=0, column=0,
                                                                                                    sticky="w", pady=5)
        username_var = tk.StringVar()
        username_entry = tk.Entry(form_frame, textvariable=username_var, font=("Arial", 12), width=25, bg="#000000")
        username_entry.grid(row=0, column=1, sticky="w", pady=5)

        # Password
        tk.Label(form_frame, text="Password:", font=("Arial", 12), bg="#000000", fg="#ecf0f1").grid(row=1, column=0,
                                                                                                    sticky="w", pady=5)
        password_var = tk.StringVar()
        password_entry = tk.Entry(form_frame, textvariable=password_var, show="*", font=("Arial", 12), width=25,
                                  bg="#000000")
        password_entry.grid(row=1, column=1, sticky="w", pady=5)

        # Email
        tk.Label(form_frame, text="Email:", font=("Arial", 12), bg="#000000", fg="#ecf0f1").grid(row=2, column=0,
                                                                                                 sticky="w", pady=5)
        email_var = tk.StringVar()
        email_entry = tk.Entry(form_frame, textvariable=email_var, font=("Arial", 12), width=25, bg="#000000")
        email_entry.grid(row=2, column=1, sticky="w", pady=5)

        # Phone
        tk.Label(form_frame, text="Phone (optional):", font=("Arial", 12), bg="#000000", fg="#ecf0f1").grid(row=3,
                                                                                                            column=0,
                                                                                                            sticky="w",
                                                                                                            pady=5)
        phone_var = tk.StringVar()
        phone_entry = tk.Entry(form_frame, textvariable=phone_var, font=("Arial", 12), width=25, bg="#000000")
        phone_entry.grid(row=3, column=1, sticky="w", pady=5)

        # Admin Level
        tk.Label(form_frame, text="Admin Level (1-3):", font=("Arial", 12), bg="#000000", fg="#ecf0f1").grid(row=4,
                                                                                                             column=0,
                                                                                                             sticky="w",
                                                                                                             pady=5)
        level_var = tk.IntVar(value=1)
        level_spinbox = tk.Spinbox(form_frame, from_=1, to=3, textvariable=level_var, font=("Arial", 12), width=5,
                                   bg="#000000")
        level_spinbox.grid(row=4, column=1, sticky="w", pady=5)

        # Department
        tk.Label(form_frame, text="Department:", font=("Arial", 12), bg="#000000", fg="#ecf0f1").grid(row=5, column=0,
                                                                                                      sticky="w",
                                                                                                      pady=5)
        department_var = tk.StringVar()
        department_var.set("Ticket Sales")
        department_menu = ttk.Combobox(form_frame, textvariable=department_var,
                                       values=["Ticket Sales", "Customer Support", "System Administration",
                                               "Event Management"],
                                       state="readonly", width=20)
        department_menu.grid(row=5, column=1, sticky="w", pady=5)

        # Button frame
        button_frame = tk.Frame(add_window, bg="#34495e")
        button_frame.pack(fill="x", pady=20)

        # Create button
        def create_admin():
            # Get form values
            username = username_var.get()
            password = password_var.get()
            email = email_var.get()
            phone = phone_var.get() if phone_var.get() else None
            level = level_var.get()
            department = department_var.get()

            # Validate input
            if not username or not password or not email or not department:
                messagebox.showerror("Error", "Username, password, email, and department are required")
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
                # Generate admin ID
                admin_id = f"ADM-{random.randint(1000, 9999)}"

                # Create new admin
                self.controller.booking_system.create_admin(admin_id, username, password, email, level, department,
                                                            phone)

                messagebox.showinfo("Success", "Admin account created successfully")

                # Close window
                add_window.destroy()

                # Refresh admin list
                self.refresh_admins()

            except Exception as e:
                messagebox.showerror("Error", f"An error occurred: {str(e)}")

        create_button = tk.Button(button_frame, text="Create Admin", command=create_admin,
                                  bg="#e74c3c", fg="gray", font=("Arial", 12, "bold"), padx=15, pady=5)
        create_button.pack(side=tk.LEFT, padx=10)

        # Cancel button
        cancel_button = tk.Button(button_frame, text="Cancel", command=add_window.destroy,
                                  bg="#7f8c8d", fg="gray", font=("Arial", 12), padx=15, pady=5)
        cancel_button.pack(side=tk.LEFT, padx=10)

    def export_order_details(self, order):
        """Export order details to a text file"""
        try:
            # Get user info
            user_id = order.get_user_id()
            user = self.controller.booking_system.get_user(user_id)
            username = user.get_username() if user else "Unknown"

            # Create filename with order ID
            filename = f"Order_{order.get_order_id()}_Details.txt"

            with open(filename, "w") as file:
                # Write header
                file.write("===== GRAND PRIX EXPERIENCE - ORDER DETAILS =====\n\n")

                # Order info
                file.write(f"Order ID: {order.get_order_id()}\n")
                file.write(f"Date: {order.get_order_date().strftime('%d %B %Y')}\n")
                file.write(f"Status: {order.get_status().value}\n\n")

                # Customer info
                file.write("CUSTOMER INFORMATION:\n")
                file.write(f"Username: {username}\n")
                if user:
                    file.write(f"User ID: {user.get_user_id()}\n")
                    file.write(f"Email: {user.get_email()}\n")
                    file.write(f"Phone: {user.get_phone_number() or 'Not provided'}\n\n")

                # Payment info
                file.write("PAYMENT INFORMATION:\n")
                payment_method = "Not specified"
                if order.get_payment_method():
                    payment_method = order.get_payment_method().value
                file.write(f"Payment Method: {payment_method}\n")
                file.write(f"Total Amount: ${order.get_total_amount():.2f}\n\n")

                # Tickets
                file.write("TICKETS PURCHASED:\n")
                tickets = order.get_tickets()

                if not tickets:
                    file.write("No tickets in this order.\n")
                else:
                    for i, ticket in enumerate(tickets):
                        file.write(f"\nTicket {i + 1}:\n")
                        file.write(f"  ID: {ticket.get_ticket_id()}\n")
                        ticket_type = "Season" if isinstance(ticket, SeasonTicket) else "Single Race"
                        file.write(f"  Type: {ticket_type}\n")
                        file.write(f"  Price: ${ticket.calculate_price():.2f}\n")
                        file.write(f"  Date: {ticket.get_event_date().strftime('%d %B %Y')}\n")
                        file.write(f"  Section: {ticket.get_venue_section()}\n")
                        file.write(f"  Used: {'Yes' if ticket.is_used() else 'No'}\n")

                        # Type-specific details
                        if isinstance(ticket, SingleRaceTicket):
                            file.write(f"  Race: {ticket.get_race_name()}\n")
                            file.write(f"  Category: {ticket.get_race_category().value}\n")
                        elif isinstance(ticket, SeasonTicket):
                            file.write(f"  Season Year: {ticket.get_season_year()}\n")
                            included_races = ticket.get_included_races()
                            file.write(f"  Races: {', '.join(included_races) if included_races else 'None'}\n")

                # Footer
                file.write("\n===== END OF ORDER DETAILS =====\n")
                file.write(f"Generated: {datetime.now().strftime('%d %B %Y %H:%M:%S')}")

            messagebox.showinfo("Export Successful", f"Order details exported to {filename}")

        except Exception as e:
            messagebox.showerror("Export Failed", f"Failed to export order details: {str(e)}")

    def export_user_data(self, user):
        """Export user data to a text file"""
        try:
            # Create filename with username
            filename = f"User_{user.get_username()}_Data.txt"

            with open(filename, "w") as file:
                # Write header
                file.write("===== GRAND PRIX EXPERIENCE - USER DATA =====\n\n")

                # User info
                file.write("USER INFORMATION:\n")
                file.write(f"User ID: {user.get_user_id()}\n")
                file.write(f"Username: {user.get_username()}\n")
                file.write(f"Email: {user.get_email()}\n")
                file.write(f"Phone: {user.get_phone_number() or 'Not provided'}\n\n")

                # Get user's orders
                orders = user.get_orders()

                # Purchase summary
                file.write("PURCHASE SUMMARY:\n")
                total_orders = len(orders)
                total_spent = sum(order.get_total_amount() for order in orders)
                total_tickets = sum(len(order.get_tickets()) for order in orders)

                file.write(f"Total Orders: {total_orders}\n")
                file.write(f"Total Tickets Purchased: {total_tickets}\n")
                file.write(f"Total Amount Spent: ${total_spent:.2f}\n\n")

                # Orders detail
                file.write("ORDERS HISTORY:\n")

                if not orders:
                    file.write("No orders found for this user.\n")
                else:
                    for i, order in enumerate(orders):
                        file.write(f"\nOrder {i + 1}:\n")
                        file.write(f"  Order ID: {order.get_order_id()}\n")
                        file.write(f"  Date: {order.get_order_date().strftime('%d %B %Y')}\n")
                        file.write(f"  Status: {order.get_status().value}\n")

                        payment_method = "Not specified"
                        if order.get_payment_method():
                            payment_method = order.get_payment_method().value
                        file.write(f"  Payment Method: {payment_method}\n")
                        file.write(f"  Total Amount: ${order.get_total_amount():.2f}\n")

                        # Tickets in order
                        tickets = order.get_tickets()
                        file.write(f"  Tickets in Order: {len(tickets)}\n")

                        for j, ticket in enumerate(tickets):
                            file.write(f"    Ticket {j + 1}: {ticket.get_ticket_id()} - ")

                            if isinstance(ticket, SingleRaceTicket):
                                file.write(f"{ticket.get_race_name()} ({ticket.get_race_category().value})\n")
                            elif isinstance(ticket, SeasonTicket):
                                file.write(
                                    f"Season {ticket.get_season_year()} ({len(ticket.get_included_races())} races)\n")
                            else:
                                file.write(f"Standard Ticket\n")

                # Footer
                file.write("\n===== END OF USER DATA =====\n")
                file.write(f"Generated: {datetime.now().strftime('%d %B %Y %H:%M:%S')}")

            messagebox.showinfo("Export Successful", f"User data exported to {filename}")

        except Exception as e:
            messagebox.showerror("Export Failed", f"Failed to export user data: {str(e)}")

    def export_users_data(self):
        """Export all users data to a text file"""
        try:
            # Create filename
            filename = f"All_Users_Data.txt"

            # Get all users
            users = self.controller.booking_system.get_all_users()

            # Filter out admins
            customers = {username: user for username, user in users.items() if not isinstance(user, Admin)}

            with open(filename, "w") as file:
                # Write header
                file.write("===== GRAND PRIX EXPERIENCE - ALL USERS DATA =====\n\n")

                file.write(f"Total Users: {len(customers)}\n\n")

                # Write user info for each user
                for i, (username, user) in enumerate(customers.items()):
                    file.write(f"USER {i + 1}:\n")
                    file.write(f"User ID: {user.get_user_id()}\n")
                    file.write(f"Username: {username}\n")
                    file.write(f"Email: {user.get_email()}\n")
                    file.write(f"Phone: {user.get_phone_number() or 'Not provided'}\n")

                    # Get user's orders
                    orders = user.get_orders()

                    # Purchase summary
                    total_orders = len(orders)
                    total_spent = sum(order.get_total_amount() for order in orders)
                    total_tickets = sum(len(order.get_tickets()) for order in orders)

                    file.write(f"Total Orders: {total_orders}\n")
                    file.write(f"Total Tickets: {total_tickets}\n")
                    file.write(f"Total Spent: ${total_spent:.2f}\n\n")

                # Footer
                file.write("\n===== END OF ALL USERS DATA =====\n")
                file.write(f"Generated: {datetime.now().strftime('%d %B %Y %H:%M:%S')}")

            messagebox.showinfo("Export Successful", f"All users data exported to {filename}")

        except Exception as e:
            messagebox.showerror("Export Failed", f"Failed to export users data: {str(e)}")

    def search_users(self, search_text):
        """Search users by username, email, or ID"""
        if not search_text:
            self.refresh_users()
            return

        # Clear current tree
        for item in self.users_tree.get_children():
            self.users_tree.delete(item)

        # Get users from booking system
        users = self.controller.booking_system.get_all_users()

        # Filter users based on search text
        search_text = search_text.lower()

        # Add filtered users to tree (exclude admins)
        for username, user in users.items():
            if not isinstance(user, Admin) and (
                    search_text in username.lower() or
                    search_text in user.get_email().lower() or
                    search_text in user.get_user_id().lower() or
                    (user.get_phone_number() and search_text in user.get_phone_number().lower())
            ):
                user_id = user.get_user_id()
                email = user.get_email()
                phone = user.get_phone_number() or "N/A"
                orders_count = len(user.get_orders())

                self.users_tree.insert("", "end", values=(user_id, username, email, phone, orders_count))

    def logout(self):
        # Reset user
        self.controller.current_user = None

        # Go back to login page
        self.controller.show_frame(AdminLoginPage)


class AdminApp(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)

        # Set window title and size
        self.title("Grand Prix Admin Portal")
        self.geometry("1000x700")
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
        for F in (AdminLoginPage, AdminRegisterPage, AdminDashboard):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        # Show login page first
        self.show_frame(AdminLoginPage)

        # Set up auto-refresh timer (refresh data every 5 seconds)
        self.setup_auto_refresh()

    def setup_auto_refresh(self):
        """Set up a timer to periodically reload data from disk"""
        # Only refresh data when on dashboard
        if self.current_user and isinstance(self.current_user, Admin):
            # Reload data from disk
            self.booking_system.load_data()

            # Refresh dashboard if visible
            if hasattr(self, "frames") and AdminDashboard in self.frames:
                current_frame = list(self.frames.keys())[
                    list(self.frames.values()).index(self.winfo_children()[0].winfo_children()[0])]
                if current_frame == AdminDashboard:
                    self.frames[AdminDashboard].refresh_dashboard()
                    self.frames[AdminDashboard].refresh_users()
                    self.frames[AdminDashboard].refresh_orders()
                    self.frames[AdminDashboard].refresh_tickets()

        # Schedule next refresh
        self.after(5000, self.setup_auto_refresh)

    def show_frame(self, cont):
        # Reload data from disk first
        self.booking_system.load_data()

        # Raise the selected frame
        frame = self.frames[cont]
        frame.tkraise()

        # If showing dashboard, refresh it
        if cont == AdminDashboard and self.current_user:
            self.frames[AdminDashboard].refresh_dashboard()
            self.frames[AdminDashboard].refresh_users()
            self.frames[AdminDashboard].refresh_tickets()
            self.frames[AdminDashboard].refresh_orders()
            self.frames[AdminDashboard].refresh_admins()


# Run the application
if __name__ == "__main__":
    app = AdminApp()
    app.mainloop()