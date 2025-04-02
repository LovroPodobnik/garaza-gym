# Cardskipper to IVMS Integration Implementation Guide

This guide provides detailed instructions for implementing and deploying the Cardskipper to IVMS integration solution.

## Prerequisites

Before starting the implementation, ensure you have:

1. **Cardskipper API access:**
   - Administrator account with API rights
   - Organization ID
   - API credentials (username and password)

2. **IVMS system:**
   - IP address and port of the IVMS device/server
   - Admin credentials
   - Users configured with email addresses matching Cardskipper

3. **Server environment:**
   - Python 3.7 or higher
   - Network access to both Cardskipper API and IVMS device
   - Ability to run a service 24/7

## Installation

1. **Set up a Python virtual environment**

   ```bash
   # Create a virtual environment
   python -m venv venv
   
   # Activate the virtual environment
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

2. **Install required packages**

   ```bash
   pip install requests
   ```

3. **Download the integration code**

   - Copy the `cardskipper_ivms_sync.py` script from this documentation
   - Or clone the repository if provided

4. **Configure the integration**

   Edit the `Config` class in the script to include your specific details:

   ```python
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
   ```

## Testing the Integration

Before deploying the full solution, it's recommended to test the connections:

1. **Run the test script**

   ```bash
   python test_integration_script.py \
     --cardskipper-username "your_username" \
     --cardskipper-password "your_password" \
     --organization-id 123 \
     --ivms-ip "192.168.1.100" \
     --ivms-password "password"
   ```

2. **Verify Cardskipper connectivity:**
   - The script should successfully connect to Cardskipper API
   - It should retrieve active members

3. **Verify IVMS connectivity:**
   - The script should successfully connect to IVMS API
   - It should retrieve user information

## Deployment

### Running as a Background Service

#### Linux (systemd)

1. **Create a service file:**

   ```bash
   sudo nano /etc/systemd/system/cardskipper-ivms.service
   ```

2. **Add the following content:**

   ```
   [Unit]
   Description=Cardskipper to IVMS Synchronization Service
   After=network.target
   
   [Service]
   User=your_username
   WorkingDirectory=/path/to/integration
   ExecStart=/path/to/integration/venv/bin/python /path/to/integration/cardskipper_ivms_sync.py
   Restart=always
   RestartSec=10
   
   [Install]
   WantedBy=multi-user.target
   ```

3. **Enable and start the service:**

   ```bash
   sudo systemctl enable cardskipper-ivms.service
   sudo systemctl start cardskipper-ivms.service
   ```

4. **Check the service status:**

   ```bash
   sudo systemctl status cardskipper-ivms.service
   ```

#### Windows

1. **Create a batch file (run.bat):**

   ```batch
   @echo off
   cd /d %~dp0
   call venv\Scripts\activate.bat
   python cardskipper_ivms_sync.py
   ```

2. **Create a scheduled task:**
   - Open Task Scheduler
   - Create a new task to run on system startup
   - Set the action to start the batch file
   - Configure to run with highest privileges
   - Set "Start in" to the directory containing the script

## Monitoring and Maintenance

### Logs

The integration logs all activities to both console and a log file:

```
cardskipper_ivms_sync.log
```

Check this file for:
- Sync operations
- API connection issues
- Member updates
- Errors and warnings

### Database

The integration maintains a SQLite database to track member states:

```
cardskipper_ivms_sync.db
```

This database contains:
- Member email addresses
- Cardskipper member IDs
- IVMS user IDs
- Validity dates

### Troubleshooting

Common issues and solutions:

1. **Authentication failures:**
   - Verify Cardskipper API credentials
   - Verify IVMS admin credentials
   - Check for special characters in passwords

2. **User matching issues:**
   - Ensure email addresses are consistent between systems
   - Check the IVMS user search response for where emails are stored

3. **Network connectivity:**
   - Verify network access to both APIs
   - Check firewall settings

## Security Considerations

1. **Credential protection:**
   - Consider using environment variables instead of hardcoding credentials
   - Restrict access to the configuration file

2. **Database security:**
   - Set appropriate file permissions for the SQLite database

3. **Network security:**
   - Use HTTPS for Cardskipper API communication
   - Consider network isolation for the integration server

## Customizing the Integration

### Changing the polling interval

Modify `POLL_INTERVAL_SECONDS` in the Config class:

```python
POLL_INTERVAL_SECONDS = 600  # Poll every 10 minutes
```

### Adding email notifications

Add SMTP settings to the Config class and implement notification sending:

```python
# In Config class
SMTP_SERVER = "smtp.example.com"
SMTP_PORT = 587
SMTP_USERNAME = "alerts@example.com"
SMTP_PASSWORD = "password"
NOTIFICATION_EMAIL = "admin@example.com"

# Implement notification function
def send_notification(subject, message):
    # Email sending code here
```

## Appendix: API Details

### Cardskipper API

- **Base URL:** https://api.cardskipper.se
- **Test URL:** https://api-test.cardskipper.se
- **Authentication:** Basic Authentication
- **Member Search Endpoint:** /Member/Export/
- **Documentation:** See Cardskipper External API documentation

### IVMS API

- **Base URL:** http://<device_ip>:<port>
- **Authentication:** Basic Authentication
- **User Search Endpoint:** /ISAPI/AccessControl/UserInfo/search
- **User Update Endpoint:** /ISAPI/AccessControl/UserInfo/modify
- **Documentation:** Hikvision IVMS documentation