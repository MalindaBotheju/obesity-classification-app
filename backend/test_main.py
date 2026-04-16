from fastapi.testclient import TestClient
from main import app

# This creates a "fake" browser/frontend to send requests to your API
client = TestClient(app)

def test_predict_endpoint_success():
    """Test that a valid patient correctly returns a prediction."""
    valid_data = {
        "Gender": "Male", 
        "Age": 25,  # Remember, we made this an int!
        "Height": 1.75, 
        "Weight": 80.0,
        "family_history_with_overweight": "yes", 
        "FAVC": "yes", 
        "FCVC": 2.0, 
        "NCP": 3.0, 
        "CAEC": "Sometimes", 
        "SMOKE": "no", 
        "CH2O": 2.0, 
        "SCC": "no", 
        "FAF": 2.0, 
        "TUE": 1.0, 
        "CALC": "Sometimes", 
        "MTRANS": "Public_Transportation"
    }
    
    response = client.post("/predict", json=valid_data)
    
    # 1. Ensure the server accepted it (Status 200 OK)
    assert response.status_code == 200
    
    # 2. Ensure the API actually returned a prediction key
    assert "prediction" in response.json()

def test_predict_endpoint_invalid_age():
    """Test that our Pydantic validation blocks impossible data."""
    invalid_data = {
        "Gender": "Male", 
        "Age": -5,  # INVALID! Age cannot be negative
        "Height": 1.75, 
        "Weight": 80.0,
        "family_history_with_overweight": "yes", 
        "FAVC": "yes", 
        "FCVC": 2.0, 
        "NCP": 3.0, 
        "CAEC": "Sometimes", 
        "SMOKE": "no", 
        "CH2O": 2.0, 
        "SCC": "no", 
        "FAF": 2.0, 
        "TUE": 1.0, 
        "CALC": "Sometimes", 
        "MTRANS": "Public_Transportation"
    }
    
    response = client.post("/predict", json=invalid_data)
    
    # Ensure the server REJECTS it (Status 422 - Unprocessable Entity)
    assert response.status_code == 422

def test_history_endpoint():
    """Test that the history endpoint is accessible."""
    response = client.get("/history")
    
    # Ensure we get a successful response and it returns a list
    assert response.status_code == 200
    assert isinstance(response.json(), list)