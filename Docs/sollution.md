# Cardskipper to IVMS Integration Solution

Based on the Cardskipper API documentation and your requirements, I can provide a comprehensive solution to automatically synchronize membership validity dates between Cardskipper and your IVMS system.

## Understanding Your Requirements

You want to:
- Automatically update membership validity dates in your IVMS system when they change in Cardskipper
- Use email addresses as the unique identifier to match users between systems
- Ensure that when a member extends their membership in Cardskipper (e.g., from 1.10.2025 to 1.11.2025), the access rights in IVMS are updated accordingly

## Proposed Solution Architecture

I recommend creating a middleware application that will:

1. **Poll Cardskipper API** at regular intervals to retrieve active members
2. **Store a local database** of the last known state
3. **Detect changes** by comparing current data with the stored state
4. **Update IVMS** via its API when changes are detected

### Technical Implementation Details

## Implementation Steps

1. **Set Up Authentication**:
   - Use Basic Authentication with Cardskipper as specified in the API documentation
   - Set up authorization for IVMS API access

2. **Retrieve Active Members from Cardskipper**:
   - Use the `/Member/Export/` endpoint
   - Filter for active members with `OnlyActive=true`
   - Include email addresses and validity dates in the response

3. **Match Users Between Systems**:
   - First, retrieve all users from IVMS using the search endpoint:
     ```
     http://<device_ip>:<port>/ISAPI/AccessControl/UserInfo/search
     ```
   - Match users based on email addresses

4. **Update IVMS When Changes Are Detected**:
   - When a validity date changes in Cardskipper, update the corresponding user in IVMS:
     ```
     http://<device_ip>:<port>/ISAPI/AccessControl/UserInfo/modify
     ```
   - Update the `beginTime` and `endTime` values

## Code Implementation

## Configuration Requirements

To implement this solution, you'll need:

1. **Cardskipper API Credentials**:
   - Username and password with API access rights
   - Your organization ID (can be retrieved using the `/Organisation/Info/` endpoint)

2. **IVMS System Details**:
   - IP address and port of your IVMS device
   - Admin username and password
   - Ensure the users in IVMS have email addresses configured

3. **Server Environment**:
   - A server that can run the integration middleware 24/7
   - Python 3.7+ installed with required packages
   - Network access to both Cardskipper API and your IVMS system

## How It Works

1. **Initial Setup**:
   - Edit the configuration section of the script with your credentials and settings
   - The middleware creates a local SQLite database to track membership states

2. **Continuous Operation**:
   - The service polls Cardskipper API at regular intervals (default: every 5 minutes)
   - When changes are detected, it updates the corresponding IVMS user records
   - All operations are logged for troubleshooting

3. **Email-Based Matching**:
   - Users are matched between systems using email addresses
   - Ensure that all users have valid email addresses in both systems

## Deployment Instructions

1. Install Python 3.7+ and required packages:
   ```bash
   pip install requests
   ```

2. Edit the `Config` class in the script with your specific connection details

3. Run the script:
   ```bash
   python cardskipper_ivms_sync.py
   ```

4. For production deployment, consider:
   - Setting up as a system service (systemd on Linux)
   - Implementing monitoring and notifications
   - Adding more extensive error handling

## Testing and Troubleshooting

1. **Test with a Single User First**:
   - Update a single membership in Cardskipper
   - Check the logs to verify that the update was detected and processed
   - Verify in IVMS that the update was applied correctly

2. **Common Issues**:
   - Authentication failures: Double-check credentials for both systems
   - User matching: Ensure emails are consistent between systems
   - Network connectivity: Ensure your server can access both APIs

3. **Monitoring**:
   - The script logs all activities to both console and a log file
   - Check `cardskipper_ivms_sync.log` for detailed operation information

## Next Steps and Enhancements

1. **Additional Features**:
   - Add email notifications for sync failures
   - Implement a web dashboard to monitor sync status
   - Add support for multiple organizations

2. **Security Enhancements**:
   - Store credentials securely (e.g., using environment variables)
   - Implement certificate validation for HTTPS connections

Would you like me to provide any additional details about specific aspects of this solution?