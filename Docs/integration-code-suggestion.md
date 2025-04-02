import requests
import base64
import json
import sqlite3
import logging
import time
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Dict, List, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("cardskipper_ivms_sync.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("CardskipperIVMSSync")

# Configuration
class Config:
    # Cardskipper configuration
    CARDSKIPPER_API_URL = "https://api.cardskipper.se"  # or test URL: https://api-test.cardskipper.se
    CARDSKIPPER_USERNAME = "your_username"
    CARDSKIPPER_PASSWORD = "your_password"
    CARDSKIPPER_ORGANIZATION_ID = 123  # Replace with your organization ID
    
    # IVMS configuration
    IVMS_DEVICE_IP = "192.168.1.100"  # Replace with your device IP
    IVMS_PORT = "80"  # Replace with your device port
    IVMS_USERNAME = "admin"  # Replace with your IVMS admin username
    IVMS_PASSWORD = "password"  # Replace with your IVMS admin password
    
    # Sync configuration
    POLL_INTERVAL_SECONDS = 300  # Poll every 5 minutes

    # Database configuration
    DB_PATH = "cardskipper_ivms_sync.db"
    
    @classmethod
    def get_ivms_base_url(cls) -> str:
        return f"http://{cls.IVMS_DEVICE_IP}:{cls.IVMS_PORT}"
    
    @classmethod
    def get_ivms_auth_header(cls) -> Dict[str, str]:
        # Create base64 encoded basic auth string
        auth_str = f"{cls.IVMS_USERNAME}:{cls.IVMS_PASSWORD}"
        auth_bytes = auth_str.encode('ascii')
        base64_bytes = base64.b64encode(auth_bytes)
        base64_auth = base64_bytes.decode('ascii')
        
        return {
            "Content-Type": "application/xml",
            "Authorization": f"Basic {base64_auth}"
        }

# Member model
class Member:
    def __init__(self, email: str, organization_member_id: str, 
                 start_date: datetime, end_date: datetime,
                 first_name: str = "", last_name: str = ""):
        self.email = email
        self.organization_member_id = organization_member_id
        self.start_date = start_date
        self.end_date = end_date
        self.first_name = first_name
        self.last_name = last_name
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email}): valid until {self.end_date}"

