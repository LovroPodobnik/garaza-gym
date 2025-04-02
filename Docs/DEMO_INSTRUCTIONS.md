# Cardskipper to IVMS Integration Demo

This interactive demo showcases how the Cardskipper to IVMS integration works using simulated data. The application demonstrates the process of synchronizing membership validity dates between the Cardskipper membership system and the IVMS access control system.

## Running the Demo

### Prerequisites

- Python 3.7 or higher
- The required packages listed in `requirements.txt`

### Installation

1. Create a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   
   # On Windows:
   venv\Scripts\activate
   
   # On macOS/Linux:
   source venv/bin/activate
   ```

2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the Streamlit application:
   ```bash
   streamlit run streamlit_demo.py
   ```

4. The application will open in your web browser at http://localhost:8501

## Using the Demo

The demo includes four main tabs:

### 1. Dashboard

- View overall statistics about the integration
- See how many members are synced with IVMS
- View charts of member status and sync history
- Review recent sync operations and any errors

### 2. Cardskipper Members

- View active members in the Cardskipper system
- Extend a member's membership to simulate a renewal
- See changes in validity dates

### 3. IVMS Users

- View users in the IVMS access control system
- See their current validity periods

### 4. Synchronization

- Manually trigger the synchronization process
- See the results of the synchronization

## Demo Workflow

To demonstrate the full integration workflow:

1. First, review the existing members and users in the Cardskipper and IVMS tabs
2. Run an initial synchronization from the Synchronization tab
3. Go to the Dashboard to see the results
4. Return to the Cardskipper Members tab and extend a member's membership
5. Run the synchronization again
6. Check the IVMS Users tab to verify that the validity dates were updated
7. Review the sync history on the Dashboard

## Understanding the Data Flow

The integration performs these steps:

1. Retrieves active members from Cardskipper
2. Compares with the previously saved state in the database
3. Identifies members that need to be updated in IVMS
4. Matches members between systems using email addresses
5. Updates the validity dates in the IVMS system
6. Records all operations in the sync history

## Notes

- This is a simulation using mock data
- In a real implementation, the synchronization would run automatically on a schedule
- Error handling and retry logic would be more robust
- The real system would use the actual Cardskipper and IVMS APIs