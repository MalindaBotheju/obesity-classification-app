// --- 1. SINGLE PREDICTION ---
document.getElementById('predictionForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const submitBtn = document.getElementById('submitBtn');
    const resultContainer = document.getElementById('resultContainer');
    const predictionText = document.getElementById('predictionText');

    submitBtn.innerText = 'Processing...';

    const data = Object.fromEntries(new FormData(e.target).entries());

    ['Height', 'Weight', 'FCVC', 'NCP', 'CH2O', 'FAF', 'TUE'].forEach(field => {
        data[field] = parseFloat(data[field]);
    });
    data['Age'] = parseInt(data['Age'], 10);

    try {
        const response = await fetch(`${CONFIG.API_URL}/predict`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        const result = await response.json();

        if (response.ok) {
            predictionText.innerText = result.prediction.replace(/_/g, ' ');
            resultContainer.classList.remove('hidden');
        } else {
            alert('Error: ' + (typeof result.detail === 'string' ? result.detail : 'Please check your inputs.'));
        }
    } catch (error) {
        console.error('Fetch error:', error);
        alert('Could not connect to the backend server.');
    } finally {
        submitBtn.innerText = 'Predict Status';
    }
});

// --- 2. BATCH PREDICTION (CSV) ---
document.getElementById('batchSubmitBtn').addEventListener('click', async () => {
    const fileInput = document.getElementById('csvFileInput');
    const statusText = document.getElementById('batchStatus');
    const batchBtn = document.getElementById('batchSubmitBtn');

    if (fileInput.files.length === 0) {
        statusText.innerText = 'Please select a CSV file first!';
        statusText.style.color = 'red';
        return;
    }

    const formData = new FormData();
    formData.append('file', fileInput.files[0]);

    batchBtn.innerText = 'Processing...';
    batchBtn.disabled = true;
    statusText.innerText = 'Processing... please wait.';
    statusText.style.color = '#0066cc';

    try {
        const response = await fetch(`${CONFIG.API_URL}/predict/batch`, {
            method: 'POST',
            body: formData
        });
        const result = await response.json();

        if (response.ok) {
            statusText.innerText = result.message;
            statusText.style.color = 'green';
            fileInput.value = '';
        } else {
            statusText.innerText = 'Error: ' + (typeof result.detail === 'string' ? result.detail : 'Failed to process the CSV.');
            statusText.style.color = 'red';
        }
    } catch (error) {
        console.error('Error:', error);
        statusText.innerText = 'Error connecting to the backend server.';
        statusText.style.color = 'red';
    } finally {
        batchBtn.innerText = 'Predict Batch';
        batchBtn.disabled = false;
    }
});
