# Cardskipper to IVMS Integration

This project provides a middleware solution for synchronizing membership data between Cardskipper (digital membership platform) and IVMS (Hikvision's access control system). When members extend their subscriptions in Cardskipper, their access rights in IVMS are automatically updated.

## Project Files

- **python_implementation_plan.md**: Detailed implementation plan for the integration
- **test_integration_script.py**: Script to test connections to Cardskipper and IVMS APIs
- **mock_integration.py**: Simulation script with mock data for both systems
- **implementation_guide.md**: Detailed guide for installing and deploying the solution

## Mock Integration Demo

The mock integration script simulates the entire integration process using local mock data, so you can see how the synchronization works without needing real API credentials.

### How It Works

1. The script creates mock data for both Cardskipper and IVMS
2. It performs an initial synchronization between the systems
3. It simulates a membership extension in Cardskipper
4. It runs the synchronization process again to update IVMS
5. It reports the results of each operation

### Running the Demo

```bash
# Make sure you have Python 3.7+ installed
python mock_integration.py
```

The script will:
- Create mock data files in the `mock_data` directory
- Create a SQLite database to track synchronization state
- Log all operations to both console and `mock_integration.log`

## Testing with Real APIs

When you're ready to test with the real systems, use the `test_integration_script.py` file:

```bash
python test_integration_script.py \
  --cardskipper-username "your_username" \
  --cardskipper-password "your_password" \
  --organization-id 123 \
  --ivms-ip "192.168.1.100" \
  --ivms-password "your_password"
```

## Implementation

For full implementation details, see the `implementation_guide.md` file.

## Features

- Automatically synchronizes membership validity dates
- Uses email addresses to match users between systems
- Maintains a local database of member states
- Detects changes in membership validity
- Logs all operations for troubleshooting

## Requirements

- Python 3.7+
- `requests` package for API communication
- Network access to both Cardskipper API and IVMS system

## Configuration

Edit the `Config` class in `cardskipper_ivms_sync.py` to include your specific details:

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
    IVMS_PASSWORD = "your_password"
    
    # Sync configuration
    POLL_INTERVAL_SECONDS = 300  # Poll every 5 minutes
```

## Support

If you encounter issues or need assistance with the integration, please contact the developer.