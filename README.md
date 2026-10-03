# Obesity Classification App

A small web app that predicts a person's obesity level from 16 inputs (body details and daily habits).

It does 3 things:
1. **Single prediction** - fill the form and see the result on the page.
2. **Batch prediction** - upload a CSV file and predict every row.
3. **Save to Supabase** - every prediction (all 16 inputs + result + time) is saved in the database.

## How it works

```
Frontend (Vercel)
      |
      v
FastAPI (Render)
  |-- /predict        -> ML model -> Supabase
  |-- /predict/batch  -> ML model -> Supabase
```

## Project structure

```
obesity-app/
|-- .github/
|   `-- workflows/
|       `-- check.yml                # GitHub Actions: checks the model on every push
|-- backend/
|   |-- main.py                      # FastAPI app: /predict and /predict/batch
|   |-- ml_utils.py                  # Preprocessing + model prediction
|   |-- obesity_full_pipeline.joblib # Trained model
|   |-- requirements.txt             # Python packages
|   |-- Dockerfile                   # Used by Render
|   |-- .dockerignore
|   |-- .env.example                 # Copy this to .env
|   `-- .env                         # Your real database URL (not uploaded to GitHub)
|-- frontend/
|   |-- index.html
|   |-- app.js
|   |-- style.css
|   `-- config.js                    # Backend URL
|-- .gitignore
`-- README.md
```

## Batch CSV format

The CSV must have these 16 columns (extra columns like `NObeyesdad` are ignored):

`Gender, Age, Height, Weight, family_history_with_overweight, FAVC, FCVC, NCP, CAEC, SMOKE, CH2O, SCC, FAF, TUE, CALC, MTRANS`

- Rows with empty or invalid values are skipped.
- The page shows a message like `Saved 500 predictions`.

## Run on your computer

You need **Python 3.11 or 3.12** (the model package `scikit-learn==1.5.1` does not install on Python 3.13). Check with `python --version`.

### 1. Create and turn on a virtual environment

Go into the backend folder:
```bash
cd backend
```

Windows:
```bash
python -m venv venv
venv\Scripts\activate
```

Mac or Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

You will see `(venv)` at the start of your terminal line when it is on.

### 2. Install the packages
```bash
pip install -r requirements.txt
```

### 3. Add your database URL
Open `backend/.env` and put your real Supabase `DATABASE_URL`.
(`backend/.env.example` shows the format.)

### 4. Start the backend
```bash
uvicorn main:app --reload
```
Check it at http://localhost:8000/docs

The first time it starts, it creates the `predictions` table in Supabase by itself.

### 5. Start the frontend
1. Open `frontend/config.js` and use the local URL:
   ```js
   API_URL: "http://localhost:8000"
   ```
2. Open `frontend/index.html` in your browser.

### 6. Stop and turn off
Press `Ctrl + C` to stop the server. Then turn off the virtual environment:
```bash
deactivate
```
Next time, just turn the environment on again (step 1) and run step 4.

## Automatic check (GitHub Actions)

The file `.github/workflows/check.yml` runs by itself every time you push to GitHub. It:
1. Installs the packages from `backend/requirements.txt` (Python 3.11).
2. Loads the model and makes one test prediction.

If something is broken, the check fails and you will see a red mark on your commit. To see the result, open the **Actions** tab in your GitHub repo.

It does not use your database or any password.

## Deploy

### 1. Supabase (database)
- Create a project, then go to **Project Settings -> Database** and copy the connection string.
- Replace `[YOUR-PASSWORD]` with your database password.

### 2. Render (backend)
1. Push this project to GitHub.
2. On Render: **New -> Web Service** -> choose your repo.
3. Set **Root Directory** to `backend`.
4. Set **Runtime** to **Docker** (Render will use `backend/Dockerfile`).
5. Add an environment variable: `DATABASE_URL` = your Supabase connection string.
6. Deploy. Copy your URL, for example `https://your-app.onrender.com`.

### 3. Vercel (frontend)
1. Open `frontend/config.js` and set your Render URL:
   ```js
   const CONFIG = {
       API_URL: "https://your-app.onrender.com"
   };
   ```
2. Push to GitHub.
3. On Vercel: **Add New -> Project** -> choose your repo.
4. Set **Root Directory** to `frontend`. Framework preset: **Other**. No build command.
5. Deploy.

## Notes
- Render's free plan sleeps when unused, so the first request can take about a minute.
- If Supabase connection fails on Render, try the **Session pooler** connection string from Supabase (it works over IPv4).
- Never upload your `.env` file or your `venv/` folder to GitHub. The `.gitignore` already blocks both.
- Before you deploy, change `frontend/config.js` back to your Render URL.