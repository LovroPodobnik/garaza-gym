#!/usr/bin/env python3
"""
Improved mock implementation of Cardskipper to IVMS integration.
This script uses a more accurate representation of Cardskipper data format.
"""

import json
import xml.etree.ElementTree as ET
import sqlite3
import logging
import time
from datetime import datetime, timedelta
import os
import random
import string

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("mock_integration_improved.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("ImprovedMockIntegration")

# Path for mock data
MOCK_DATA_DIR = "mock_data"
if not os.path.exists(MOCK_DATA_DIR):
    os.makedirs(MOCK_DATA_DIR)

# Mock Cardskipper data
CARDSKIPPER_MEMBERS_FILE = os.path.join(MOCK_DATA_DIR, "cardskipper_members_improved.json")
# Mock IVMS data
IVMS_USERS_FILE = os.path.join(MOCK_DATA_DIR, "ivms_users_improved.json")
# SQLite database for integration
DB_FILE = os.path.join(MOCK_DATA_DIR, "integration_improved.db")

class MockDatabase:
    """Database manager for the integration."""
    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        self.initialize_db()
    
    def initialize_db(self):
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()
            
            # Create members table if it doesn't exist
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS members (
                    email TEXT PRIMARY KEY,
                    organization_member_id TEXT,
                    start_date TEXT,
                    end_date TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    ivms_user_id TEXT,
                    member_code TEXT,
                    role_id TEXT,
                    role_name TEXT
                )
            ''')
            self.conn.commit()
            
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            raise
    
    def close(self):
        if self.conn:
            self.conn.close()
    
    def get_all_members(self):
        try:
            self.cursor.execute("SELECT email, organization_member_id, start_date, end_date, first_name, last_name, ivms_user_id, member_code, role_id, role_name FROM members")
            rows = self.cursor.fetchall()
            
            members = {}
            for row in rows:
                email, org_member_id, start_date, end_date, first_name, last_name, ivms_user_id, member_code, role_id, role_name = row
                members[email] = {
                    "email": email,
                    "organization_member_id": org_member_id,
                    "start_date": start_date,
                    "end_date": end_date,
                    "first_name": first_name,
                    "last_name": last_name,
                    "ivms_user_id": ivms_user_id,
                    "member_code": member_code,
                    "role_id": role_id,
                    "role_name": role_name
                }
            
            return members
        except Exception as e:
            logger.error(f"Error getting members from database: {e}")
            return {}
    
    def update_member(self, member, ivms_user_id=None):
        try:
            # Extract values from the member dict
            email = member["email"]
            org_member_id = member["organization_member_id"]
            start_date = member["start_date"]
            end_date = member["end_date"]
            first_name = member["first_name"]
            last_name = member["last_name"]
            member_code = member.get("member_code", "")
            role_id = member.get("role_id", "")
            role_name = member.get("role_name", "")
            
            # Check if the member exists
            self.cursor.execute("SELECT email FROM members WHERE email = ?", (email,))
            existing_member = self.cursor.fetchone()
            
            if existing_member:
                # Update existing member
                if ivms_user_id:
                    self.cursor.execute("""
                        UPDATE members 
                        SET organization_member_id = ?, start_date = ?, end_date = ?, 
                            first_name = ?, last_name = ?, ivms_user_id = ?,
                            member_code = ?, role_id = ?, role_name = ?
                        WHERE email = ?
                    """, (
                        org_member_id, 
                        start_date, 
                        end_date,
                        first_name,
                        last_name,
                        ivms_user_id,
                        member_code,
                        role_id,
                        role_name,
                        email
                    ))
                else:
                    self.cursor.execute("""
                        UPDATE members 
                        SET organization_member_id = ?, start_date = ?, end_date = ?, 
                            first_name = ?, last_name = ?,
                            member_code = ?, role_id = ?, role_name = ?
                        WHERE email = ?
                    """, (
                        org_member_id, 
                        start_date, 
                        end_date,
                        first_name,
                        last_name,
                        member_code,
                        role_id,
                        role_name,
                        email
                    ))
            else:
                # Insert new member
                self.cursor.execute("""
                    INSERT INTO members (
                        email, organization_member_id, start_date, end_date,
                        first_name, last_name, ivms_user_id, member_code, role_id, role_name
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    email, 
                    org_member_id, 
                    start_date, 
                    end_date,
                    first_name,
                    last_name,
                    ivms_user_id,
                    member_code,
                    role_id,
                    role_name
                ))
            
            self.conn.commit()
            logger.info(f"Updated member in database: {email}")
        except Exception as e:
            logger.error(f"Error updating member in database: {e}")
            self.conn.rollback()
    
    def get_ivms_user_id(self, email):
        try:
            self.cursor.execute("SELECT ivms_user_id FROM members WHERE email = ?", (email,))
            result = self.cursor.fetchone()
            return result[0] if result and result[0] else None
        except Exception as e:
            logger.error(f"Error getting IVMS user ID for {email}: {e}")
            return None


class MockCardskipper:
    """Mock Cardskipper API with sample data."""
    def __init__(self, data_file):
        self.data_file = data_file
        self.load_or_create_data()
    
    def load_or_create_data(self):
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r') as f:
                data = json.load(f)
                self.members = data.get("members", [])
        else:
            # Create mock data
            self.members = self.generate_mock_members()
            with open(self.data_file, 'w') as f:
                json.dump({"members": self.members}, f, indent=2)
    
    def save_data(self):
        with open(self.data_file, 'w') as f:
            json.dump({"members": self.members}, f, indent=2)
    
    def generate_random_member_code(self, length=6):
        """Generate a random member code."""
        chars = string.ascii_lowercase + string.digits
        return ''.join(random.choice(chars) for _ in range(length))
    
    def generate_mock_members(self):
        """Generate mock membership data."""
        members = []
        
        # Sample Slovenian last names
        last_names = [
            "Novak", "Kovačič", "Horvat", "Krajnc", "Zupančič", 
            "Potočnik", "Kovač", "Mlakar", "Vidmar", "Golob",
            "Kos", "Jerič", "Kralj", "Pavlič", "Šuštar",
            "Kobal", "Černe", "Kolar", "Turk", "Zupan"
        ]
        
        # Sample Slovenian first names
        first_names = [
            "Luka", "Marko", "Jan", "Matej", "Andrej",
            "Nina", "Eva", "Maja", "Ana", "Sara",
            "Nejc", "Žiga", "Rok", "Jure", "Matevž",
            "Anja", "Tina", "Katja", "Petra", "Urška"
        ]
        
        # Role definitions
        roles = [
            {"Id": 456, "Name": "Dijak 16-17", "Type": "Student", "OrganisationUnit": "Youth"},
            {"Id": 457, "Name": "24/7", "Type": "Regular", "OrganisationUnit": "Adult"},
            {"Id": 458, "Name": "OG - stari član", "Type": "Regular", "OrganisationUnit": "Adult"},
            {"Id": 459, "Name": "Mesečna", "Type": "Regular", "OrganisationUnit": "Adult"},
            {"Id": 460, "Name": "Študent", "Type": "Student", "OrganisationUnit": "Adult"}
        ]
        
        # Create 20 mock members
        for i in range(1, 21):
            # Generate a unique ID for the member
            org_member_id = str(1000 + i)
            
            # Select a random name
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            
            # Generate random birthdate
            year = random.randint(1980, 2008)
            month = random.randint(1, 12)
            day = random.randint(1, 28)
            birthdate = f"{year}-{month:02d}-{day:02d}T00:00:00"
            
            # Generate a random member code
            member_code = self.generate_random_member_code()
            
            # Create contact info
            email = f"{first_name.lower()}.{last_name.lower()}@example.com"
            phone = f"+3867{random.randint(1000000, 9999999)}"
            
            # Select a random role
            role = random.choice(roles)
            
            # Generate dates based on role
            if role["Type"] == "Student":
                # Student memberships might be aligned with school year
                start_date = f"2024-09-01T00:00:00"
                end_date = f"2025-06-30T23:59:59"
            else:
                # Regular memberships have different durations
                start_month = random.randint(1, 12)
                start_day = random.randint(1, 28)
                start_date = f"2024-{start_month:02d}-{start_day:02d}T00:00:00"
                
                # End date is typically 1 month, 3 months, or 12 months after start date
                duration = random.choice([1, 3, 12])
                end_month = start_month + duration
                end_year = 2024
                
                if end_month > 12:
                    end_month = end_month - 12
                    end_year = 2025
                    
                end_date = f"{end_year}-{end_month:02d}-{start_day:02d}T23:59:59"
            
            # Create the member object using the structure from the real data
            member = {
                "OrganisationMemberId": org_member_id,
                "Firstname": first_name,
                "Lastname": last_name,
                "Birthdate": birthdate,
                "MemberCode": member_code,
                "ContactInfo": {
                    "EMail": email,
                    "CellPhone1": phone
                },
                "Organisations": {
                    "Organisation": {
                        "Id": 123,  # Using fixed org ID for simplicity
                        "Roles": {
                            "Role": {
                                "Id": role["Id"],
                                "Name": role["Name"],
                                "StartDate": start_date,
                                "EndDate": end_date,
                                "Type": role["Type"],
                                "OrganisationUnit": role["OrganisationUnit"]
                            }
                        }
                    }
                }
            }
            
            # Add extra fields for some members
            if i % 5 == 0:
                member["Extra"] = {
                    "Extra1": f"Extra info {i}-1",
                    "Extra2": f"Extra info {i}-2",
                    "Extra3": f"Extra info {i}-3"
                }
                
            members.append(member)
        
        return members
    
    def get_active_members(self):
        """Return only active members in a simplified format."""
        active_members = []
        today = datetime.now()
        
        for member in self.members:
            try:
                # Extract key information
                role = member["Organisations"]["Organisation"]["Roles"]["Role"]
                end_date_str = role["EndDate"]
                end_date = datetime.strptime(end_date_str, "%Y-%m-%dT%H:%M:%S")
                
                # Check if membership is active (end date is in the future)
                if end_date > today:
                    # Create a simplified member object for internal use
                    simplified_member = {
                        "organization_member_id": member["OrganisationMemberId"],
                        "first_name": member["Firstname"],
                        "last_name": member["Lastname"],
                        "email": member["ContactInfo"]["EMail"],
                        "member_code": member["MemberCode"],
                        "start_date": role["StartDate"],
                        "end_date": role["EndDate"],
                        "role_id": str(role["Id"]),
                        "role_name": role["Name"]
                    }
                    active_members.append(simplified_member)
            except (KeyError, ValueError) as e:
                logger.error(f"Error processing member {member.get('OrganisationMemberId', 'unknown')}: {e}")
        
        return active_members
    
    def extend_membership(self, email, days=30):
        """Extend a member's membership by the specified number of days."""
        for member in self.members:
            try:
                if member["ContactInfo"]["EMail"] == email:
                    # Get the role
                    role = member["Organisations"]["Organisation"]["Roles"]["Role"]
                    
                    # Parse the current end date
                    current_end_str = role["EndDate"]
                    current_end = datetime.strptime(current_end_str, "%Y-%m-%dT%H:%M:%S")
                    
                    # Add days
                    new_end = current_end + timedelta(days=days)
                    
                    # Update the member
                    role["EndDate"] = new_end.strftime("%Y-%m-%dT%H:%M:%S")
                    
                    # Save changes
                    self.save_data()
                    
                    logger.info(f"Extended membership for {email} by {days} days")
                    return True
            except (KeyError, ValueError) as e:
                logger.error(f"Error extending membership for {email}: {e}")
        
        logger.warning(f"Member with email {email} not found")
        return False


class MockIVMS:
    """Mock IVMS API with sample data."""
    def __init__(self, data_file):
        self.data_file = data_file
        self.load_or_create_data()
    
    def load_or_create_data(self):
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r') as f:
                self.users = json.load(f)
        else:
            # Create mock data
            self.users = self.generate_mock_users()
            self.save_data()
    
    def save_data(self):
        with open(self.data_file, 'w') as f:
            json.dump(self.users, f, indent=2)
    
    def generate_mock_users(self):
        """Generate mock IVMS user data."""
        users = []
        
        # Create 15 mock users (some will match Cardskipper members)
        for i in range(1, 16):
            # Generate an employee number for the user
            employee_no = str(2000 + i)
            
            # Set validity dates
            begin_time = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%dT%H:%M:%S")
            end_time = (datetime.now() + timedelta(days=365)).strftime("%Y-%m-%dT%H:%M:%S")
            
            # For the first 10 users, use names that might match Cardskipper
            if i <= 10:
                first_name = ["Luka", "Marko", "Jan", "Matej", "Andrej", "Nina", "Eva", "Maja", "Ana", "Sara"][i-1]
                last_name = ["Novak", "Kovačič", "Horvat", "Krajnc", "Zupančič", "Potočnik", "Kovač", "Mlakar", "Vidmar", "Golob"][i-1]
                name = f"{first_name} {last_name}"
                email = f"{first_name.lower()}.{last_name.lower()}@example.com"
            else:
                # For the rest, use generic names
                name = f"IVMS User {i}"
                email = f"ivms_user{i}@example.com"
            
            user = {
                "employeeNo": employee_no,
                "name": name,
                "email": email,
                "beginTime": begin_time,
                "endTime": end_time
            }
            
            users.append(user)
        
        return users
    
    def get_all_users(self):
        """Return all IVMS users."""
        return self.users
    
    def get_user_by_email(self, email):
        """Find a user by email."""
        for user in self.users:
            if user["email"] == email:
                return user
        return None
    
    def update_user_validity(self, employee_no, begin_time, end_time):
        """Update a user's validity period."""
        for user in self.users:
            if user["employeeNo"] == employee_no:
                user["beginTime"] = begin_time
                user["endTime"] = end_time
                self.save_data()
                logger.info(f"Updated validity for user {employee_no}")
                return True
        
        logger.warning(f"User with employee number {employee_no} not found")
        return False


class MockSyncService:
    """Mock service to synchronize Cardskipper and IVMS data."""
    def __init__(self, cardskipper, ivms, db):
        self.cardskipper = cardskipper
        self.ivms = ivms
        self.db = db
    
    def sync(self):
        """Synchronize membership data between systems."""
        try:
            logger.info("Starting synchronization")
            
            # Get active members from Cardskipper
            cardskipper_members = self.cardskipper.get_active_members()
            
            if not cardskipper_members:
                logger.warning("No active members found in Cardskipper")
                return
            
            # Get all members from database
            db_members = self.db.get_all_members()
            
            # Get all IVMS users
            ivms_users = self.ivms.get_all_users()
            
            # Create email to user ID mapping
            email_to_user_id = {}
            for user in ivms_users:
                if "email" in user and user["email"]:
                    email_to_user_id[user["email"]] = user["employeeNo"]
            
            # Process each member from Cardskipper
            updates_needed = []
            for member in cardskipper_members:
                try:
                    email = member["email"]
                    
                    # Check if we need to update this member
                    needs_update = False
                    ivms_user_id = None
                    
                    # Check if member exists in our database
                    if email in db_members:
                        db_member = db_members[email]
                        db_end_date = db_member["end_date"]
                        
                        # If end date has changed, we need to update
                        if db_end_date != member["end_date"]:
                            needs_update = True
                            logger.info(f"Member {email} needs update: end date changed from {db_end_date} to {member['end_date']}")
                        
                        # Get IVMS user ID from database
                        ivms_user_id = db_member["ivms_user_id"]
                    else:
                        # New member, needs update
                        needs_update = True
                        logger.info(f"New member found: {email}")
                    
                    # If we don't have an IVMS user ID yet, try to find one
                    if not ivms_user_id and email in email_to_user_id:
                        ivms_user_id = email_to_user_id[email]
                        logger.info(f"Found IVMS user ID for {email}: {ivms_user_id}")
                    
                    # Update member in our database
                    self.db.update_member(member, ivms_user_id)
                    
                    # If member needs update and we have an IVMS user ID, update IVMS
                    if needs_update and ivms_user_id:
                        updates_needed.append({
                            "email": email,
                            "ivms_user_id": ivms_user_id,
                            "start_date": member["start_date"],
                            "end_date": member["end_date"]
                        })
                
                except Exception as e:
                    logger.error(f"Error processing member {member.get('email', 'unknown')}: {e}")
            
            # Perform IVMS updates
            for update in updates_needed:
                success = self.ivms.update_user_validity(
                    update["ivms_user_id"],
                    update["start_date"],
                    update["end_date"]
                )
                
                if success:
                    logger.info(f"Successfully updated IVMS for member {update['email']}")
                else:
                    logger.error(f"Failed to update IVMS for member {update['email']}")
            
            logger.info(f"Synchronization completed: {len(updates_needed)} updates performed")
            
        except Exception as e:
            logger.error(f"Error during synchronization: {e}")


def simulate_membership_extension():
    """Simulate a membership extension in Cardskipper."""
    cardskipper = MockCardskipper(CARDSKIPPER_MEMBERS_FILE)
    
    # Get active members
    active_members = cardskipper.get_active_members()
    if not active_members:
        logger.error("No active members found to extend")
        return False
    
    # Pick a random member to extend
    member_to_extend = random.choice(active_members)
    email = member_to_extend["email"]
    
    # Find the original member to get current end date
    for member in cardskipper.members:
        if member["ContactInfo"]["EMail"] == email:
            role = member["Organisations"]["Organisation"]["Roles"]["Role"]
            old_end_date = role["EndDate"]
            break
    else:
        logger.error(f"Could not find original member record for {email}")
        return False
    
    # Extend membership by a random number of days (30, 60, or 90)
    days_to_extend = random.choice([30, 60, 90])
    
    success = cardskipper.extend_membership(email, days_to_extend)
    
    if success:
        # Reload to get updated data
        cardskipper = MockCardskipper(CARDSKIPPER_MEMBERS_FILE)
        
        # Find the updated member
        for member in cardskipper.members:
            if member["ContactInfo"]["EMail"] == email:
                role = member["Organisations"]["Organisation"]["Roles"]["Role"]
                new_end_date = role["EndDate"]
                
                logger.info(f"Simulated membership extension for {email}")
                logger.info(f"Member: {member['Firstname']} {member['Lastname']}")
                logger.info(f"Membership: {role['Name']}")
                logger.info(f"Old end date: {old_end_date}")
                logger.info(f"New end date: {new_end_date}")
                logger.info(f"Extended by: {days_to_extend} days")
                return True
    
    return False


def run_simulation(num_cycles=3, interval_seconds=5):
    """Run a simulation of the integration."""
    try:
        logger.info("Starting improved mock integration simulation")
        
        # Initialize components
        cardskipper = MockCardskipper(CARDSKIPPER_MEMBERS_FILE)
        ivms = MockIVMS(IVMS_USERS_FILE)
        db = MockDatabase(DB_FILE)
        
        # Create sync service
        sync_service = MockSyncService(cardskipper, ivms, db)
        
        # Initial sync
        logger.info("Performing initial synchronization")
        sync_service.sync()
        
        # Run simulation cycles
        for cycle in range(1, num_cycles + 1):
            logger.info(f"Starting simulation cycle {cycle}")
            
            # Simulate a membership extension
            if simulate_membership_extension():
                logger.info("Membership extension simulated successfully")
            else:
                logger.warning("Failed to simulate membership extension")
            
            # Wait for the specified interval
            logger.info(f"Waiting {interval_seconds} seconds before next sync")
            time.sleep(interval_seconds)
            
            # Perform synchronization
            logger.info(f"Performing synchronization cycle {cycle}")
            sync_service.sync()
        
        logger.info("Simulation completed successfully")
        
        # Print final status
        logger.info("Final Status Report:")
        active_members = cardskipper.get_active_members()
        logger.info(f"Cardskipper active members: {len(active_members)}")
        ivms_users = ivms.get_all_users()
        logger.info(f"IVMS users: {len(ivms_users)}")
        db_members = db.get_all_members()
        logger.info(f"Database members: {len(db_members)}")
        
        # Print details of a few members that got updated
        logger.info("\nSample of synced members:")
        synced_members = []
        for email, db_member in db_members.items():
            if db_member["ivms_user_id"]:
                synced_members.append(db_member)
        
        # Show up to 5 synced members
        for i, member in enumerate(synced_members[:5]):
            logger.info(f"{i+1}. {member['first_name']} {member['last_name']} ({member['email']})")
            logger.info(f"   Cardskipper ID: {member['organization_member_id']}")
            logger.info(f"   IVMS ID: {member['ivms_user_id']}")
            logger.info(f"   Valid until: {member['end_date']}")
            logger.info(f"   Role: {member['role_name']} (ID: {member['role_id']})")
            logger.info("")
        
        return True
        
    except Exception as e:
        logger.error(f"Error during simulation: {e}")
        return False
    finally:
        if 'db' in locals():
            db.close()


if __name__ == "__main__":
    run_simulation(num_cycles=3, interval_seconds=3)