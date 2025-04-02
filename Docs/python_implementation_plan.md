# Cardskipper to IVMS Integration Python Implementation Plan

## Project Overview

This integration will create a Python-based middleware to automatically synchronize membership validity dates between Cardskipper (a digital membership card platform) and IVMS (Hikvision's access control system). When a member extends their membership in Cardskipper, their access rights in IVMS will be automatically updated.

## System Architecture

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│  Cardskipper │         │   Python     │         │     IVMS    │
│    API      │◄────────┤  Middleware   ├────────►│   System    │
└─────────────┘         └──────────────┘         └─────────────┘
                              │
                              ▼
                        ┌──────────────┐
                        │    SQLite    │
                        │   Database   │
                        └──────────────┘
```

## Key Components

1. **Cardskipper API Client**
   - Authenticate using Basic Auth
   - Retrieve active members and their validity dates
   - Handle XML data formatting for Cardskipper API

2. **IVMS API Client**
   - Authenticate with the IVMS system
   - Search for users by email
   - Update user validity periods

3. **Database Manager**
   - Track the last known state of members
   - Detect changes in validity dates
   - Store mappings between Cardskipper and IVMS user IDs

4. **Synchronization Service**
   - Orchestrate the synchronization process
   - Run as a background service
   - Implement error handling and logging

## Implementation Steps

### 1. Project Setup

- Create virtual environment
- Install required packages:
  - `requests` for API communication
  - `lxml` for XML processing
  - Standard library: `sqlite3`, `logging`, `datetime`, etc.

### 2. Cardskipper API Integration

- Implement authentication with Cardskipper API
- Create functions to retrieve active members
- Parse XML responses to extract member data
- Focus on retrieving emails and validity dates

### 3. IVMS API Integration

- Implement the ISAPI protocol for IVMS communication
- Create functions to search users by email
- Implement user validity date updates
- Handle Base64 authentication for IVMS

### 4. Database Implementation

- Design SQLite schema to track:
  - Member emails
  - Cardskipper organization member IDs
  - IVMS user IDs
  - Validity start/end dates
- Implement CRUD operations for member data

### 5. Synchronization Logic

- Define the synchronization workflow:
  1. Get all active members from Cardskipper
  2. Compare with local database to detect changes
  3. For changed records, update IVMS
  4. Update local database with new state
- Implement error handling and retries

### 6. Service Implementation

- Create a main service class that runs the sync at regular intervals
- Implement proper shutdown handling
- Add comprehensive logging

### 7. Configuration Management

- Create a configuration class for credentials and settings
- Support environment variable overrides
- Document all required configuration parameters

### 8. Testing and Deployment

- Test with a single user first
- Implement comprehensive error handling
- Create deployment instructions
- Add monitoring capabilities

## Development Schedule

1. **Week 1**: Setup project and implement Cardskipper API client
2. **Week 2**: Implement IVMS API client
3. **Week 3**: Create database layer and synchronization logic
4. **Week 4**: Testing, refinement, and documentation

## Technical Considerations

### Security

- Store credentials securely
- Implement proper error handling to prevent security issues
- Use HTTPS for all API communications

### Performance

- Optimize polling frequency to balance timeliness vs API load
- Consider batch processing for better performance
- Index the database properly for efficient lookups

### Reliability

- Implement proper logging for troubleshooting
- Add retry mechanisms for transient failures
- Consider adding email notifications for critical errors

## Future Enhancements

1. Web dashboard for monitoring the synchronization status
2. Support for multiple Cardskipper organizations
3. Two-way synchronization (changes in either system are reflected in the other)
4. More sophisticated user matching beyond email addresses

## Getting Started

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Configure the integration by editing `config.py`
4. Run the integration: `python main.py`