// Handle image upload and classification functionality

document.addEventListener('DOMContentLoaded', function() {
    const imageUploadForm = document.getElementById('imageUploadForm');
    const imageFileInput = document.getElementById('imageFile');
    const imagePreview = document.getElementById('imagePreview');
    const classificationResult = document.getElementById('classificationResult');
    const ewasteTypeField = document.getElementById('ewaste_type');
    const recyclingInfoSection = document.getElementById('recyclingInfo');
    const autofillMessage = document.getElementById('autofillMessage');
    const spinner = document.getElementById('classificationSpinner');
    
    if (!imageUploadForm) return;
    
    // Preview image when selected
    imageFileInput.addEventListener('change', function() {
        const file = this.files[0];
        if (!file) {
            imagePreview.src = '';
            imagePreview.classList.add('d-none');
            return;
        }
        
        const reader = new FileReader();
        reader.onload = function(e) {
            imagePreview.src = e.target.result;
            imagePreview.classList.remove('d-none');
        }
        reader.readAsDataURL(file);
    });
    
    // Submit image for classification
    imageUploadForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const formData = new FormData();
        const file = imageFileInput.files[0];
        
        if (!file) {
            alert('Please select an image to classify');
            return;
        }
        
        formData.append('image', file);
        
        // Show spinner and hide previous results
        spinner.classList.remove('d-none');
        classificationResult.classList.add('d-none');
        recyclingInfoSection.classList.add('d-none');
        autofillMessage.classList.add('d-none');
        
        // Send the request
        fetch('/classify', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(err => {
                    throw new Error(err.error || 'Classification failed');
                });
            }
            return response.json();
        })
        .then(data => {
            // Hide spinner
            spinner.classList.add('d-none');
            
            // Display result
            classificationResult.classList.remove('d-none');
            classificationResult.innerHTML = `
                <div class="alert alert-success">
                    <h5>Classification Result:</h5>
                    <p><strong>Detected E-waste Type:</strong> ${data.ewaste_type}</p>
                    <p><strong>Confidence:</strong> ${data.confidence.toFixed(2)}%</p>
                </div>
            `;
            
            // Update the e-waste type select field if it exists
            if (ewasteTypeField) {
                console.log('Found ewaste_type field, attempting to update with: ' + data.ewaste_type);
                
                // Find the option that matches the detected type, or default to "Other"
                const options = ewasteTypeField.options;
                let found = false;
                
                // First try an exact match (case sensitive)
                for (let i = 0; i < options.length; i++) {
                    if (options[i].value === data.ewaste_type) {
                        console.log('Exact match found at index ' + i + ': ' + options[i].value);
                        ewasteTypeField.selectedIndex = i;
                        found = true;
                        break;
                    }
                }
                
                // If no exact match, try a case-insensitive match
                if (!found && data.ewaste_type) {
                    const lowerCaseType = data.ewaste_type.toLowerCase();
                    for (let i = 0; i < options.length; i++) {
                        if (options[i].value.toLowerCase() === lowerCaseType) {
                            console.log('Case-insensitive match found at index ' + i + ': ' + options[i].value);
                            ewasteTypeField.selectedIndex = i;
                            found = true;
                            break;
                        }
                    }
                }
                
                // If still no match, try partial match
                if (!found && data.ewaste_type) {
                    for (let i = 0; i < options.length; i++) {
                        if (data.ewaste_type.includes(options[i].value) || 
                            options[i].value.includes(data.ewaste_type)) {
                            console.log('Partial match found at index ' + i + ': ' + options[i].value);
                            ewasteTypeField.selectedIndex = i;
                            found = true;
                            break;
                        }
                    }
                }
                
                // If still not found, set to "Other"
                if (!found) {
                    for (let i = 0; i < options.length; i++) {
                        if (options[i].value === 'Other') {
                            console.log('No match found, defaulting to Other');
                            ewasteTypeField.selectedIndex = i;
                            break;
                        }
                    }
                }
                
                // Trigger a change event so any dependent fields update
                const event = new Event('change');
                ewasteTypeField.dispatchEvent(event);
                
                // Update RAM field if computer-related item
                const ramField = document.getElementById('ram');
                if (ramField && data.ewaste_type) {
                    if (data.ewaste_type === 'Laptop' || data.ewaste_type === 'Desktop-PC') {
                        // Default to a common RAM value
                        ramField.value = '8GB';
                    } else if (data.ewaste_type === 'Smartphone' || data.ewaste_type === 'Tablet') {
                        // For mobile devices
                        ramField.value = '4GB';
                    } else {
                        // For other devices
                        ramField.value = '';
                    }
                }
                
                // Add a visual indication that the field was auto-updated
                ewasteTypeField.classList.add('is-valid');
                
                // Show the autofill message
                if (autofillMessage) {
                    autofillMessage.classList.remove('d-none');
                    setTimeout(() => {
                        autofillMessage.classList.add('d-none');
                    }, 5000);
                }
                
                setTimeout(() => {
                    ewasteTypeField.classList.remove('is-valid');
                }, 3000);
            } else {
                console.log('E-waste type field not found in the form');
            }
            
            // Show recycling information
            if (data.recycling_info) {
                recyclingInfoSection.classList.remove('d-none');
                recyclingInfoSection.innerHTML = `
                    <div class="card shadow-sm mt-3">
                        <div class="card-header bg-info text-white">
                            <h5 class="mb-0">Recycling Information</h5>
                        </div>
                        <div class="card-body">
                            <p>${data.recycling_info}</p>
                        </div>
                    </div>
                `;
            }
        })
        .catch(error => {
            spinner.classList.add('d-none');
            classificationResult.classList.remove('d-none');
            classificationResult.innerHTML = `
                <div class="alert alert-danger">
                    <h5>Error:</h5>
                    <p>${error.message}</p>
                </div>
            `;
        });
    });
});
