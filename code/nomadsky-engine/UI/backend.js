// Get form values and display them
// const source = '{{source}}';
const destination = '{{destination}}';
const vmname = '{{vmname}}';

const source = document.getElementById('source-platform').value;
// document.getElementById('source-platform').textContent = source;
document.getElementById('dest-platform').textContent = destination;
document.getElementById('vm-name').textContent = vmname;

// Update step status
function updateStep(stepId, status, customMessage = null, extraData = null) {
    const step = document.getElementById(stepId);
    const icon = step.querySelector('.status-icon');
    const description = step.querySelector('.status-description');
    
    step.classList.remove('pending', 'running', 'completed', 'error');
    step.classList.add(status);
    
    if (status === 'running') {
        icon.innerHTML = '<div class="spinner"></div>';
    } else if (status === 'completed') {
        icon.innerHTML = '<span class="checkmark">✓</span>';
    } else if (status === 'error') {
        icon.innerHTML = '<span class="error-icon">✗</span>';
    } else {
        icon.innerHTML = '<span class="pending-icon">○</span>';
    }
    
    if (customMessage) {
        description.textContent = customMessage;
    }
    
    if (extraData) {
        const existingExtra = step.querySelector('.error-details, .vm-list');
        if (existingExtra) existingExtra.remove();
        
        const extraDiv = document.createElement('div');
        extraDiv.className = extraData.type === 'error' ? 'error-details' : 'vm-list';
        
        if (extraData.type === 'error') {
            extraDiv.textContent = extraData.message;
        } else if (extraData.type === 'vm-list') {
            extraDiv.innerHTML = `
                <div class="vm-list-title">Available VMs found:</div>
                <ul>${extraData.vms.map(vm => `<li>${vm}</li>`).join('')}</ul>
            `;
        }
        
        step.querySelector('.status-content').appendChild(extraDiv);
    }
}

// Run a single script via Flask
async function runScript(stepId, scriptName, successMessage, sharedData) {
    updateStep(stepId, 'running', 'Processing...');
    
    const bodyObj = {
        script: scriptName,
        source: source,
        destination: destination,
        vmname: vmname,
        extraValue: sharedData
    };
    const body = JSON.stringify(bodyObj);  
    try {     
            const response = await fetch('http://localhost:5000/api/run-script', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: body 
        });
        const result = await response.json();

        if (result.success) {
            const data = JSON.parse(result.output);
            updateStep(stepId, 'completed', data.message);
            return result
        } else {
            updateStep(stepId, 'error', 'Script failed', {
                type: 'error',
                message: result.error
            });
            return false;
        }
    } catch (error) {
        updateStep(stepId, 'error', error.message, {
            type: 'error',
            message: error.message
        });
        return false;
    }
}
// successMessage ||

    
// Run all migration steps
async function runMigration() {
    const steps = [
        { id: 'step1', script: 'fetch_vm.py', message: 'VM found successfully!'},  
        { id: 'step2', script: 'stop_vm.py', message: 'VM stopped successfully' },
        { id: 'step3', script: 'download_vm.py', message: 'Download completed' },
        { id: 'step4', script: 'transform_vm.py', message: 'Format conversion completed'},
        { id: 'step5', script: 'create_network.py', message: 'Network resources created' },
        { id: 'step6', script: 'upload_image.py', message: 'Upload completed successfully' },
        { id: 'step7', script: 'start_vm.py', message: 'VM is now running!' }
    ];

    let sharedData = {
    whatastart: 'empthy'
    }; // Store data from previous steps
    
    for (const step of steps) {
        const success = await runScript(step.id, step.script, step.message, sharedData);
        if (!success.success) {
            return; // Stop on error
        }
        // Parse output and add to shared data
        const dataout = JSON.parse(success.output);
        sharedData = { ...sharedData, ...dataout }; // Merge new data
        
        await new Promise(resolve => setTimeout(resolve, 500)); // Small delay between steps
    }
    
    // Show success banner
    setTimeout(() => {
        document.getElementById('success-banner').classList.add('show');
    }, 500);
}

// Start migration when page loads
window.addEventListener('load', runMigration);
