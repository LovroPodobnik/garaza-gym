import streamlit as st
import json
import os
import time
import random
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import altair as alt

# Set page configuration
st.set_page_config(
    page_title="Cardskipper to IVMS Integration Demo",
    page_icon="🔄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Path for mock data
MOCK_DATA_DIR = "mock_data"
if not os.path.exists(MOCK_DATA_DIR):
    os.makedirs(MOCK_DATA_DIR)

# Mock data files
CARDSKIPPER_MEMBERS_FILE = os.path.join(MOCK_DATA_DIR, "cardskipper_members_demo.json")
IVMS_USERS_FILE = os.path.join(MOCK_DATA_DIR, "ivms_users_demo.json")
DB_FILE = os.path.join(MOCK_DATA_DIR, "integration_demo.db")

# Custom CSS
st.markdown("""
    <style>
        .main {
            background-color: #f5f5f5;
        }
        .stApp {
            max-width: 1200px;
            margin: 0 auto;
        }
        .card {
            background-color: white;
            border-radius: 5px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        .header {
            color: #1E3A8A;
            font-weight: bold;
        }
        .subheader {
            color: #3B82F6;
            font-weight: 500;
        }
        .highlight {
            background-color: #DBEAFE;
            padding: 5px;
            border-radius: 3px;
        }
        .success {
            color: #10B981;
            font-weight: bold;
        }
        .error {
            color: #EF4444;
            font-weight: bold;
        }
        .info {
            color: #3B82F6;
            font-weight: bold;
        }
        .warning {
            color: #F59E0B;
            font-weight: bold;
        }
    </style>
""", unsafe_allow_html=True)


class DatabaseManager:
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
                    ivms_employee_no TEXT,
                    member_code TEXT,
                    role_id TEXT,
                    role_name TEXT,
                    phone TEXT
                )
            ''')
            
            # Create sync_history table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS sync_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT NOT NULL,
                    cardskipper_id TEXT NOT NULL,
                    ivms_id TEXT,
                    previous_end_date TEXT,
                    new_end_date TEXT,
                    sync_status TEXT,
                    sync_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create sync_errors table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS sync_errors (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT,
                    error_message TEXT,
                    error_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    resolved BOOLEAN DEFAULT FALSE
                )
            ''')
            
            self.conn.commit()
        except Exception as e:
            st.error(f"Error initializing database: {e}")
            raise
    
    def close(self):
        if self.conn:
            self.conn.close()
    
    def get_all_members(self):
        try:
            self.cursor.execute("""
                SELECT email, organization_member_id, start_date, end_date, 
                       first_name, last_name, ivms_employee_no, member_code, 
                       role_id, role_name, phone 
                FROM members
            """)
            rows = self.cursor.fetchall()
            
            members = {}
            for row in rows:
                email, org_member_id, start_date, end_date, first_name, last_name, ivms_employee_no, member_code, role_id, role_name, phone = row
                members[email] = {
                    "email": email,
                    "organization_member_id": org_member_id,
                    "start_date": start_date,
                    "end_date": end_date,
                    "first_name": first_name,
                    "last_name": last_name,
                    "ivms_employee_no": ivms_employee_no,
                    "member_code": member_code,
                    "role_id": role_id,
                    "role_name": role_name,
                    "phone": phone
                }
            
            return members
        except Exception as e:
            st.error(f"Error getting members from database: {e}")
            return {}
    
    def update_member(self, member, ivms_employee_no=None):
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
            phone = member.get("phone", "")
            
            # Check if the member exists
            self.cursor.execute("SELECT email, end_date FROM members WHERE email = ?", (email,))
            existing_member = self.cursor.fetchone()
            
            if existing_member:
                previous_end_date = existing_member[1]
                
                # Update existing member
                if ivms_employee_no:
                    self.cursor.execute("""
                        UPDATE members 
                        SET organization_member_id = ?, start_date = ?, end_date = ?, 
                            first_name = ?, last_name = ?, ivms_employee_no = ?,
                            member_code = ?, role_id = ?, role_name = ?, phone = ?
                        WHERE email = ?
                    """, (
                        org_member_id, 
                        start_date, 
                        end_date,
                        first_name,
                        last_name,
                        ivms_employee_no,
                        member_code,
                        role_id,
                        role_name,
                        phone,
                        email
                    ))
                else:
                    self.cursor.execute("""
                        UPDATE members 
                        SET organization_member_id = ?, start_date = ?, end_date = ?, 
                            first_name = ?, last_name = ?,
                            member_code = ?, role_id = ?, role_name = ?, phone = ?
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
                        phone,
                        email
                    ))
                
                # Record in sync history if end date changed
                if previous_end_date != end_date:
                    self.cursor.execute("""
                        INSERT INTO sync_history (
                            email, cardskipper_id, ivms_id, previous_end_date, new_end_date, sync_status
                        )
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        email,
                        org_member_id,
                        ivms_employee_no or "Not matched",
                        previous_end_date,
                        end_date,
                        "Success" if ivms_employee_no else "Pending"
                    ))
            else:
                # Insert new member
                self.cursor.execute("""
                    INSERT INTO members (
                        email, organization_member_id, start_date, end_date,
                        first_name, last_name, ivms_employee_no, member_code, 
                        role_id, role_name, phone
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    email, 
                    org_member_id, 
                    start_date, 
                    end_date,
                    first_name,
                    last_name,
                    ivms_employee_no,
                    member_code,
                    role_id,
                    role_name,
                    phone
                ))
                
                # Record in sync history as new member
                self.cursor.execute("""
                    INSERT INTO sync_history (
                        email, cardskipper_id, ivms_id, previous_end_date, new_end_date, sync_status
                    )
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    email,
                    org_member_id,
                    ivms_employee_no or "Not matched",
                    None,
                    end_date,
                    "New member"
                ))
            
            self.conn.commit()
        except Exception as e:
            st.error(f"Error updating member in database: {e}")
            # Record error
            self.cursor.execute("""
                INSERT INTO sync_errors (email, error_message)
                VALUES (?, ?)
            """, (email, str(e)))
            self.conn.commit()
            self.conn.rollback()
    
    def get_ivms_employee_no(self, email):
        try:
            self.cursor.execute("SELECT ivms_employee_no FROM members WHERE email = ?", (email,))
            result = self.cursor.fetchone()
            return result[0] if result and result[0] else None
        except Exception as e:
            st.error(f"Error getting IVMS employee number for {email}: {e}")
            return None
    
    def get_sync_history(self, limit=100):
        try:
            self.cursor.execute("""
                SELECT id, email, cardskipper_id, ivms_id, previous_end_date, new_end_date, sync_status, sync_time
                FROM sync_history
                ORDER BY sync_time DESC
                LIMIT ?
            """, (limit,))
            return self.cursor.fetchall()
        except Exception as e:
            st.error(f"Error getting sync history: {e}")
            return []
    
    def get_sync_errors(self, limit=100):
        try:
            self.cursor.execute("""
                SELECT id, email, error_message, error_time, resolved
                FROM sync_errors
                ORDER BY error_time DESC
                LIMIT ?
            """, (limit,))
            return self.cursor.fetchall()
        except Exception as e:
            st.error(f"Error getting sync errors: {e}")
            return []
    
    def get_sync_stats(self):
        try:
            # Get total members
            self.cursor.execute("SELECT COUNT(*) FROM members")
            total_members = self.cursor.fetchone()[0]
            
            # Get synced members (with IVMS ID)
            self.cursor.execute("SELECT COUNT(*) FROM members WHERE ivms_employee_no IS NOT NULL")
            synced_members = self.cursor.fetchone()[0]
            
            # Get unsynced members
            self.cursor.execute("SELECT COUNT(*) FROM members WHERE ivms_employee_no IS NULL")
            unsynced_members = self.cursor.fetchone()[0]
            
            # Get total sync operations
            self.cursor.execute("SELECT COUNT(*) FROM sync_history")
            total_syncs = self.cursor.fetchone()[0]
            
            # Get successful syncs
            self.cursor.execute("SELECT COUNT(*) FROM sync_history WHERE sync_status = 'Success'")
            successful_syncs = self.cursor.fetchone()[0]
            
            # Get sync errors
            self.cursor.execute("SELECT COUNT(*) FROM sync_errors")
            sync_errors = self.cursor.fetchone()[0]
            
            # Get sync history grouped by day
            self.cursor.execute("""
                SELECT DATE(sync_time) as sync_date, COUNT(*) as count
                FROM sync_history
                GROUP BY DATE(sync_time)
                ORDER BY sync_date
            """)
            sync_by_date = self.cursor.fetchall()
            
            return {
                "total_members": total_members,
                "synced_members": synced_members,
                "unsynced_members": unsynced_members,
                "total_syncs": total_syncs,
                "successful_syncs": successful_syncs,
                "sync_errors": sync_errors,
                "sync_by_date": sync_by_date
            }
        except Exception as e:
            st.error(f"Error getting sync stats: {e}")
            return {
                "total_members": 0,
                "synced_members": 0,
                "unsynced_members": 0,
                "total_syncs": 0,
                "successful_syncs": 0,
                "sync_errors": 0,
                "sync_by_date": []
            }
    
    def resolve_error(self, error_id):
        try:
            self.cursor.execute("UPDATE sync_errors SET resolved = 1 WHERE id = ?", (error_id,))
            self.conn.commit()
            return True
        except Exception as e:
            st.error(f"Error resolving error: {e}")
            return False


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
        chars = "abcdefghijklmnopqrstuvwxyz0123456789"
        return ''.join(random.choice(chars) for _ in range(length))
    
    def generate_mock_members(self):
        """Generate mock membership data."""
        # Sample member data based on the example
        members = [
            {
                "OrganisationMemberId": "1001",
                "Firstname": "Adi",
                "Lastname": "Mijatović",
                "Birthdate": "2008-10-11T00:00:00",
                "MemberCode": "3ket5yk",
                "ContactInfo": {
                    "EMail": "adi.mijatovic@example.com",
                    "CellPhone1": "+38670123456"
                },
                "Organisations": {
                    "Organisation": {
                        "Id": 123,
                        "Roles": {
                            "Role": {
                                "Id": 456,
                                "Name": "Dijak 16-17",
                                "StartDate": "2024-07-01T00:00:00",
                                "EndDate": "2025-02-07T23:59:59",
                                "Type": "Student",
                                "OrganisationUnit": "Youth"
                            }
                        }
                    }
                },
                "Extra": {
                    "Extra1": "",
                    "Extra2": "",
                    "Extra3": ""
                }
            },
            {
                "OrganisationMemberId": "1002",
                "Firstname": "Admil",
                "Lastname": "Kantarević",
                "Birthdate": "2005-03-05T00:00:00",
                "MemberCode": "4rpj24",
                "ContactInfo": {
                    "EMail": "admil.kantarevic@example.com",
                    "CellPhone1": "+38670234567"
                },
                "Organisations": {
                    "Organisation": {
                        "Id": 123,
                        "Roles": {
                            "Role": {
                                "Id": 457,
                                "Name": "24/7",
                                "StartDate": "2024-10-17T00:00:00",
                                "EndDate": "2025-10-16T23:59:59",
                                "Type": "Regular",
                                "OrganisationUnit": "Adult"
                            }
                        }
                    }
                }
            },
            {
                "OrganisationMemberId": "1003",
                "Firstname": "Admir",
                "Lastname": "Fetić",
                "Birthdate": "1987-04-06T00:00:00",
                "MemberCode": "cpl48v",
                "ContactInfo": {
                    "EMail": "admir.fetic@example.com",
                    "CellPhone1": "+38670345678"
                },
                "Organisations": {
                    "Organisation": {
                        "Id": 123,
                        "Roles": {
                            "Role": {
                                "Id": 458,
                                "Name": "OG - stari član",
                                "StartDate": "2024-03-04T00:00:00",
                                "EndDate": "2025-03-03T23:59:59",
                                "Type": "Regular",
                                "OrganisationUnit": "Adult"
                            }
                        }
                    }
                }
            },
            {
                "OrganisationMemberId": "1004",
                "Firstname": "Admir",
                "Lastname": "Guberinić",
                "Birthdate": "1994-12-26T00:00:00",
                "MemberCode": "9m1881",
                "ContactInfo": {
                    "EMail": "admir.guberinic@example.com",
                    "CellPhone1": "+38670456789"
                },
                "Organisations": {
                    "Organisation": {
                        "Id": 123,
                        "Roles": {
                            "Role": {
                                "Id": 457,
                                "Name": "24/7",
                                "StartDate": "2025-01-27T00:00:00",
                                "EndDate": "2026-01-26T23:59:59",
                                "Type": "Regular",
                                "OrganisationUnit": "Adult"
                            }
                        }
                    }
                }
            },
            {
                "OrganisationMemberId": "1005",
                "Firstname": "Adrian",
                "Lastname": "Kočan",
                "Birthdate": "2007-12-03T00:00:00",
                "MemberCode": "u1ua34",
                "ContactInfo": {
                    "EMail": "adrian.kocan@example.com",
                    "CellPhone1": "+38670567890"
                },
                "Organisations": {
                    "Organisation": {
                        "Id": 123,
                        "Roles": {
                            "Role": {
                                "Id": 456,
                                "Name": "Dijak 16-17",
                                "StartDate": "2024-08-15T00:00:00",
                                "EndDate": "2025-02-15T23:59:59",
                                "Type": "Student",
                                "OrganisationUnit": "Youth"
                            }
                        }
                    }
                }
            },
            {
                "OrganisationMemberId": "1006",
                "Firstname": "Aida",
                "Lastname": "Alibović",
                "Birthdate": "1992-05-15T00:00:00",
                "MemberCode": "h7kl93",
                "ContactInfo": {
                    "EMail": "aida.alibovic@example.com",
                    "CellPhone1": "+38670678901"
                },
                "Organisations": {
                    "Organisation": {
                        "Id": 123,
                        "Roles": {
                            "Role": {
                                "Id": 459,
                                "Name": "Mesečna",
                                "StartDate": "2024-02-20T00:00:00",
                                "EndDate": "2025-02-19T23:59:59",
                                "Type": "Regular",
                                "OrganisationUnit": "Adult"
                            }
                        }
                    }
                }
            },
            {
                "OrganisationMemberId": "1007",
                "Firstname": "Luka",
                "Lastname": "Starčević",
                "Birthdate": "1995-03-22T00:00:00",
                "MemberCode": "p8mn23",
                "ContactInfo": {
                    "EMail": "luka.starcevic@example.com",
                    "CellPhone1": ""
                },
                "Organisations": {
                    "Organisation": {
                        "Id": 123,
                        "Roles": {
                            "Role": {
                                "Id": 459,
                                "Name": "Mesečna",
                                "StartDate": "2025-02-04T00:00:00",
                                "EndDate": "2025-03-06T23:59:59",
                                "Type": "Regular",
                                "OrganisationUnit": "Adult"
                            }
                        }
                    }
                }
            }
        ]
        
        # Add a few more members
        for i in range(8, 15):
            # Sample Slovenian names
            first_names = ["Marko", "Jan", "Matej", "Nejc", "Žiga", "Ana", "Maja", "Eva", "Nina", "Tina", "Anja", "Peter", "Jure"]
            last_names = ["Novak", "Horvat", "Kovačič", "Krajnc", "Zupančič", "Potočnik", "Kovač", "Mlakar", "Vidmar", "Golob"]
            
            # Pick random name
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            
            # Generate random birthdate
            year = random.randint(1980, 2008)
            month = random.randint(1, 12)
            day = random.randint(1, 28)
            birthdate = f"{year}-{month:02d}-{day:02d}T00:00:00"
            
            # Generate member code
            member_code = self.generate_random_member_code()
            
            # Generate email and phone
            email = f"{first_name.lower()}.{last_name.lower()}@example.com"
            phone = f"+3867{random.randint(1000000, 9999999)}"
            
            # Define role types
            roles = [
                {"Id": 456, "Name": "Dijak 16-17", "Type": "Student", "OrganisationUnit": "Youth"},
                {"Id": 457, "Name": "24/7", "Type": "Regular", "OrganisationUnit": "Adult"},
                {"Id": 458, "Name": "OG - stari član", "Type": "Regular", "OrganisationUnit": "Adult"},
                {"Id": 459, "Name": "Mesečna", "Type": "Regular", "OrganisationUnit": "Adult"},
                {"Id": 460, "Name": "Študent", "Type": "Student", "OrganisationUnit": "Adult"}
            ]
            
            # Pick a random role
            role = random.choice(roles)
            
            # Generate dates
            now = datetime.now()
            start_date = (now - timedelta(days=random.randint(30, 180))).strftime("%Y-%m-%dT%H:%M:%S")
            
            # End date based on role
            if role["Name"] == "Mesečna":
                end_date = (now + timedelta(days=random.randint(15, 45))).strftime("%Y-%m-%dT%H:%M:%S")
            elif role["Name"] == "24/7":
                end_date = (now + timedelta(days=random.randint(180, 365))).strftime("%Y-%m-%dT%H:%M:%S")
            else:
                end_date = (now + timedelta(days=random.randint(30, 180))).strftime("%Y-%m-%dT%H:%M:%S")
            
            # Create the member object
            member = {
                "OrganisationMemberId": f"{1000 + i}",
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
                        "Id": 123,
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
                        "phone": member["ContactInfo"]["CellPhone1"],
                        "member_code": member["MemberCode"],
                        "start_date": role["StartDate"],
                        "end_date": role["EndDate"],
                        "role_id": str(role["Id"]),
                        "role_name": role["Name"]
                    }
                    active_members.append(simplified_member)
            except (KeyError, ValueError) as e:
                st.error(f"Error processing member {member.get('OrganisationMemberId', 'unknown')}: {e}")
        
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
                    
                    return {
                        "success": True,
                        "message": f"Extended membership for {member['Firstname']} {member['Lastname']} by {days} days",
                        "old_end_date": current_end_str,
                        "new_end_date": new_end.strftime("%Y-%m-%dT%H:%M:%S"),
                        "member": {
                            "name": f"{member['Firstname']} {member['Lastname']}",
                            "email": email,
                            "role": role["Name"]
                        }
                    }
            except (KeyError, ValueError) as e:
                return {
                    "success": False,
                    "message": f"Error extending membership: {e}",
                    "email": email
                }
        
        return {
            "success": False,
            "message": f"Member with email {email} not found",
            "email": email
        }


