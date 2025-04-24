// Handle image upload and classification on the classify.html page
document.addEventListener('DOMContentLoaded', function() {
    const uploadForm = document.getElementById('upload-form');
    const imageInput = document.getElementById('image-input');
    const previewContainer = document.getElementById('preview-container');
    const previewImage = document.getElementById('preview-image');
    const classifyButton = document.getElementById('classify-button');
    const loadingSpinner = document.getElementById('loading-spinner');
    const resultContainer = document.getElementById('result-container');
    
    // Show image preview when image is selected
    imageInput.addEventListener('change', function() {
        const file = this.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function(e) {
                previewImage.src = e.target.result;
                previewContainer.style.display = 'block';
                classifyButton.disabled = false;
            }
            reader.readAsDataURL(file);
        } else {
            previewContainer.style.display = 'none';
            classifyButton.disabled = true;
        }
    });
    
    // Handle form submission
    uploadForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const formData = new FormData();
        const file = imageInput.files[0];
        
        if (!file) {
            alert('Please select an image to classify');
            return;
        }
        
        formData.append('image', file);
        
        // Show loading spinner
        loadingSpinner.style.display = 'block';
        resultContainer.style.display = 'none';
        
        // Send image to server for classification
        fetch('/api/classify', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            // Hide loading spinner
            loadingSpinner.style.display = 'none';
            
            // Display classification results
            resultContainer.style.display = 'block';
            
            if (data.success) {
                // Get the e-waste type and confidence level
                const ewasteType = data.result.ewaste_type;
                const confidence = (data.result.confidence * 100).toFixed(1);
                
                // Create HTML for the result
                let resultHTML = `
                    <div class="alert alert-success">
                        <h4 class="alert-heading mb-3">E-Waste Identified!</h4>
                        <p class="mb-1">We've identified your item as:</p>
                        <h3 class="my-3">${ewasteType.replace(/-/g, ' ')}</h3>
                        <div class="progress mb-3" style="height: 20px;">
                            <div class="progress-bar bg-success" role="progressbar" 
                                style="width: ${confidence}%" 
                                aria-valuenow="${confidence}" aria-valuemin="0" aria-valuemax="100">
                                ${confidence}% confidence
                            </div>
                        </div>
                    </div>
                    
                    <div class="card mb-4">
                        <div class="card-header d-flex justify-content-between align-items-center">
                            <h5 class="mb-0">Recycling Information</h5>
                        </div>
                        <div class="card-body">
                            <p>${data.result.recycling_info || 'Information about recycling this item will be provided soon.'}</p>
                        </div>
                    </div>
                    
                    <div class="d-grid gap-2">
                        <a href="/schedule?ewaste_type=${encodeURIComponent(ewasteType)}" class="btn btn-success">
                            <i class="fas fa-calendar-alt me-2"></i> Schedule Pickup for this Item
                        </a>
                        <button type="button" class="btn btn-outline-secondary" onclick="document.getElementById('image-input').value = ''; document.getElementById('upload-form').reset(); document.getElementById('preview-container').style.display = 'none'; document.getElementById('result-container').style.display = 'none';">
                            <i class="fas fa-redo me-2"></i> Try Another Image
                        </button>
                    </div>
                `;
                
                resultContainer.innerHTML = resultHTML;
            } else {
                // Display error message
                resultContainer.innerHTML = `
                    <div class="alert alert-danger">
                        <h5>Error:</h5>
                        <p>${data.message || 'An error occurred during classification.'}</p>
                        <button type="button" class="btn btn-outline-danger mt-3" onclick="document.getElementById('image-input').value = ''; document.getElementById('upload-form').reset(); document.getElementById('preview-container').style.display = 'none';">
                            <i class="fas fa-redo me-2"></i> Try Again
                        </button>
                    </div>
                `;
            }
        })
        .catch(error => {
            // Hide loading spinner
            loadingSpinner.style.display = 'none';
            
            // Display error message
            resultContainer.style.display = 'block';
            resultContainer.innerHTML = `
                <div class="alert alert-danger">
                    <h5>Error:</h5>
                    <p>${error.message}</p>
                    <button type="button" class="btn btn-outline-danger mt-3" onclick="document.getElementById('image-input').value = ''; document.getElementById('upload-form').reset(); document.getElementById('preview-container').style.display = 'none';">
                        <i class="fas fa-redo me-2"></i> Try Again
                    </button>
                </div>
            `;
        });
    });
});