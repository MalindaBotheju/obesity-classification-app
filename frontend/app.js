// --- 1. SINGLE PATIENT PREDICTION ---
document.getElementById('predictionForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const submitBtn = document.getElementById('submitBtn');
    const resultContainer = document.getElementById('resultContainer');
    const predictionText = document.getElementById('predictionText');
    
    submitBtn.innerText = 'Processing...';
    
    // Create an object from form data
    const formData = new FormData(e.target);
    const data = Object.fromEntries(formData.entries());

    // Convert numeric strings to actual numbers (Floats)
    const floatFields = ['Height', 'Weight', 'FCVC', 'NCP', 'CH2O', 'FAF', 'TUE'];
    floatFields.forEach(field => {
        data[field] = parseFloat(data[field]);
    });

    // Parse Age strictly as an Integer
    data['Age'] = parseInt(data['Age'], 10);

    try {
        const response = await fetch('https://obesity-classification-app-z9sy.onrender.com/predict', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        const result = await response.json();
        
        if (response.ok) {
            predictionText.innerText = result.prediction.replace(/_/g, ' ');
            resultContainer.classList.remove('hidden');
        } else {
            alert('Error: ' + result.detail);
        }
    } catch (error) {
        console.error('Fetch error:', error);
        alert('Could not connect to the backend server.');
    } finally {
        submitBtn.innerText = 'Predict Status';
    }
});

// --- 2. BATCH CSV PREDICTION (HOSPITAL UPLOAD) ---
document.getElementById('batchSubmitBtn').addEventListener('click', async () => {
    const fileInput = document.getElementById("csvFileInput");
    const statusText = document.getElementById("batchStatus");
    const batchSubmitBtn = document.getElementById("batchSubmitBtn");

    // Check if user actually selected a file
    if (fileInput.files.length === 0) {
        statusText.innerText = "Please select a CSV file first!";
        statusText.style.color = "red";
        return;
    }

    const file = fileInput.files[0];
    const formData = new FormData();
    formData.append("file", file);

    // Update UI while processing
    batchSubmitBtn.innerText = "Processing Batch...";
    batchSubmitBtn.disabled = true;
    statusText.innerText = "Processing... please wait. This might take a moment for large files.";
    statusText.style.color = "#0066cc";

    try {
        const response = await fetch("https://obesity-classification-app-z9sy.onrender.com/predict/batch", {
            method: "POST",
            body: formData // No Content-Type header needed for FormData; the browser sets it automatically
        });

        if (response.ok) {
            // Trigger the browser to download the returned CSV file
            const blob = await response.blob();
            const downloadUrl = window.URL.createObjectURL(blob);
            const a = document.createElement("a");
            a.href = downloadUrl;
            a.download = "hospital_predictions_results.csv";
            document.body.appendChild(a);
            a.click();
            a.remove();
            
            statusText.innerText = "Success! Predictions downloaded and saved to the database.";
            statusText.style.color = "green";
            fileInput.value = ""; // Clear the input
        } else {
            const errorData = await response.json();
            statusText.innerText = "Error: " + (errorData.detail || "Failed to process batch.");
            statusText.style.color = "red";
        }
    } catch (error) {
        console.error("Error:", error);
        statusText.innerText = "Error connecting to the backend server.";
        statusText.style.color = "red";
    } finally {
        // Reset the button
        batchSubmitBtn.innerText = "Upload & Predict Batch";
        batchSubmitBtn.disabled = false;
    }
});