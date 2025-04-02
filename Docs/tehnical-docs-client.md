# Cardskipper to IVMS Integration - Technical Documentation

## Project Overview

This document provides detailed technical specifications for developing an integration between Cardskipper membership system and Hikvision IVMS access control system. The integration will automatically synchronize membership validity dates from Cardskipper to IVMS.

## Integration Requirements

1. Monitor active users in Cardskipper for membership validity date changes
2. When changes occur, automatically update corresponding user records in IVMS
3. Use email addresses as the common identifier between systems
4. Store a local record of all synchronizations for audit and troubleshooting

## API Specifications

### 1. Cardskipper API

**Base URLs:**
- Production: `https://api.cardskipper.se`
- Test: `https://api-test.cardskipper.se`

**Authentication:**
- Basic Authentication (username/password)
- Requires administrator account with API access rights

**Key Endpoints:**

1. **Get Organization Info**
   - Path: `/Organisation/Info/`
   - Method: GET
   - Purpose: Retrieve organization and role information

2. **Member Search**
   - Path: `/Member/Export/`
   - Method: POST with XML body
   - Purpose: Retrieve active members with validity dates
   - Required XML format:
   ```xml
   <?xml version="1.0" encoding="utf-8"?>
   <SearchCriteriaMember xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema">
       <OrganisationId>[YOUR_ORGANIZATION_ID]</OrganisationId>
       <OnlyActive>true</OnlyActive>
   </SearchCriteriaMember>
   ```

### 2. IVMS API

**Base URL:**
- `http://<device_ip>:<port>/ISAPI/`

**Authentication:**
- Basic Authentication (username:password in Base64)
- Headers:
  - Content-Type: application/xml
  - Authorization: Basic [base64-encoded-credentials]

**Key Endpoints:**

1. **Search Users**
   - Path: `/ISAPI/AccessControl/UserInfo/search`
   - Method: POST
   - XML Body:
   ```xml
   <UserInfoSearch>
     <searchID>1</searchID>
     <searchResultPosition>0</searchResultPosition>
     <maxResults>100</maxResults>
   </UserInfoSearch>
   ```
   - Response: List of users with their IDs, names, and email addresses

2. **Update User Validity**
   - Path: `/ISAPI/AccessControl/UserInfo/modify`
   - Method: PUT
   - XML Body:
   ```xml
   <UserInfo>
     <employeeNo>[USER_ID]</employeeNo>
     <Valid>
       <enable>true</enable>
       <beginTime>[START_DATE]</beginTime>
       <endTime>[END_DATE]</endTime>
     </Valid>
   </UserInfo>
   ```
   - Date Format: YYYY-MM-DDThh:mm:ss (e.g., 2025-02-04T00:00:00)

## Implementation Steps

### 1. Setup and Authentication

```python
import requests
import base64
import xml.etree.ElementTree as ET

# IVMS Authentication
def get_ivms_auth_header(username, password):
    # Create base64 encoded basic auth string
    auth_str = f"{username}:{password}"
    auth_bytes = auth_str.encode('ascii')
    base64_bytes = base64.b64encode(auth_bytes)
    base64_auth = base64_bytes.decode('ascii')
    
    return {
        "Content-Type": "application/xml",
        "Authorization": f"Basic {base64_auth}"
    }

# Cardskipper Authentication
cardskipper_auth = (CARDSKIPPER_USERNAME, CARDSKIPPER_PASSWORD)
```

### 2. Retrieve IVMS Users

```python
def get_ivms_users(device_ip, port, headers):
    search_xml = """
    <UserInfoSearch>
        <searchID>1</searchID>
        <searchResultPosition>0</searchResultPosition>
        <maxResults>1000</maxResults>
    </UserInfoSearch>
    """
    
    url = f"http://{device_ip}:{port}/ISAPI/AccessControl/UserInfo/search"
    response = requests.post(url, headers=headers, data=search_xml)
    
    if response.status_code != 200:
        raise Exception(f"Failed to get IVMS users: {response.status_code} - {response.text}")
    
    # Parse XML response to extract user IDs and emails
    root = ET.fromstring(response.content)
    user_map = {}
    
    for user_info in root.findall(".//UserInfo"):
        employee_no = user_info.find("employeeNo").text if user_info.find("employeeNo") is not None else None
        email = user_info.find("email").text if user_info.find("email") is not None else None
        
        if employee_no and email:
            user_map[email.lower()] = employee_no
    
    return user_map
```

### 3. Retrieve Cardskipper Members

