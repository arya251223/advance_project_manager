const API_URL = 'http://localhost:8000';

// DOM Elements
const projectForm = document.getElementById('projectForm');
const statusSection = document.getElementById('statusSection');
const projectsList = document.getElementById('projectsList');
const submitBtn = document.getElementById('submitBtn');
const downloadBtn = document.getElementById('downloadBtn');
const newProjectBtn = document.getElementById('newProjectBtn');
const toast = document.getElementById('toast');

// State
let currentProjectId = null;
let statusCheckInterval = null;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadProjects();
    checkAPIHealth();
});

// Form submission
projectForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const formData = new FormData(projectForm);
    const requirements = formData.get('requirements')
        .split('\n')
        .filter(r => r.trim())
        .map(r => r.trim());
    
    const projectData = {
        title: formData.get('title'),
        description: formData.get('description'),
        project_type: formData.get('project_type'),
        requirements: requirements
    };
    
    await submitProject(projectData);
});

// Submit project to API
async function submitProject(projectData) {
    try {
        // Update UI
        submitBtn.classList.add('loading');
        submitBtn.disabled = true;
        
        // Send request
        const response = await fetch(`${API_URL}/assign_project`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(projectData)
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        currentProjectId = result.project_id;
        
        // Show status section
        showStatus(result);
        
        // Start checking status
        startStatusChecking();
        
        // Show success message
        showToast('Project submitted successfully!', 'success');
        
        // Reset form
        projectForm.reset();
        
    } catch (error) {
        console.error('Error submitting project:', error);
        showToast('Failed to submit project. Please try again.', 'error');
    } finally {
        submitBtn.classList.remove('loading');
        submitBtn.disabled = false;
    }
}

// Show project status
function showStatus(project) {
    statusSection.style.display = 'block';
    
    const statusTitle = document.getElementById('statusTitle');
    const statusBadge = document.getElementById('statusBadge');
    const statusDetails = document.getElementById('statusDetails');
    const statusActions = document.getElementById('statusActions');
    const progressFill = document.getElementById('progressFill');
    
    // Update status display
    statusTitle.textContent = project.title || 'Generating Project...';
    
    // Update badge
    statusBadge.className = 'status-badge';
    if (project.status === 'completed') {
        statusBadge.classList.add('completed');
        statusBadge.textContent = 'Completed';
        statusActions.style.display = 'flex';
        progressFill.style.width = '100%';
    } else if (project.status === 'failed') {
        statusBadge.classList.add('failed');
        statusBadge.textContent = 'Failed';
        progressFill.style.width = '100%';
    } else {
        statusBadge.classList.add('in-progress');
        statusBadge.textContent = 'In Progress';
        statusActions.style.display = 'none';
        animateProgress();
    }
    
    // Update details
    statusDetails.innerHTML = `
        <p><strong>Project ID:</strong> ${project.project_id}</p>
        <p><strong>Status:</strong> ${project.message}</p>
        <p><strong>Created:</strong> ${new Date(project.created_at).toLocaleString()}</p>
    `;
}

// Animate progress bar
function animateProgress() {
    const progressFill = document.getElementById('progressFill');
    let progress = 0;
    
    const progressInterval = setInterval(() => {
        if (progress < 90) {
            progress += Math.random() * 10;
            progressFill.style.width = `${Math.min(progress, 90)}%`;
        }
    }, 2000);
    
    // Store interval to clear later
    progressFill.dataset.interval = progressInterval;
}

// Start checking project status
function startStatusChecking() {
    if (statusCheckInterval) {
        clearInterval(statusCheckInterval);
    }
    
    statusCheckInterval = setInterval(async () => {
        if (!currentProjectId) return;
        
        try {
            const response = await fetch(`${API_URL}/project/${currentProjectId}/status`);
            if (!response.ok) throw new Error('Failed to get status');
            
            const project = await response.json();
            
            // Update status display
            showStatus(project);
            
            // Stop checking if completed or failed
            if (project.status === 'completed' || project.status === 'failed') {
                stopStatusChecking();
                
                if (project.status === 'completed') {
                    showToast('Project completed successfully!', 'success');
                } else {
                    showToast('Project generation failed.', 'error');
                }
                
                // Reload projects list
                loadProjects();
            }
        } catch (error) {
            console.error('Error checking status:', error);
        }
    }, 5000); // Check every 5 seconds
}

// Stop status checking
function stopStatusChecking() {
    if (statusCheckInterval) {
        clearInterval(statusCheckInterval);
        statusCheckInterval = null;
    }
    
    // Clear progress animation
    const progressFill = document.getElementById('progressFill');
    if (progressFill.dataset.interval) {
        clearInterval(progressFill.dataset.interval);
    }
}

// Download project
downloadBtn.addEventListener('click', async () => {
    if (!currentProjectId) return;
    
    try {
        // Create download link
        const downloadUrl = `${API_URL}/download/${currentProjectId}`;
        
        // Create temporary link and click it
        const link = document.createElement('a');
        link.href = downloadUrl;
        link.download = `project_${currentProjectId}.zip`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        showToast('Download started!', 'success');
    } catch (error) {
        console.error('Error downloading project:', error);
        showToast('Failed to download project.', 'error');
    }
});

// Create new project
newProjectBtn.addEventListener('click', () => {
    statusSection.style.display = 'none';
    currentProjectId = null;
    stopStatusChecking();
    projectForm.scrollIntoView({ behavior: 'smooth' });
});

// Load projects list
async function loadProjects() {
    try {
        const response = await fetch(`${API_URL}/projects`);
        if (!response.ok) throw new Error('Failed to load projects');
        
        const data = await response.json();
        displayProjects(data.projects);
    } catch (error) {
        console.error('Error loading projects:', error);
    }
}

// Display projects
function displayProjects(projects) {
    const projectsContainer = document.getElementById('projectsContainer');
    
    if (projects.length === 0) {
        projectsContainer.innerHTML = '<p class="empty-state">No projects yet. Create your first project above!</p>';
        return;
    }
    
    projectsContainer.innerHTML = projects.map(project => `
        <div class="project-item">
            <div class="project-info">
                <h3>Project ${project.project_id.substring(0, 8)}...</h3>
                <div class="project-meta">
                    <span>Status: ${project.status}</span> • 
                    <span>${new Date(project.created_at).toLocaleDateString()}</span>
                </div>
            </div>
            <div class="project-actions">
                ${project.status === 'completed' ? 
                    `<button class="btn btn-success" onclick="downloadProject('${project.project_id}')">Download</button>` : 
                    `<span class="status-badge ${project.status}">${project.status}</span>`
                }
            </div>
        </div>
    `).join('');
}

// Download specific project
window.downloadProject = async (projectId) => {
    try {
        const downloadUrl = `${API_URL}/download/${projectId}`;
        
        const link = document.createElement('a');
        link.href = downloadUrl;
        link.download = `project_${projectId}.zip`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        showToast('Download started!', 'success');
    } catch (error) {
        console.error('Error downloading project:', error);
        showToast('Failed to download project.', 'error');
    }
};

// Check API health
async function checkAPIHealth() {
    try {
        const response = await fetch(`${API_URL}/health`);
        if (!response.ok) throw new Error('API is not healthy');
        
        const data = await response.json();
        console.log('API Health:', data);
    } catch (error) {
        console.error('API Health Check Failed:', error);
        showToast('Cannot connect to API. Please ensure the backend is running.', 'error');
    }
}

// Show toast notification
function showToast(message, type = 'info') {
    toast.textContent = message;
    toast.className = `toast ${type}`;
    toast.classList.add('show');
    
    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

// Handle errors globally
window.addEventListener('error', (event) => {
    console.error('Global error:', event.error);
    showToast('An unexpected error occurred.', 'error');
});

// Handle unhandled promise rejections
window.addEventListener('unhandledrejection', (event) => {
    console.error('Unhandled promise rejection:', event.reason);
    showToast('An unexpected error occurred.', 'error');
});