# Database Manager
class DatabaseManager:
    def __init__(self, db_path: str):
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
    
    def get_all_members(self) -> Dict[str, Dict]:
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
    
    def update_member(self, member: Member, ivms_user_id: Optional[str] = None):
        try:
            # Check if the member exists
            self.cursor.execute("SELECT email FROM members WHERE email = ?", (member.email,))
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
                        member.organization_member_id, 
                        member.start_date.isoformat(), 
                        member.end_date.isoformat(),
                        member.first_name,
                        member.last_name,
                        ivms_user_id,
                        member.email
                    ))
                else:
                    self.cursor.execute("""
                        UPDATE members 
                        SET organization_member_id = ?, start_date = ?, end_date = ?, 
                            first_name = ?, last_name = ?
                        WHERE email = ?
                    """, (
                        member.organization_member_id, 
                        member.start_date.isoformat(), 
                        member.end_date.isoformat(),
                        member.first_name,
                        member.last_name,
                        member.email
                    ))
            else:
                # Insert new member
                self.cursor.execute("""
                    INSERT INTO members (email, organization_member_id, start_date, end_date, first_name, last_name, ivms_user_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    member.email, 
                    member.organization_member_id, 
                    member.start_date.isoformat(), 
                    member.end_date.isoformat(),
                    member.first_name,
                    member.last_name,
                    ivms_user_id
                ))
            
            self.conn.commit()
            logger.info(f"Updated member in database: {member.email}")
        except Exception as e:
            logger.error(f"Error updating member in database: {e}")
            self.conn.rollback()
    
    def get_ivms_user_id(self, email: str) -> Optional[str]:
        try:
            self.cursor.execute("SELECT ivms_user_id FROM members WHERE email = ?", (email,))
            result = self.cursor.fetchone()
            return result[0] if result else None
        except Exception as e:
            logger.error(f"Error getting IVMS user ID for {email}: {e}")
            return None

# Cardskipper API Client
class CardskipperClient:
    def __init__(self, api_url: str, username: str, password: str):
        self.api_url = api_url
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.session.auth = (username, password)
    
    def get_active_members(self, organization_id: int) -> List[Member]:
        try:
            # Prepare the XML for member search
            search_xml = f"""<?xml version="1.0" encoding="utf-8"?>
            <SearchCriteriaMember xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema">
                <OrganisationId>{organization_id}</OrganisationId>
                <OnlyActive>true</OnlyActive>
            </SearchCriteriaMember>"""
            
            # Make the request to search for members
            response = self.session.post(
                f"{self.api_url}/Member/Export/",
                headers={"Content-Type": "application/xml"},
                data=search_xml
            )
            
            if response.status_code != 200:
                logger.error(f"Failed to get members: {response.status_code} - {response.text}")
                return []
            
            # Parse the XML response
            root = ET.fromstring(response.content)
            
            members = []
            # Iterate through all member elements
            for member_elem in root.findall(".//Member"):
                try:
                    # Get basic member info
                    first_name = member_elem.find("Firstname").text if member_elem.find("Firstname") is not None else ""
                    last_name = member_elem.find("Lastname").text if member_elem.find("Lastname") is not None else ""
                    org_member_id = member_elem.find("OrganisationMemberId").text if member_elem.find("OrganisationMemberId") is not None else ""
                    
                    # Get email from contact info
                    contact_info = member_elem.find("ContactInfo")
                    email = contact_info.find("EMail").text if contact_info is not None and contact_info.find("EMail") is not None else ""
                    
                    if not email:
                        logger.warning(f"Member {first_name} {last_name} has no email address, skipping")
                        continue
                    
                    # Get membership dates from roles
                    organisations = member_elem.find("Organisations")
                    if organisations is None:
                        logger.warning(f"Member {first_name} {last_name} has no organizations, skipping")
                        continue
                    
                    organisation = organisations.find(f"Organisation[Id='{organization_id}']")
                    if organisation is None:
                        logger.warning(f"Member {first_name} {last_name} is not in organization {organization_id}, skipping")
                        continue
                    
                    roles = organisation.find("Roles")
                    if roles is None or len(roles.findall("Role")) == 0:
                        logger.warning(f"Member {first_name} {last_name} has no roles in organization {organization_id}, skipping")
                        continue
                    
                    # Get the latest end date across all roles
                    latest_end_date = None
                    earliest_start_date = None
                    
                    for role in roles.findall("Role"):
                        start_date_str = role.find("StartDate").text if role.find("StartDate") is not None else None
                        end_date_str = role.find("EndDate").text if role.find("EndDate") is not None else None
                        
                        if start_date_str:
                            start_date = datetime.fromisoformat(start_date_str.replace('Z', '+00:00'))
                            if earliest_start_date is None or start_date < earliest_start_date:
                                earliest_start_date = start_date
                        
                        if end_date_str:
                            end_date = datetime.fromisoformat(end_date_str.replace('Z', '+00:00'))
                            if latest_end_date is None or end_date > latest_end_date:
                                latest_end_date = end_date
                    
                    if latest_end_date is None or earliest_start_date is None:
                        logger.warning(f"Member {first_name} {last_name} has invalid dates, skipping")
                        continue
                    
                    # Create member object
                    member = Member(
                        email=email,
                        organization_member_id=org_member_id,
                        first_name=first_name,
                        last_name=last_name,
                        start_date=earliest_start_date,
                        end_date=latest_end_date
                    )
                    
                    members.append(member)
                    
                except Exception as e:
                    logger.error(f"Error parsing member data: {e}")
            
            logger.info(f"Retrieved {len(members)} active members from Cardskipper")
            return members
            
        except Exception as e:
            logger.error(f"Error getting active members: {e}")
            return []

# IVMS API Client
class IVMSClient:
    def __init__(self, base_url: str, headers: Dict[str, str]):
        self.base_url = base_url
        self.headers = headers
    
    def search_users(self) -> Dict[str, str]:
        try:
            search_xml = """
            <UserInfoSearch>
                <searchID>1</searchID>
                <searchResultPosition>0</searchResultPosition>
                <maxResults>1000</maxResults>
            </UserInfoSearch>
            """
            
            response = requests.post(
                f"{self.base_url}/ISAPI/AccessControl/UserInfo/search",
                headers=self.headers,
                data=search_xml
            )
            
            if response.status_code != 200:
                logger.error(f"Failed to search IVMS users: {response.status_code} - {response.text}")
                return {}
            
            # Parse the XML response to get user IDs and emails
            root = ET.fromstring(response.content)
            
            user_map = {}
            for user_info in root.findall(".//UserInfo"):
                try:
                    user_id = user_info.find("employeeNo").text if user_info.find("employeeNo") is not None else None
                    
                    # Email might be stored in different places depending on IVMS configuration
                    # Try different possible locations
                    email = None
                    
                    # Try in UserInfo/email
                    if user_info.find("email") is not None:
                        email = user_info.find("email").text
                    
                    # Try in UserInfo/extensionInfo
                    elif user_info.find("extensionInfo") is not None:
                        extension_info = user_info.find("extensionInfo")
                        if extension_info.find("email") is not None:
                            email = extension_info.find("email").text
                    
                    if user_id and email:
                        user_map[email] = user_id
                
                except Exception as e:
                    logger.error(f"Error parsing user info: {e}")
            
            logger.info(f"Retrieved {len(user_map)} users from IVMS")
            return user_map
            
        except Exception as e:
            logger.error(f"Error searching IVMS users: {e}")
            return {}
    
    def update_user_validity(self, user_id: str, start_date: datetime, end_date: datetime) -> bool:
        try:
            # Format dates in the format expected by IVMS
            start_date_str = start_date.strftime("%Y-%m-%dT%H:%M:%S")
            end_date_str = end_date.strftime("%Y-%m-%dT%H:%M:%S")
            
            update_xml = f"""
            <UserInfo>
                <employeeNo>{user_id}</employeeNo>
                <Valid>
                    <beginTime>{start_date_str}</beginTime>
                    <endTime>{end_date_str}</endTime>
                </Valid>
            </UserInfo>
            """
            
            response = requests.put(
                f"{self.base_url}/ISAPI/AccessControl/UserInfo/modify",
                headers=self.headers,
                data=update_xml
            )
            
            if response.status_code != 200:
                logger.error(f"Failed to update user validity: {response.status_code} - {response.text}")
                return False
            
            logger.info(f"Successfully updated validity for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating user validity: {e}")
            return False

# Main Synchronization Service
class CardskipperIVMSSync:
    def __init__(self, config: Config):
        self.config = config
        self.db_manager = DatabaseManager(config.DB_PATH)
        self.cardskipper_client = CardskipperClient(
            config.CARDSKIPPER_API_URL,
            config.CARDSKIPPER_USERNAME,
            config.CARDSKIPPER_PASSWORD
        )
        self.ivms_client = IVMSClient(
            config.get_ivms_base_url(),
            config.get_ivms_auth_header()
        )
    
    def sync(self):
        try:
            logger.info("Starting synchronization")
            
            # Get all members from Cardskipper
            cardskipper_members = self.cardskipper_client.get_active_members(
                self.config.CARDSKIPPER_ORGANIZATION_ID
            )
            
            if not cardskipper_members:
                logger.warning("No members retrieved from Cardskipper, stopping sync")
                return
            
            # Get all members from local database
            db_members = self.db_manager.get_all_members()
            
            # Get all users from IVMS
            ivms_users = self.ivms_client.search_users()
            
            # Process each member from Cardskipper
            for member in cardskipper_members:
                try:
                    # Check if we need to update this member
                    needs_update = False
                    ivms_user_id = None
                    
                    # Check if member exists in our database
                    if member.email in db_members:
                        db_member = db_members[member.email]
                        db_end_date = datetime.fromisoformat(db_member["end_date"])
                        
                        # If end date has changed, we need to update
                        if db_end_date != member.end_date:
                            needs_update = True
                            logger.info(f"Member {member.email} needs update: end date changed from {db_end_date} to {member.end_date}")
                        
                        # Get IVMS user ID from database
                        ivms_user_id = db_member["ivms_user_id"]
                    else:
                        # New member, needs update
                        needs_update = True
                        logger.info(f"New member found: {member.email}")
                    
                    # If we don't have an IVMS user ID yet, try to find one
                    if not ivms_user_id and member.email in ivms_users:
                        ivms_user_id = ivms_users[member.email]
                        logger.info(f"Found IVMS user ID for {member.email}: {ivms_user_id}")
                    
                    # Update member in our database
                    self.db_manager.update_member(member, ivms_user_id)
                    
                    # If member needs update and we have an IVMS user ID, update IVMS
                    if needs_update and ivms_user_id:
                        success = self.ivms_client.update_user_validity(
                            ivms_user_id,
                            member.start_date,
                            member.end_date
                        )
                        
                        if success:
                            logger.info(f"Successfully updated IVMS for member {member.email}")
                        else:
                            logger.error(f"Failed to update IVMS for member {member.email}")
                    elif needs_update and not ivms_user_id:
                        logger.warning(f"Member {member.email} needs update but no IVMS user ID found")
                
                except Exception as e:
                    logger.error(f"Error processing member {member.email}: {e}")
            
            logger.info("Synchronization completed")
            
        except Exception as e:
            logger.error(f"Error during synchronization: {e}")
        
    def run_forever(self):
        try:
            logger.info(f"Starting CardskipperIVMSSync service, polling every {self.config.POLL_INTERVAL_SECONDS} seconds")
            
            while True:
                try:
                    self.sync()
                except Exception as e:
                    logger.error(f"Error during sync cycle: {e}")
                
                time.sleep(self.config.POLL_INTERVAL_SECONDS)
        
        except KeyboardInterrupt:
            logger.info("Service stopped by user")
        finally:
            self.db_manager.close()
            logger.info("Service stopped")

# Main entry point
if __name__ == "__main__":
    sync_service = CardskipperIVMSSync(Config)
    sync_service.run_forever()
