# 🏥 Obesity Classification & Prediction System

A production-grade, end-to-end Machine Learning application that classifies patient obesity risk levels based on physical and lifestyle data. This project features a full CI/CD pipeline and a decoupled architecture, deployed across Render, Vercel, and Supabase.

## 🚀 Live Demo
<div align="center">

[![Live Web App](https://img.shields.io/badge/Vercel-Live_Web_App-black?style=for-the-badge&logo=vercel)](https://obesity-classification-app.vercel.app)
[![Backend API Docs](https://img.shields.io/badge/Render-Backend_API_Docs-46E3B7?style=for-the-badge&logo=render&logoColor=white)](https://obesity-classification-app-z9sy.onrender.com/docs)

</div>

## ✨ Key Features
* **Individual Prediction:** Instant classification via a clean web form.
* **Batch processing:** Upload hospital CSV files to process hundreds of patients at once.
* **Cloud Persistence:** All predictions are automatically logged to a Supabase PostgreSQL database.
* **Automated Workflow:** GitHub Actions tests code integrity on every push.

## 🛠 Tech Stack
![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=flat-square&logo=fastapi)
![Scikit-Learn](https://img.shields.io/badge/scikit_learn-F7931E?style=flat-square&logo=scikit-learn&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=flat-square&logo=javascript&logoColor=black)
![Supabase](https://img.shields.io/badge/Supabase-3ECF8E?style=flat-square&logo=supabase&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker&logoColor=white)

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
- VS Code or your preferred editor
- A Supabase account (or local PostgreSQL database)
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running on your machine.

You are absolutely right, I completely skipped the most fundamental step—actually getting the code onto the machine. Good catch.

Here is the revised **Local Development & Testing** section with the cloning and directory navigation steps included right at the beginning.

---

## 💻 Local Development & Testing

This guide details how to set up and run the complete system on your own machine using Docker. Running locally via Docker Compose is the fastest and most reliable way to spin up both the frontend and backend environments simultaneously.

### 1. Prerequisites

* **Git** installed on your machine.
* **[Docker Desktop](https://www.docker.com/products/docker-desktop/)** installed and running.
* A **Supabase** account (or local PostgreSQL database).
* VS Code or your preferred code editor.

### 2. Clone the Repository

Download the project files to your local machine and navigate into the root directory.

1. **Clone the repository:**
   ```bash
   git clone https://github.com/MalindaBotheju/obesity-classification-app.git
   ```
   
2. **Navigate into the project folder:**
```bash
cd obesity-classification-app

```

### 2. Environment Setup

Before spinning up the containers, you need to provide your database connection string so the backend can securely communicate with Supabase.

1. **Create your local `.env` file:** Create a new file named `.env` inside the `backend/` directory.
2. **Add your Supabase URL:** Paste your connection string into the file:
   
```
  SUPABASE_URL=paste_your_real_URL_here
```

### 3. Frontend Configuration

Ensure your frontend is configured to communicate with the local backend container rather than the live production server.

1. **Open `frontend/app.js`.**
2. **Update the `fetch` URLs:** Comment out the live Render URLs and uncomment the localhost lines so they point to your local backend (typically port 8000):
```javascript
// -- SINGLE PATIENT --
// Live Render: https://obesity-classification-app-z9sy.onrender.com/predict
// Locally: 
const response = await fetch('http://localhost:8000/predict', { ...

```

### 4. Running the Application

With Docker Compose configured, you can build and start the entire stack with a single command.

1. **Open your terminal** in the root directory of the project (where the `docker-compose.yml` file is located).
2. **Build and start the containers:**
```bash
docker-compose up --build

```


*(Note: You only need the `--build` flag the first time or when you make changes to the `Dockerfile` or `requirements.txt`. For subsequent runs, just `docker-compose up` is sufficient.)*
3. **Access the web app:** Once the containers are running, open your web browser and navigate to the frontend port mapped in your compose file (typically `http://localhost` or `http://localhost:3000`). Your backend API documentation will be accessible at `http://localhost:8000/docs`.
4. **Shutting down:** To stop the application, press `Ctrl + C` in your terminal, or open a new terminal in the root directory and run:
```bash
docker-compose down

```
