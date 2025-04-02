#!/usr/bin/env python3
"""
Mock implementation of Cardskipper to IVMS integration.
This script simulates both APIs and demonstrates the integration logic.
"""

import json
import xml.etree.ElementTree as ET
import sqlite3
import logging
import time
from datetime import datetime, timedelta
import uuid
import os
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("mock_integration.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("MockIntegration")

# Path for mock data
MOCK_DATA_DIR = "mock_data"
if not os.path.exists(MOCK_DATA_DIR):
    os.makedirs(MOCK_DATA_DIR)

# Mock Cardskipper data
CARDSKIPPER_MEMBERS_FILE = os.path.join(MOCK_DATA_DIR, "cardskipper_members.json")
# Mock IVMS data
IVMS_USERS_FILE = os.path.join(MOCK_DATA_DIR, "ivms_users.json")
# SQLite database for integration
DB_FILE = os.path.join(MOCK_DATA_DIR, "integration.db")

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
                    ivms_user_id TEXT
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
            self.cursor.execute("SELECT email, organization_member_id, start_date, end_date, first_name, last_name, ivms_user_id FROM members")
            rows = self.cursor.fetchall()
            
            members = {}
            for row in rows:
                email, org_member_id, start_date, end_date, first_name, last_name, ivms_user_id = row
                members[email] = {
                    "email": email,
                    "organization_member_id": org_member_id,
                    "start_date": start_date,
                    "end_date": end_date,
                    "first_name": first_name,
                    "last_name": last_name,
                    "ivms_user_id": ivms_user_id
                }
            
            return members
        except Exception as e:
            logger.error(f"Error getting members from database: {e}")
            return {}
    
    def update_member(self, member, ivms_user_id=None):
        try:
            # Check if the member exists
            self.cursor.execute("SELECT email FROM members WHERE email = ?", (member["email"],))
            existing_member = self.cursor.fetchone()
            
            if existing_member:
                # Update existing member
                if ivms_user_id:
                    self.cursor.execute("""
                        UPDATE members 
                        SET organization_member_id = ?, start_date = ?, end_date = ?, 
                            first_name = ?, last_name = ?, ivms_user_id = ?
                        WHERE email = ?
                    """, (
                        member["organization_member_id"], 
                        member["start_date"], 
                        member["end_date"],
                        member["first_name"],
                        member["last_name"],
                        ivms_user_id,
                        member["email"]
                    ))
                else:
                    self.cursor.execute("""
                        UPDATE members 
                        SET organization_member_id = ?, start_date = ?, end_date = ?, 
                            first_name = ?, last_name = ?
                        WHERE email = ?
                    """, (
                        member["organization_member_id"], 
                        member["start_date"], 
                        member["end_date"],
                        member["first_name"],
                        member["last_name"],
                        member["email"]
                    ))
            else:
                # Insert new member
                self.cursor.execute("""
                    INSERT INTO members (email, organization_member_id, start_date, end_date, first_name, last_name, ivms_user_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    member["email"], 
                    member["organization_member_id"], 
                    member["start_date"], 
                    member["end_date"],
                    member["first_name"],
                    member["last_name"],
                    ivms_user_id
                ))
            
            self.conn.commit()
            logger.info(f"Updated member in database: {member['email']}")
        except Exception as e:
            logger.error(f"Error updating member in database: {e}")
            self.conn.rollback()
    
    def get_ivms_user_id(self, email):
        try:
            self.cursor.execute("SELECT ivms_user_id FROM members WHERE email = ?", (email,))
            result = self.cursor.fetchone()
            return result[0] if result else None
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
                self.members = json.load(f)
        else:
            # Create mock data
            self.members = self.generate_mock_members()
            self.save_data()
    
    def save_data(self):
        with open(self.data_file, 'w') as f:
            json.dump(self.members, f, indent=2)
    
    def generate_mock_members(self):
        """Generate mock membership data."""
        members = []
        
        # Create 20 mock members
        for i in range(1, 21):
            # Generate a unique ID for the member
            org_member_id = str(1000 + i)
            
            # Alternate between different validity periods
            if i % 3 == 0:
                # Expired membership
                start_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%dT%H:%M:%S")
                end_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%dT%H:%M:%S")
            elif i % 3 == 1:
                # Soon to expire
                start_date = (datetime.now() - timedelta(days=330)).strftime("%Y-%m-%dT%H:%M:%S")
                end_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%dT%H:%M:%S")
            else:
                # Valid for a while
                start_date = (datetime.now() - timedelta(days=60)).strftime("%Y-%m-%dT%H:%M:%S")
                end_date = (datetime.now() + timedelta(days=300)).strftime("%Y-%m-%dT%H:%M:%S")
            
            member = {
                "organization_member_id": org_member_id,
                "first_name": f"FirstName{i}",
                "last_name": f"LastName{i}",
                "email": f"member{i}@example.com",
                "start_date": start_date,
                "end_date": end_date,
                "active": i % 3 != 0  # Only expired memberships are inactive
            }
            
            members.append(member)
        
        return members
    
    def get_active_members(self):
        """Return only active members."""
        return [m for m in self.members if m["active"]]
    
    def extend_membership(self, email, days=30):
        """Extend a member's membership by the specified number of days."""
        for member in self.members:
            if member["email"] == email:
                # Parse the current end date
                current_end = datetime.strptime(member["end_date"], "%Y-%m-%dT%H:%M:%S")
                # Add days
                new_end = current_end + timedelta(days=days)
                # Update the member
                member["end_date"] = new_end.strftime("%Y-%m-%dT%H:%M:%S")
                member["active"] = True
                self.save_data()
                logger.info(f"Extended membership for {email} by {days} days")
                return True
        
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
            
            # Make some emails match the Cardskipper format for testing
            if i <= 10:
                email = f"member{i}@example.com"
            else:
                email = f"ivms_user{i}@example.com"
            
            user = {
                "employee_no": employee_no,
                "name": f"User {i}",
                "email": email,
                "begin_time": begin_time,
                "end_time": end_time
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
            if user["employee_no"] == employee_no:
                user["begin_time"] = begin_time
                user["end_time"] = end_time
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
                    email_to_user_id[user["email"]] = user["employee_no"]
            
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
                    logger.error(f"Error processing member {member['email']}: {e}")
            
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
    
    # Get an active member to extend
    active_members = cardskipper.get_active_members()
    if not active_members:
        logger.error("No active members found to extend")
        return False
    
    # Pick the first member
    member_to_extend = active_members[0]
    email = member_to_extend["email"]
    
    # Extend membership by 60 days
    days_to_extend = 60
    old_end_date = member_to_extend["end_date"]
    
    success = cardskipper.extend_membership(email, days_to_extend)
    
    if success:
        # Reload to get updated data
        cardskipper = MockCardskipper(CARDSKIPPER_MEMBERS_FILE)
        updated_members = [m for m in cardskipper.members if m["email"] == email]
        if updated_members:
            new_end_date = updated_members[0]["end_date"]
            logger.info(f"Simulated membership extension for {email}")
            logger.info(f"Old end date: {old_end_date}")
            logger.info(f"New end date: {new_end_date}")
            return True
    
    return False


def run_simulation(num_cycles=3, interval_seconds=5):
    """Run a simulation of the integration."""
    try:
        logger.info("Starting mock integration simulation")
        
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
        
        return True
        
    except Exception as e:
        logger.error(f"Error during simulation: {e}")
        return False
    finally:
        if 'db' in locals():
            db.close()


if __name__ == "__main__":
    run_simulation()