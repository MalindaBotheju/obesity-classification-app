# 🏥 Obesity Classification & Prediction System

A production-grade, end-to-end Machine Learning application that classifies patient obesity risk levels based on physical and lifestyle data. This project features a full CI/CD pipeline and a decoupled architecture, deployed across Render, Vercel, and Supabase.

## 🚀 Live Demo
* **Frontend Web App:** https://obesity-classification-app.vercel.app
* **Backend API Docs:** https://obesity-classification-app-z9sy.onrender.com/docs

## ✨ Key Features
* **Individual Prediction:** Instant classification via a clean web form.
* **Batch processing:** Upload hospital CSV files to process hundreds of patients at once.
* **Cloud Persistence:** All predictions are automatically logged to a Supabase PostgreSQL database.
* **Automated Workflow:** GitHub Actions tests code integrity on every push.

## ⚙️ Architecture & Data Flow
The image below illustrates how the different services interact to process data and make predictions:

![System Architecture and Data Flow Diagram](images/architecture_diagram.png)

## 📁 Project Structure

```text
obesity-classification/
├── .github/                            # GitHub Actions workflows
├── backend/                            # FastAPI server & ML pipeline
│   ├── .dockerignore                   # Docker exclusion rules
│   ├── .env                            # Local environment variables
│   ├── Dockerfile                      # Backend container configuration
│   ├── main.py                         # FastAPI application and routes
│   ├── ml_utils.py                     # Machine learning utility functions
│   ├── obesity_full_pipeline.joblib    # Trained and saved ML model
│   ├── requirements.txt                # Python backend dependencies
│   └── test_main.py                    # Unit tests for the API
├── frontend/                           # Vanilla JS Web Interface
│   ├── app.js                          # Frontend logic and API requests
│   ├── Dockerfile                      # Frontend container configuration
│   ├── index.html                      # Main user interface
│   └── style.css                       # Application styling
├── images/                             # Image assets for the README
├── notes/                              # Additional project notes
├── .gitignore                          # Git exclusion rules
├── docker-compose.yml                  # Multi-container Docker configuration
├── obesity_classification.ipynb        # Jupyter notebook for model training
├── obesity-dataset.csv                 # Original training dataset
└── README.md                           # Project documentation
```

## 🖥️ The Web Interface

### Single Prediction Form
Users can enter patient data directly into the web interface. All 16 lifestyle features are captured, validated, and sent to the ML model.

![Obesity Classification Form Screenshot](images/dashboard_form.png)

### Batch Prediction (CSV Upload)
This view shows the bulk processing feature. Users select a CSV file of patient data, and the system processes it, stores the results in Supabase, and downloads a generated CSV file.

![Batch CSV Processing Screenshot](images/batch_results.png)

## 💻 Local Development & Testing

This guide details how to set up and run the complete system on your own machine. Running locally is the fastest way to test new changes.

### 1. Prerequisites
- Python 3.10+
- VS Code or your preferred editor
- A Supabase account (or local PostgreSQL database)

### 2. Backend (FastAPI) Setup
The backend handles the ML model and database communication.

1.  **Navigate to the backend folder:**
    ```bash
    cd backend
    ```
2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    # Windows:
    .\venv\Scripts\activate
    # Mac/Linux:
    source venv/bin/activate
    ```
3.  **Install the required libraries:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Create your local `.env` file:** Create a new file named `.env` inside the `backend/` folder and add your Supabase connection string:
    ```env
    # Format: postgresql://postgres:[PASSWORD]@db.[PROJECT_ID].supabase.co:5432/postgres
    DATABASE_URL=paste_your_real_string_here
    ```
5.  **Start the local backend server:**
    ```bash
    uvicorn main:app --reload
    ```
    Your API will now be live and accepting requests at `http://127.0.0.1:8000`.

### 3. Frontend Setup
The frontend just needs to know where to find the backend server.

1.  **Open `frontend/app.js`.**
2.  **Change the `fetch` URLs.** Comment out the live Render URLs and uncomment the localhost lines. It should look like this:
    ```javascript
    // -- SINGLE PATIENT --
    //Live Render: [https://obesity-classification-app-z9sy.onrender.com/predict](https://obesity-classification-app-z9sy.onrender.com/predict)
    //Locally: 
    const response = await fetch('[http://127.0.0.1:8000/predict](http://127.0.0.1:8000/predict)', { ...
    ```
3.  **Open the web page.** Simply double-click `frontend/index.html` to open it in your browser.

## 🦾 Continuous Integration (CI) with GitHub Actions
This project uses GitHub Actions to automatically test the stability of the backend environment. You can see the build status by clicking on the **Actions** tab of this repository. Every push is verified to ensure it doesn't break.