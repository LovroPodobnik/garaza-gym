#!/usr/bin/env python3
"""
Test script for Cardskipper to IVMS integration.
This script tests the connection to both APIs and performs basic operations.
"""

import requests
import base64
import xml.etree.ElementTree as ET
from datetime import datetime
import logging
import argparse
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("test_integration.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("CardskipperIVMSTest")

class TestConfig:
    """Configuration for the test script."""
    # Cardskipper configuration
    CARDSKIPPER_API_URL = "https://api-test.cardskipper.se"  # Using test environment
    CARDSKIPPER_USERNAME = ""
    CARDSKIPPER_PASSWORD = ""
    CARDSKIPPER_ORGANIZATION_ID = 0
    
    # IVMS configuration
    IVMS_DEVICE_IP = ""
    IVMS_PORT = "80"
    IVMS_USERNAME = "admin"
    IVMS_PASSWORD = ""

def test_cardskipper_connection(config):
    """Test connection to Cardskipper API."""
    try:
        logger.info("Testing Cardskipper API connection...")
        
        # Create session with basic auth
        session = requests.Session()
        session.auth = (config.CARDSKIPPER_USERNAME, config.CARDSKIPPER_PASSWORD)
        
        # Test retrieving countries (simple endpoint)
        response = session.get(f"{config.CARDSKIPPER_API_URL}/Basedata/Country/")
        
        if response.status_code != 200:
            logger.error(f"Failed to connect to Cardskipper API: {response.status_code} - {response.text}")
            return False
        
        logger.info("Successfully connected to Cardskipper API!")
        logger.info(f"Response: {response.text[:100]}...")  # Show first 100 chars
        return True
    
    except Exception as e:
        logger.error(f"Error testing Cardskipper API connection: {e}")
        return False

def test_cardskipper_member_search(config):
    """Test member search on Cardskipper API."""
    try:
        logger.info("Testing Cardskipper member search...")
        
        # Create session with basic auth
        session = requests.Session()
        session.auth = (config.CARDSKIPPER_USERNAME, config.CARDSKIPPER_PASSWORD)
        
        # Prepare XML for member search
        search_xml = f"""<?xml version="1.0" encoding="utf-8"?>
        <SearchCriteriaMember xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema">
            <OrganisationId>{config.CARDSKIPPER_ORGANIZATION_ID}</OrganisationId>
            <OnlyActive>true</OnlyActive>
        </SearchCriteriaMember>"""
        
        # Make the request
        response = session.post(
            f"{config.CARDSKIPPER_API_URL}/Member/Export/",
            headers={"Content-Type": "application/xml"},
            data=search_xml
        )
        
        if response.status_code != 200:
            logger.error(f"Failed to search for members: {response.status_code} - {response.text}")
            return False
        
        # Parse the XML response
        root = ET.fromstring(response.content)
        
        # Count members
        members = root.findall(".//Member")
        member_count = len(members)
        
        logger.info(f"Found {member_count} active members")
        
        # If we found members, display first member's details
        if member_count > 0:
            first_member = members[0]
            first_name = first_member.find("Firstname").text if first_member.find("Firstname") is not None else "Unknown"
            last_name = first_member.find("Lastname").text if first_member.find("Lastname") is not None else "Unknown"
            
            logger.info(f"First member: {first_name} {last_name}")
        
        return True
    
    except Exception as e:
        logger.error(f"Error testing Cardskipper member search: {e}")
        return False

def test_ivms_connection(config):
    """Test connection to IVMS API."""
    try:
        logger.info("Testing IVMS API connection...")
        
        # Create base64 encoded basic auth string
        auth_str = f"{config.IVMS_USERNAME}:{config.IVMS_PASSWORD}"
        auth_bytes = auth_str.encode('ascii')
        base64_bytes = base64.b64encode(auth_bytes)
        base64_auth = base64_bytes.decode('ascii')
        
        headers = {
            "Content-Type": "application/xml",
            "Authorization": f"Basic {base64_auth}"
        }
        
        # Test searching users
        search_xml = """
        <UserInfoSearch>
            <searchID>1</searchID>
            <searchResultPosition>0</searchResultPosition>
            <maxResults>10</maxResults>
        </UserInfoSearch>
        """
        
        ivms_url = f"http://{config.IVMS_DEVICE_IP}:{config.IVMS_PORT}"
        response = requests.post(
            f"{ivms_url}/ISAPI/AccessControl/UserInfo/search",
            headers=headers,
            data=search_xml
        )
        
        if response.status_code != 200:
            logger.error(f"Failed to connect to IVMS API: {response.status_code} - {response.text}")
            return False
        
        # Parse the XML response
        root = ET.fromstring(response.content)
        
        # Count users
        users = root.findall(".//UserInfo")
        user_count = len(users)
        
        logger.info(f"Successfully connected to IVMS API! Found {user_count} users.")
        
        # If we found users, display first user's details
        if user_count > 0:
            first_user = users[0]
            employee_no = first_user.find("employeeNo").text if first_user.find("employeeNo") is not None else "Unknown"
            name = first_user.find("name").text if first_user.find("name") is not None else "Unknown"
            
            logger.info(f"First user: {name} (Employee No: {employee_no})")
        
        return True
    
    except Exception as e:
        logger.error(f"Error testing IVMS API connection: {e}")
        return False

def test_update_user_validity(config):
    """Test updating a user's validity in IVMS."""
    try:
        logger.info("Testing updating user validity in IVMS (simulation only)...")
        
        # IMPORTANT: This function just demonstrates the API call structure
        # It does not actually modify any users
        
        # Create base64 encoded basic auth string
        auth_str = f"{config.IVMS_USERNAME}:{config.IVMS_PASSWORD}"
        auth_bytes = auth_str.encode('ascii')
        base64_bytes = base64.b64encode(auth_bytes)
        base64_auth = base64_bytes.decode('ascii')
        
        headers = {
            "Content-Type": "application/xml",
            "Authorization": f"Basic {base64_auth}"
        }
        
        # Sample user ID - would come from your search or matching
        sample_user_id = "12345"  # This should be replaced with a real user ID
        
        # Sample dates
        start_date = datetime.now()
        end_date = datetime(2025, 12, 31, 23, 59, 59)
        
        # Format dates in the format expected by IVMS
        start_date_str = start_date.strftime("%Y-%m-%dT%H:%M:%S")
        end_date_str = end_date.strftime("%Y-%m-%dT%H:%M:%S")
        
        # Create the XML for update
        update_xml = f"""
        <UserInfo>
            <employeeNo>{sample_user_id}</employeeNo>
            <Valid>
                <beginTime>{start_date_str}</beginTime>
                <endTime>{end_date_str}</endTime>
            </Valid>
        </UserInfo>
        """
        
        logger.info("XML that would be sent for update:")
        logger.info(update_xml)
        
        # This is what the actual API call would look like:
        # ivms_url = f"http://{config.IVMS_DEVICE_IP}:{config.IVMS_PORT}"
        # response = requests.put(
        #     f"{ivms_url}/ISAPI/AccessControl/UserInfo/modify",
        #     headers=headers,
        #     data=update_xml
        # )
        
        logger.info("Update simulation completed (no actual changes were made)")
        return True
    
    except Exception as e:
        logger.error(f"Error in update simulation: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Test Cardskipper to IVMS integration')
    parser.add_argument('--cardskipper-username', required=True, help='Cardskipper username')
    parser.add_argument('--cardskipper-password', required=True, help='Cardskipper password')
    parser.add_argument('--organization-id', required=True, type=int, help='Cardskipper organization ID')
    parser.add_argument('--ivms-ip', required=True, help='IVMS device IP address')
    parser.add_argument('--ivms-password', required=True, help='IVMS admin password')
    parser.add_argument('--ivms-port', default='80', help='IVMS device port (default: 80)')
    parser.add_argument('--test', choices=['all', 'cardskipper', 'ivms'], default='all', 
                        help='Which tests to run (default: all)')
    
    args = parser.parse_args()
    
    # Set up configuration
    config = TestConfig()
    config.CARDSKIPPER_USERNAME = args.cardskipper_username
    config.CARDSKIPPER_PASSWORD = args.cardskipper_password
    config.CARDSKIPPER_ORGANIZATION_ID = args.organization_id
    config.IVMS_DEVICE_IP = args.ivms_ip
    config.IVMS_PASSWORD = args.ivms_password
    config.IVMS_PORT = args.ivms_port
    
    logger.info("Starting Cardskipper to IVMS integration tests")
    
    success = True
    
    if args.test in ['all', 'cardskipper']:
        cardskipper_conn_ok = test_cardskipper_connection(config)
        if cardskipper_conn_ok:
            cardskipper_search_ok = test_cardskipper_member_search(config)
            success = success and cardskipper_search_ok
        else:
            success = False
    
    if args.test in ['all', 'ivms']:
        ivms_conn_ok = test_ivms_connection(config)
        if ivms_conn_ok:
            ivms_update_ok = test_update_user_validity(config)
            success = success and ivms_update_ok
        else:
            success = False
    
    if success:
        logger.info("All tests completed successfully!")
        return 0
    else:
        logger.error("One or more tests failed. See log for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())