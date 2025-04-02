# Cardskipper to IVMS Integration

This project provides a solution for automatically synchronizing membership validity dates between Cardskipper (digital membership platform) and IVMS (Hikvision's access control system). When members extend their subscriptions in Cardskipper, their access rights in IVMS are automatically updated.

## Project Overview

The integration solves a common problem for gyms and fitness centers:
1. When a member extends their membership in Cardskipper, the validity date must be manually updated in IVMS
2. This manual process is time-consuming and error-prone
3. If updates are forgotten or delayed, members can't access the facility despite having valid memberships

Our solution automates this entire process:
1. Automatically detects membership changes in Cardskipper
2. Matches members between systems using email addresses
3. Updates validity dates in IVMS automatically
4. Maintains a log of all changes for auditing

## Repository Contents

- **`src/integration.py`**: Main integration code that connects Cardskipper and IVMS
- **`src/streamlit_demo.py`**: Interactive demo application showing how the integration works
- **`Docs/`**: Documentation files and client proposals
  - `DEMO_INSTRUCTIONS.md`: Instructions for running the demo application
  - `prijateljska-ponudba.md`: Client proposal in Slovenian
  - `tehnicna-dokumentacija-slovenscina.md`: Technical documentation in Slovenian
  - `python_implementation_plan.md`: Detailed implementation plan
  - `requirements.txt`: Required Python packages

## Demo Application

The repository includes an interactive Streamlit demo that visualizes how the integration works:

1. View Cardskipper members and their membership dates
2. View IVMS users and their access rights
3. Extend memberships in Cardskipper
4. See how changes propagate to IVMS
5. Monitor the synchronization history and logs

To run the demo:

```bash
# Install requirements
pip install -r Docs/requirements.txt

# Run the Streamlit app
streamlit run src/streamlit_demo.py
```

## Implementation Options

The integration can be deployed in several ways:

1. **On an existing computer**: Install on a computer that's always on (e.g., reception desk)
2. **On a dedicated device**: Use a small, low-power computer (e.g., Raspberry Pi)
3. **As a cloud service**: Host on a cloud provider for maximum reliability

## Benefits

- **Time savings**: No more manual data entry in two systems
- **Error elimination**: No possibility of forgetting to update access in IVMS
- **Improved member experience**: Members get immediate access after renewal
- **Simple maintenance**: Set up once, then works automatically
- **Professional impression**: Gym operates more smoothly and efficiently

## Contact

For more information or to implement this solution, please contact [Your Contact Information].