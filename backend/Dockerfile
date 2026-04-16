# 1. Use the official Python image (matching your version)
FROM python:3.11-slim

# 2. Set the working directory inside the container
WORKDIR /app

# 3. Copy the requirements file first (this makes future builds much faster)
COPY requirements.txt .

# 4. Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy the rest of your backend code into the container
COPY . .

# 6. Expose the port FastAPI runs on
EXPOSE 8000

# 7. Command to start the FastAPI server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]