```python
def get_cardskipper_members(api_url, auth, organization_id):
    search_xml = f"""<?xml version="1.0" encoding="utf-8"?>
    <SearchCriteriaMember xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema">
        <OrganisationId>{organization_id}</OrganisationId>
        <OnlyActive>true</OnlyActive>
    </SearchCriteriaMember>"""
    
    response = requests.post(
        f"{api_url}/Member/Export/",
        auth=auth,
        headers={"Content-Type": "application/xml"},
        data=search_xml
    )
    
    if response.status_code != 200:
        raise Exception(f"Failed to get Cardskipper members: {response.status_code} - {response.text}")
    
    # Process the XML response to extract members with validity dates
    root = ET.fromstring(response.content)
    members = []
    
    # Parse member data including email and membership validity dates
    # (Implementation details omitted for brevity)
    
    return members
```

### 4. Update IVMS User Validity

```python
def update_ivms_user_validity(device_ip, port, headers, employee_no, start_date, end_date):
    # Format dates in the format expected by IVMS
    start_date_str = start_date.strftime("%Y-%m-%dT%H:%M:%S")
    end_date_str = end_date.strftime("%Y-%m-%dT%H:%M:%S")
    
    update_xml = f"""
    <UserInfo>
        <employeeNo>{employee_no}</employeeNo>
        <Valid>
            <enable>true</enable>
            <beginTime>{start_date_str}</beginTime>
            <endTime>{end_date_str}</endTime>
        </Valid>
    </UserInfo>
    """
    
    url = f"http://{device_ip}:{port}/ISAPI/AccessControl/UserInfo/modify"
    response = requests.put(url, headers=headers, data=update_xml)
    
    if response.status_code != 200:
        raise Exception(f"Failed to update user validity: {response.status_code} - {response.text}")
    
    return True
```

### 5. Refresh IVMS Device Data

After updating users via the API, it may be necessary to refresh the device data in the IVMS-4200 Control Panel:

1. Navigate to: IVMS-4200 Control Panel → Device Management 
2. Click "Refresh the device data"

## Synchronization Logic

1. Retrieve all active members from Cardskipper
2. Retrieve all users from IVMS
3. Match users between systems using email address
4. For each Cardskipper member:
   - Check if validity dates have changed since last sync
   - If changed, update the corresponding IVMS user
   - Record the update in local database for audit
5. Schedule this process to run at regular intervals (e.g., every 15 minutes)

## Error Handling

1. Log all API requests and responses for troubleshooting
2. Implement retry logic for transient errors
3. Send notifications for persistent failures
4. Store failed updates in a queue for manual resolution

## Testing Procedure

1. Create a test member in Cardskipper with a known email address
2. Verify the member exists in IVMS with the same email
3. Extend the membership validity in Cardskipper
4. Run the sync process manually
5. Verify the validity dates are updated in IVMS

## Security Considerations

1. Store all credentials securely (e.g., environment variables, secure vault)
2. Use HTTPS for Cardskipper API connections
3. Limit IP access to the IVMS API when possible
4. Implement authentication token rotation if supported

## Example Postman Configuration

For testing the IVMS API directly:

1. Create a new request in Postman
2. Set the URL to `http://<device_ip>:<port>/ISAPI/AccessControl/UserInfo/search` or `http://<device_ip>:<port>/ISAPI/AccessControl/UserInfo/modify`
3. Set the method to POST (search) or PUT (modify)
4. Add headers:
   - Content-Type: application/xml
   - Authorization: Basic [base64-encoded username:password]
5. Set the body to raw XML with the appropriate format
6. Send the request and verify the response

## Database Schema

Create a local database to track synchronization status:

```sql
CREATE TABLE sync_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL,
    cardskipper_id TEXT NOT NULL,
    ivms_id TEXT NOT NULL,
    previous_end_date TEXT,
    new_end_date TEXT,
    sync_status TEXT,
    sync_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE sync_errors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT,
    error_message TEXT,
    error_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved BOOLEAN DEFAULT FALSE
);
```

## Configuration Settings

Store these settings in a configuration file:

```ini
[Cardskipper]
API_URL = https://api.cardskipper.se
USERNAME = your_username
PASSWORD = your_password
ORGANIZATION_ID = 123

[IVMS]
DEVICE_IP = 192.168.1.100
PORT = 80
USERNAME = admin
PASSWORD = password

[Sync]
INTERVAL_MINUTES = 15
EMAIL_NOTIFICATIONS = true
NOTIFICATION_EMAIL = admin@example.com
```

## Deployment Instructions

1. Set up a dedicated server or container for the integration
2. Install Python 3.7+ with required dependencies
3. Configure the application with proper credentials
4. Set up a cron job or scheduler to run the sync at defined intervals
5. Implement logging to a centralized log management system
6. Set up monitoring and alerts for critical failures