class MockIVMS:
    """Mock IVMS API with sample data."""
    def __init__(self, data_file):
        self.data_file = data_file
        self.load_or_create_data()
    
    def load_or_create_data(self):
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r') as f:
                data = json.load(f)
                self.user_info = data.get("UserInfoSearchResult", {}).get("UserInfo", [])
                self.search_id = data.get("UserInfoSearchResult", {}).get("searchID", "1")
                self.total_matches = len(self.user_info)
        else:
            # Create mock data
            self.user_info = self.generate_mock_users()
            self.search_id = "1"
            self.total_matches = len(self.user_info)
            self.save_data()
    
    def save_data(self):
        data = {
            "UserInfoSearchResult": {
                "searchID": self.search_id,
                "responseStatusStrg": "OK",
                "numOfMatches": self.total_matches,
                "totalMatches": self.total_matches,
                "UserInfo": self.user_info
            }
        }
        with open(self.data_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def generate_mock_users(self):
        """Generate mock IVMS user data."""
        # Use the example data as a base
        users = [
            {
                "employeeNo": "00000051",
                "name": "Luka Starcevic",
                "gender": "male",
                "email": "luka.starcevic@example.com",
                "phoneNo": "",
                "Valid": {
                    "enable": True,
                    "beginTime": "2025-02-04T00:00:00",
                    "endTime": "2025-03-06T23:59:59"
                }
            },
            {
                "employeeNo": "00000052",
                "name": "Adi Mijatović",
                "gender": "male",
                "email": "adi.mijatovic@example.com",
                "phoneNo": "+38670123456",
                "Valid": {
                    "enable": True,
                    "beginTime": "2024-07-01T00:00:00",
                    "endTime": "2025-02-07T23:59:59"
                }
            },
            {
                "employeeNo": "00000053",
                "name": "Admil Kantarevic",
                "gender": "male",
                "email": "admil.kantarevic@example.com",
                "phoneNo": "+38670234567",
                "Valid": {
                    "enable": True,
                    "beginTime": "2024-10-17T00:00:00",
                    "endTime": "2025-10-16T23:59:59"
                }
            },
            {
                "employeeNo": "00000054",
                "name": "Admir Fetic",
                "gender": "male",
                "email": "admir.fetic@example.com",
                "phoneNo": "+38670345678",
                "Valid": {
                    "enable": True,
                    "beginTime": "2024-03-04T00:00:00",
                    "endTime": "2025-03-03T23:59:59"
                }
            },
            {
                "employeeNo": "00000055",
                "name": "Admir Guberinic",
                "gender": "male",
                "email": "admir.guberinic@example.com",
                "phoneNo": "+38670456789",
                "Valid": {
                    "enable": True,
                    "beginTime": "2025-01-27T00:00:00",
                    "endTime": "2026-01-26T23:59:59"
                }
            },
            {
                "employeeNo": "00000056",
                "name": "Adrian Kocan",
                "gender": "male",
                "email": "adrian.kocan@example.com",
                "phoneNo": "+38670567890",
                "Valid": {
                    "enable": True,
                    "beginTime": "2024-08-15T00:00:00",
                    "endTime": "2025-02-15T23:59:59"
                }
            },
            {
                "employeeNo": "00000057",
                "name": "Aida Alibovic",
                "gender": "female",
                "email": "aida.alibovic@example.com",
                "phoneNo": "+38670678901",
                "Valid": {
                    "enable": True,
                    "beginTime": "2024-02-20T00:00:00",
                    "endTime": "2025-02-19T23:59:59"
                }
            }
        ]
        
        return users
    
    def get_all_users(self):
        """Return all IVMS users."""
        return self.user_info
    
    def get_user_by_email(self, email):
        """Find a user by email."""
        for user in self.user_info:
            if user.get("email") == email:
                return user
        return None
    
    def update_user_validity(self, employee_no, begin_time, end_time):
        """Update a user's validity period."""
        for user in self.user_info:
            if user["employeeNo"] == employee_no:
                user["Valid"]["beginTime"] = begin_time
                user["Valid"]["endTime"] = end_time
                user["Valid"]["enable"] = True
                self.save_data()
                return True
        
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
            # Get active members from Cardskipper
            cardskipper_members = self.cardskipper.get_active_members()
            
            if not cardskipper_members:
                return {
                    "success": False,
                    "message": "No active members found in Cardskipper"
                }
            
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
                    ivms_employee_no = None
                    
                    # Check if member exists in our database
                    if email in db_members:
                        db_member = db_members[email]
                        db_end_date = db_member["end_date"]
                        
                        # If end date has changed, we need to update
                        if db_end_date != member["end_date"]:
                            needs_update = True
                        
                        # Get IVMS employee number from database
                        ivms_employee_no = db_member["ivms_employee_no"]
                    else:
                        # New member, needs update
                        needs_update = True
                    
                    # If we don't have an IVMS employee number yet, try to find one
                    if not ivms_employee_no and email in email_to_user_id:
                        ivms_employee_no = email_to_user_id[email]
                    
                    # Update member in our database
                    self.db.update_member(member, ivms_employee_no)
                    
                    # If member needs update and we have an IVMS employee number, update IVMS
                    if needs_update and ivms_employee_no:
                        updates_needed.append({
                            "email": email,
                            "ivms_employee_no": ivms_employee_no,
                            "start_date": member["start_date"],
                            "end_date": member["end_date"]
                        })
                
                except Exception as e:
                    # Record error
                    self.db.cursor.execute("""
                        INSERT INTO sync_errors (email, error_message)
                        VALUES (?, ?)
                    """, (member.get("email", "unknown"), str(e)))
                    self.db.conn.commit()
            
            # Perform IVMS updates
            updated_count = 0
            for update in updates_needed:
                success = self.ivms.update_user_validity(
                    update["ivms_employee_no"],
                    update["start_date"],
                    update["end_date"]
                )
                
                if success:
                    updated_count += 1
            
            return {
                "success": True,
                "message": f"Synchronization completed successfully",
                "total_members": len(cardskipper_members),
                "updates_needed": len(updates_needed),
                "updates_completed": updated_count
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error during synchronization: {e}"
            }


def initialize_demo():
    """Initialize the demo environment."""
    # Initialize components
    cardskipper = MockCardskipper(CARDSKIPPER_MEMBERS_FILE)
    ivms = MockIVMS(IVMS_USERS_FILE)
    db = DatabaseManager(DB_FILE)
    sync_service = MockSyncService(cardskipper, ivms, db)
    
    return cardskipper, ivms, db, sync_service


def show_header():
    """Display the app header."""
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("Cardskipper to IVMS Integration Demo")
        st.markdown("*Automatically synchronize membership dates from Cardskipper to IVMS access control system*")
    with col2:
        st.image("https://www.cardskipper.com/wp-content/uploads/2018/11/Cardskipper-logotype.png", width=200)


def show_dashboard(db, sync_service):
    """Display the main dashboard."""
    st.markdown("## Dashboard", unsafe_allow_html=True)
    
    # Get stats
    stats = db.get_sync_stats()
    
    # Create metrics row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Members", stats["total_members"])
    with col2:
        st.metric("Synced with IVMS", stats["synced_members"])
    with col3:
        st.metric("Total Sync Operations", stats["total_syncs"])
    with col4:
        st.metric("Sync Success Rate", f"{int(stats['successful_syncs']/max(1, stats['total_syncs'])*100)}%")
    
    # Create charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Members Status", unsafe_allow_html=True)
        if stats["total_members"] > 0:
            fig, ax = plt.subplots()
            ax.pie(
                [stats["synced_members"], stats["unsynced_members"]], 
                labels=["Synced with IVMS", "Not synced"], 
                autopct='%1.1f%%',
                colors=['#3B82F6', '#9CA3AF']
            )
            st.pyplot(fig)
        else:
            st.info("No members in the system yet.")
    
    with col2:
        st.markdown("### Sync History", unsafe_allow_html=True)
        if stats["sync_by_date"]:
            # Create a pandas DataFrame from the sync_by_date data
            df = pd.DataFrame(stats["sync_by_date"], columns=["Date", "Count"])
            df["Date"] = pd.to_datetime(df["Date"])
            
            # Create a bar chart
            chart = alt.Chart(df).mark_bar().encode(
                x=alt.X('Date:T', title='Date'),
                y=alt.Y('Count:Q', title='Number of Syncs'),
                color=alt.value('#3B82F6')
            ).properties(
                width=400,
                height=300
            )
            
            st.altair_chart(chart, use_container_width=True)
        else:
            st.info("No sync history available.")
    
    # Show recent sync operations
    st.markdown("### Recent Sync Operations", unsafe_allow_html=True)
    sync_history = db.get_sync_history(limit=10)
    
    if sync_history:
        history_df = pd.DataFrame(
            sync_history,
            columns=["ID", "Email", "Cardskipper ID", "IVMS ID", "Previous End Date", "New End Date", "Status", "Timestamp"]
        )
        st.dataframe(history_df, hide_index=True)
    else:
        st.info("No sync operations have been performed yet.")
    
    # Show sync errors
    st.markdown("### Sync Errors", unsafe_allow_html=True)
    sync_errors = db.get_sync_errors(limit=10)
    
    if sync_errors:
        error_df = pd.DataFrame(
            sync_errors,
            columns=["ID", "Email", "Error Message", "Timestamp", "Resolved"]
        )
        error_df["Resolved"] = error_df["Resolved"].map({0: "No", 1: "Yes"})
        st.dataframe(error_df, hide_index=True)
    else:
        st.success("No errors found. All systems operating normally.")


def show_cardskipper_members(cardskipper):
    """Display Cardskipper members."""
    st.markdown("## Cardskipper Members", unsafe_allow_html=True)
    st.markdown("This section simulates the Cardskipper membership system. You can view all active members and extend memberships.")
    
    active_members = cardskipper.get_active_members()
    
    # Convert to DataFrame for display
    if active_members:
        df = pd.DataFrame([
            {
                "Name": f"{m['first_name']} {m['last_name']}",
                "Email": m['email'],
                "Membership": m['role_name'],
                "Valid From": m['start_date'],
                "Valid Until": m['end_date'],
                "ID": m['organization_member_id']
            }
            for m in active_members
        ])
        
        st.dataframe(df, hide_index=True)
        
        # Member selection for extension
        st.markdown("### Extend Membership", unsafe_allow_html=True)
        st.markdown("Select a member and extend their membership to simulate a membership renewal.")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            selected_email = st.selectbox(
                "Select Member", 
                options=[m["email"] for m in active_members],
                format_func=lambda x: next((f"{m['first_name']} {m['last_name']} ({x})" for m in active_members if m["email"] == x), x)
            )
        
        with col2:
            extension_days = st.number_input("Days to Extend", min_value=1, max_value=365, value=30, step=1)
        
        if st.button("Extend Membership", type="primary"):
            with st.spinner("Extending membership..."):
                result = cardskipper.extend_membership(selected_email, extension_days)
                
                if result["success"]:
                    st.success(result["message"])
                    st.markdown(f"""
                    **Member:** {result['member']['name']}  
                    **Old end date:** {result['old_end_date']}  
                    **New end date:** {result['new_end_date']}
                    """)
                else:
                    st.error(result["message"])
    else:
        st.info("No active members found in Cardskipper.")


def show_ivms_users(ivms):
    """Display IVMS users."""
    st.markdown("## IVMS Users", unsafe_allow_html=True)
    st.markdown("This section simulates the IVMS access control system. You can view all users and their validity periods.")
    
    users = ivms.get_all_users()
    
    # Convert to DataFrame for display
    if users:
        df = pd.DataFrame([
            {
                "Employee No": u['employeeNo'],
                "Name": u['name'],
                "Email": u.get('email', ''),
                "Valid From": u['Valid']['beginTime'],
                "Valid Until": u['Valid']['endTime'],
                "Status": "Active" if u['Valid']['enable'] else "Inactive"
            }
            for u in users
        ])
        
        st.dataframe(df, hide_index=True)
    else:
        st.info("No users found in IVMS.")


def show_sync_controls(sync_service):
    """Display synchronization controls."""
    st.markdown("## Synchronization", unsafe_allow_html=True)
    st.markdown("This section allows you to manually trigger the synchronization process.")
    
    if st.button("Run Synchronization", type="primary"):
        with st.spinner("Running synchronization..."):
            # Add a small delay to simulate processing
            time.sleep(2)
            result = sync_service.sync()
            
            if result["success"]:
                st.success(result["message"])
                st.markdown(f"""
                **Total members processed:** {result['total_members']}  
                **Updates needed:** {result['updates_needed']}  
                **Updates completed:** {result['updates_completed']}
                """)
            else:
                st.error(result["message"])


def main():
    """Main application function."""
    # Initialize demo environment
    cardskipper, ivms, db, sync_service = initialize_demo()
    
    try:
        # Display header
        show_header()
        
        # Create tabs
        tab1, tab2, tab3, tab4 = st.tabs(["Dashboard", "Cardskipper Members", "IVMS Users", "Synchronization"])
        
        with tab1:
            show_dashboard(db, sync_service)
        
        with tab2:
            show_cardskipper_members(cardskipper)
        
        with tab3:
            show_ivms_users(ivms)
        
        with tab4:
            show_sync_controls(sync_service)
    
    finally:
        # Close database connection
        db.close()


if __name__ == "__main__":
    main()