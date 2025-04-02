#!/usr/bin/env python3
"""
Final mock implementation of Cardskipper to IVMS integration.
This script uses the exact data structure from both Cardskipper and IVMS examples.
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
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("mock_integration_final.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("MockIntegrationFinal")

# Path for mock data
MOCK_DATA_DIR = "mock_data"
if not os.path.exists(MOCK_DATA_DIR):
    os.makedirs(MOCK_DATA_DIR)

# Mock Cardskipper data
CARDSKIPPER_MEMBERS_FILE = os.path.join(MOCK_DATA_DIR, "cardskipper_members_final.json")
# Mock IVMS data
IVMS_USERS_FILE = os.path.join(MOCK_DATA_DIR, "ivms_users_final.json")
# SQLite database for integration
DB_FILE = os.path.join(MOCK_DATA_DIR, "integration_final.db")

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
                    ivms_employee_no TEXT,
                    member_code TEXT,
                    role_id TEXT,
                    role_name TEXT,
                    phone TEXT
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
            logger.error(f"Error getting members from database: {e}")
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
            self.cursor.execute("SELECT email FROM members WHERE email = ?", (email,))
            existing_member = self.cursor.fetchone()
            
            if existing_member:
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
            
            self.conn.commit()
            logger.info(f"Updated member in database: {email}")
        except Exception as e:
            logger.error(f"Error updating member in database: {e}")
            self.conn.rollback()
    
    def get_ivms_employee_no(self, email):
        try:
            self.cursor.execute("SELECT ivms_employee_no FROM members WHERE email = ?", (email,))
            result = self.cursor.fetchone()
            return result[0] if result and result[0] else None
        except Exception as e:
            logger.error(f"Error getting IVMS employee number for {email}: {e}")
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
    
    def generate_mock_member_code(self, length=6):
        """Generate a random member code."""
        chars = string.ascii_lowercase + string.digits
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
        
        # Generate additional members
        for i in range(8, 21):
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
            member_code = self.generate_mock_member_code()
            
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
            
            # Generate dates based on role
            if role["Type"] == "Student":
                # Student memberships often aligned with school year
                start_date = f"2024-09-01T00:00:00"
                end_date = f"2025-06-30T23:59:59"
            else:
                # Regular memberships have different durations
                start_month = random.randint(1, 12)
                start_day = random.randint(1, 28)
                start_date = f"2024-{start_month:02d}-{start_day:02d}T00:00:00"
                
                # Duration based on role
                if role["Name"] == "Mesečna":
                    # Monthly membership
                    end_month = start_month + 1
                    end_year = 2024
                    if end_month > 12:
                        end_month = 1
                        end_year = 2025
                elif role["Name"] == "24/7":
                    # Annual membership
                    end_month = start_month
                    end_day = start_day
                    end_year = 2025
                else:
                    # Other memberships (3-6 months)
                    duration = random.choice([3, 6])
                    end_month = start_month + duration
                    end_year = 2024
                    if end_month > 12:
                        end_month = end_month - 12
                        end_year = 2025
                
                end_date = f"{end_year}-{end_month:02d}-{start_day:02d}T23:59:59"
            
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
            
            # Add Extra field for some members
            if i % 3 == 0:
                member["Extra"] = {
                    "Extra1": f"Note {i}",
                    "Extra2": "",
                    "Extra3": ""
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
    """Mock IVMS API with sample data based on the provided example."""
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
        """Generate mock IVMS user data based on the example."""
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
        
        # Generate some additional mock users that don't have matches in Cardskipper
        for i in range(58, 65):
            employee_no = f"{i:08d}"
            
            # Sample Slovenian names
            first_names = ["Matjaž", "Simon", "Gregor", "Aleš", "Boštjan", "Tomaž", "Tanja", "Nataša"]
            last_names = ["Petek", "Hribar", "Kos", "Košir", "Bizjak", "Jerman", "Božič"]
            
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            name = f"{first_name} {last_name}"
            
            # Other user attributes
            gender = random.choice(["male", "female"])
            email = f"{first_name.lower()}.{last_name.lower()}@example.com"
            phone = f"+3867{random.randint(1000000, 9999999)}" if random.random() > 0.2 else ""
            
            # Validity dates (some in the past, some in the future)
            if random.random() > 0.3:
                # Active user
                begin_time = (datetime.now() - timedelta(days=random.randint(30, 180))).strftime("%Y-%m-%dT%H:%M:%S")
                end_time = (datetime.now() + timedelta(days=random.randint(30, 180))).strftime("%Y-%m-%dT%H:%M:%S")
                enable = True
            else:
                # Expired user
                begin_time = (datetime.now() - timedelta(days=random.randint(180, 365))).strftime("%Y-%m-%dT%H:%M:%S")
                end_time = (datetime.now() - timedelta(days=random.randint(1, 30))).strftime("%Y-%m-%dT%H:%M:%S")
                enable = False
            
            # Create user
            user = {
                "employeeNo": employee_no,
                "name": name,
                "gender": gender,
                "email": email,
                "phoneNo": phone,
                "Valid": {
                    "enable": enable,
                    "beginTime": begin_time,
                    "endTime": end_time
                }
            }
            
            users.append(user)
        
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
                    ivms_employee_no = None
                    
                    # Check if member exists in our database
                    if email in db_members:
                        db_member = db_members[email]
                        db_end_date = db_member["end_date"]
                        
                        # If end date has changed, we need to update
                        if db_end_date != member["end_date"]:
                            needs_update = True
                            logger.info(f"Member {email} needs update: end date changed from {db_end_date} to {member['end_date']}")
                        
                        # Get IVMS employee number from database
                        ivms_employee_no = db_member["ivms_employee_no"]
                    else:
                        # New member, needs update
                        needs_update = True
                        logger.info(f"New member found: {email}")
                    
                    # If we don't have an IVMS employee number yet, try to find one
                    if not ivms_employee_no and email in email_to_user_id:
                        ivms_employee_no = email_to_user_id[email]
                        logger.info(f"Found IVMS employee number for {email}: {ivms_employee_no}")
                    
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
                    logger.error(f"Error processing member {member.get('email', 'unknown')}: {e}")
            
            # Perform IVMS updates
            for update in updates_needed:
                success = self.ivms.update_user_validity(
                    update["ivms_employee_no"],
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
    old_end_date = None
    for member in cardskipper.members:
        if member["ContactInfo"]["EMail"] == email:
            role = member["Organisations"]["Organisation"]["Roles"]["Role"]
            old_end_date = role["EndDate"]
            break
    
    if not old_end_date:
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
                
                logger.info("=" * 50)
                logger.info("MEMBERSHIP EXTENSION SIMULATION")
                logger.info("=" * 50)
                logger.info(f"Extended membership for: {member['Firstname']} {member['Lastname']}")
                logger.info(f"Email: {email}")
                logger.info(f"Membership: {role['Name']}")
                logger.info(f"Old end date: {old_end_date}")
                logger.info(f"New end date: {new_end_date}")
                logger.info(f"Extended by: {days_to_extend} days")
                logger.info("=" * 50)
                return True
    
    return False


def run_simulation(num_cycles=3, interval_seconds=5):
    """Run a simulation of the integration."""
    try:
        logger.info("\n" + "=" * 80)
        logger.info("STARTING CARDSKIPPER TO IVMS INTEGRATION SIMULATION")
        logger.info("=" * 80 + "\n")
        
        # Initialize components
        cardskipper = MockCardskipper(CARDSKIPPER_MEMBERS_FILE)
        ivms = MockIVMS(IVMS_USERS_FILE)
        db = MockDatabase(DB_FILE)
        
        # Print initial status
        logger.info("Initial system status:")
        logger.info(f"- Cardskipper members: {len(cardskipper.members)}")
        active_members = cardskipper.get_active_members()
        logger.info(f"- Cardskipper active members: {len(active_members)}")
        logger.info(f"- IVMS users: {len(ivms.user_info)}")
        
        # Create sync service
        sync_service = MockSyncService(cardskipper, ivms, db)
        
        # Initial sync
        logger.info("\nPerforming initial synchronization...")
        sync_service.sync()
        
        # Run simulation cycles
        for cycle in range(1, num_cycles + 1):
            logger.info(f"\nStarting simulation cycle {cycle}...")
            
            # Simulate a membership extension
            if simulate_membership_extension():
                logger.info("Membership extension simulated successfully")
            else:
                logger.warning("Failed to simulate membership extension")
            
            # Wait for the specified interval
            logger.info(f"Waiting {interval_seconds} seconds before next sync...")
            time.sleep(interval_seconds)
            
            # Perform synchronization
            logger.info(f"Performing synchronization cycle {cycle}...")
            sync_service.sync()
        
        logger.info("\nSimulation completed successfully")
        
        # Print final status
        logger.info("\n" + "=" * 50)
        logger.info("FINAL STATUS REPORT")
        logger.info("=" * 50)
        active_members = cardskipper.get_active_members()
        logger.info(f"Cardskipper active members: {len(active_members)}")
        ivms_users = ivms.get_all_users()
        logger.info(f"IVMS users: {len(ivms_users)}")
        db_members = db.get_all_members()
        logger.info(f"Database members: {len(db_members)}")
        
        # Count members with IVMS IDs
        synced_count = sum(1 for member in db_members.values() if member["ivms_employee_no"])
        logger.info(f"Members synced with IVMS: {synced_count}")
        
        # Sample of synced members
        logger.info("\nSample of members synced with IVMS:")
        synced_members = [m for m in db_members.values() if m["ivms_employee_no"]]
        
        for i, member in enumerate(synced_members[:5]):
            logger.info(f"\n{i+1}. {member['first_name']} {member['last_name']}")
            logger.info(f"   Email: {member['email']}")
            logger.info(f"   Cardskipper ID: {member['organization_member_id']}")
            logger.info(f"   IVMS Employee No: {member['ivms_employee_no']}")
            logger.info(f"   Role: {member['role_name']}")
            logger.info(f"   Valid until: {member['end_date']}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error during simulation: {e}")
        return False
    finally:
        if 'db' in locals():
            db.close()


if __name__ == "__main__":
    run_simulation(num_cycles=3, interval_seconds=3)