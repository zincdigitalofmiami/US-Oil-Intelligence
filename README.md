# U.S. Oil Solutions

A comprehensive web application for U.S. Oil Solutions, providing ML-driven oil price forecasting, procurement signals, and strategic planning tools. The application is designed to help the company make informed decisions by leveraging data analysis and predictive modeling.

## Key Features

*   **ML-Powered Forecasting:** Utilizes a Prophet model to generate future oil price forecasts.
*   **Procurement Recommendations:** Provides actionable "BUY," "WAIT," or "HEDGE" signals based on forecast data.
*   **Automated Data Ingestion:** Includes a web scraper to automatically fetch market analysis from external sources like ProFarmer.
*   **Secure Credential Management:** Integrations with external services are managed securely using Google Secret Manager.
*   **Historical Data Upload:** Allows for uploading historical data to refine and train forecasting models.
*   **Strategic Planning:** (Placeholder for future functionality)
*   **Sales Intelligence:** (Placeholder for future functionality)

## Technical Stack

*   **Backend:** FastAPI (Python)
*   **Frontend:** Vue.js with Tailwind CSS
*   **Database:** Google Firestore
*   **Deployment:**
    *   Backend service deployed on Google Cloud Run.
    *   Frontend deployed on Firebase Hosting.
*   **Secrets Management:** Google Secret Manager
*   **CI/CD:** GitHub Actions

## Project Structure

*   `svc/`: The core FastAPI backend service.
    *   `api/`: Defines the API routes.
    *   `services/`: Contains business logic, including data scrapers and forecasting models.
    *   `main.py`: The application entrypoint.
*   `ui/`: The Vue.js frontend application.
*   `functions/`: Cloud Functions for ancillary backend tasks.
*   `cloudrun/`: Deployment scripts for the backend service.
*   `data/`: Sample data files.

## Getting Started

### Prerequisites

*   Python 3.9+
*   Node.js 16+
*   Google Cloud SDK

### Backend

```bash
# Set up and activate python virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the development server
python -m svc.main
```

### Frontend

```bash
# Navigate to the UI directory
cd ui

# Install dependencies
npm install

# Run the development server
npm run dev
```

## Deployment

The backend service can be deployed to Google Cloud Run using the provided script.

```bash
# Authenticate with Google Cloud
gcloud auth login

# Set your Google Cloud Project ID
PROJECT_ID=your-project-id-here
gcloud config set project $PROJECT_ID

# Enable required services
gcloud services enable run.googleapis.com

# Run the deployment script
./cloudrun/deploy.sh
```
