// Global state for tracking progress
let completedTasks = new Set();
let expandedMilestones = new Set();

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    initializeRoadmap();
    updateProgress();
    setupEventListeners();
    setupAccessibility();
});

// Initialize roadmap state
function initializeRoadmap() {
    // Set first milestone as expanded by default
    expandedMilestones.add(1);
    updateMilestoneDisplay(1);
}

// Setup event listeners
function setupEventListeners() {
    // Handle navigation placeholder links
    document.addEventListener('click', function(e) {
        // Only prevent default for placeholder links, not external links
        if (e.target.classList.contains('placeholder') || e.target.closest('.placeholder')) {
            e.preventDefault();
            showToast('This page is coming soon! 🚧');
            return;
        }
        
        // Handle internal anchor links
        if (e.target.matches('a[href^="#"]')) {
            e.preventDefault();
            const target = document.querySelector(e.target.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
            return;
        }
        
        // External links should work normally - don't prevent default
    });

    // Handle milestone expansion keyboard navigation
    document.addEventListener('keydown', function(e) {
        if (e.target.classList.contains('milestone-header') && (e.key === 'Enter' || e.key === ' ')) {
            e.preventDefault();
            const milestoneId = parseInt(e.target.closest('.milestone').dataset.milestone);
            toggleMilestone(milestoneId);
        }
        
        if (e.target.classList.contains('task-checkbox') && (e.key === 'Enter' || e.key === ' ')) {
            e.preventDefault();
            const taskId = e.target.closest('.task').dataset.task;
            toggleTask(taskId);
        }
    });
}

// Toggle milestone expansion
function toggleMilestone(milestoneId) {
    const milestone = document.querySelector(`[data-milestone="${milestoneId}"]`);
    if (!milestone) return;

    if (expandedMilestones.has(milestoneId)) {
        expandedMilestones.delete(milestoneId);
        milestone.classList.remove('expanded');
    } else {
        expandedMilestones.add(milestoneId);
        milestone.classList.add('expanded');
    }

    updateMilestoneDisplay(milestoneId);
    updateAccessibility();
}

// Update milestone visual state
function updateMilestoneDisplay(milestoneId) {
    const milestone = document.querySelector(`[data-milestone="${milestoneId}"]`);
    if (!milestone) return;

    const details = milestone.querySelector(`#details-${milestoneId}`);
    const toggle = milestone.querySelector('.milestone-toggle');

    if (expandedMilestones.has(milestoneId)) {
        milestone.classList.add('expanded');
        if (details) {
            details.style.maxHeight = details.scrollHeight + 'px';
        }
        if (toggle) {
            toggle.style.transform = 'rotate(180deg)';
        }
    } else {
        milestone.classList.remove('expanded');
        if (details) {
            details.style.maxHeight = '0px';
        }
        if (toggle) {
            toggle.style.transform = 'rotate(0deg)';
        }
    }
}

// Toggle task completion
function toggleTask(taskId) {
    const taskElement = document.querySelector(`[data-task="${taskId}"]`);
    const checkbox = taskElement?.querySelector('.task-checkbox');
    
    if (!taskElement || !checkbox) return;

    if (completedTasks.has(taskId)) {
        // Mark as incomplete
        completedTasks.delete(taskId);
        checkbox.classList.remove('completed');
        taskElement.classList.remove('completed');
    } else {
        // Mark as complete
        completedTasks.add(taskId);
        checkbox.classList.add('completed');
        taskElement.classList.add('completed');
        
        // Add celebration effect
        checkbox.style.animation = 'celebrate 0.5s ease-out';
        setTimeout(() => {
            checkbox.style.animation = '';
        }, 500);
    }

    // Update milestone status
    updateMilestoneStatus(taskId);
    updateProgress();
    updateAccessibility();
    
    // Auto-expand next milestone if current one is complete
    autoExpandNextMilestone();
}

// Update milestone completion status
function updateMilestoneStatus(taskId) {
    const milestoneId = parseInt(taskId.split('-')[0]);
    const milestone = document.querySelector(`[data-milestone="${milestoneId}"]`);
    const statusIndicator = document.querySelector(`#status-${milestoneId}`);
    
    if (!milestone || !statusIndicator) return;

    // Count completed tasks in this milestone
    const allTasks = milestone.querySelectorAll('.task');
    const completedInMilestone = Array.from(allTasks).filter(task => 
        completedTasks.has(task.dataset.task)
    ).length;

    // Update milestone status
    if (completedInMilestone === allTasks.length && allTasks.length > 0) {
        // Milestone complete
        statusIndicator.classList.add('completed');
        milestone.classList.add('completed');
        
        // Celebrate milestone completion
        const icon = milestone.querySelector('.milestone-icon');
        if (icon) {
            icon.style.animation = 'celebrate 0.8s ease-out';
            setTimeout(() => {
                icon.style.animation = '';
            }, 800);
        }
    } else {
        // Milestone incomplete
        statusIndicator.classList.remove('completed');
        milestone.classList.remove('completed');
    }
}

// Auto-expand next milestone when current is complete
function autoExpandNextMilestone() {
    const milestones = document.querySelectorAll('.milestone');
    
    for (let i = 0; i < milestones.length; i++) {
        const milestone = milestones[i];
        const milestoneId = parseInt(milestone.dataset.milestone);
        const allTasks = milestone.querySelectorAll('.task');
        const completedInMilestone = Array.from(allTasks).filter(task => 
            completedTasks.has(task.dataset.task)
        ).length;

        // If this milestone is complete and next exists
        if (completedInMilestone === allTasks.length && allTasks.length > 0) {
            const nextMilestone = milestones[i + 1];
            if (nextMilestone) {
                const nextMilestoneId = parseInt(nextMilestone.dataset.milestone);
                if (!expandedMilestones.has(nextMilestoneId)) {
                    // Small delay for better UX
                    setTimeout(() => {
                        expandedMilestones.add(nextMilestoneId);
                        updateMilestoneDisplay(nextMilestoneId);
                    }, 500);
                }
            }
        }
    }
}

// Update overall progress
function updateProgress() {
    const totalTasks = document.querySelectorAll('.task').length;
    const completedCount = completedTasks.size;
    const percentage = totalTasks > 0 ? Math.round((completedCount / totalTasks) * 100) : 0;
    
    // Update progress bar
    const progressFill = document.getElementById('progressFill');
    const progressText = document.getElementById('progressText');
    const progressStats = document.getElementById('progressStats');
    
    if (progressFill) {
        progressFill.style.width = percentage + '%';
    }
    
    if (progressText) {
        progressText.textContent = `${percentage}% Complete`;
    }
    
    // Update milestone stats
    const completedMilestones = getCompletedMilestonesCount();
    const totalMilestones = document.querySelectorAll('.milestone').length;
    
    if (progressStats) {
        progressStats.textContent = `${completedMilestones}/${totalMilestones} Milestones`;
    }
}

// Get number of completed milestones
function getCompletedMilestonesCount() {
    const milestones = document.querySelectorAll('.milestone');
    let count = 0;
    
    milestones.forEach(milestone => {
        const allTasks = milestone.querySelectorAll('.task');
        const completedInMilestone = Array.from(allTasks).filter(task => 
            completedTasks.has(task.dataset.task)
        ).length;
        
        if (completedInMilestone === allTasks.length && allTasks.length > 0) {
            count++;
        }
    });
    
    return count;
}

// Scroll to roadmap section
function scrollToRoadmap() {
    const roadmapSection = document.getElementById('roadmap');
    if (roadmapSection) {
        roadmapSection.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
        });
    }
}

// Reset all progress
function resetProgress() {
    if (confirm('Are you sure you want to reset all progress? This will mark all tasks as incomplete.')) {
        // Clear completed tasks
        completedTasks.clear();
        
        // Reset all visual states
        document.querySelectorAll('.task-checkbox').forEach(checkbox => {
            checkbox.classList.remove('completed');
        });
        
        document.querySelectorAll('.task').forEach(task => {
            task.classList.remove('completed');
        });
        
        document.querySelectorAll('.milestone-status').forEach(status => {
            status.classList.remove('completed');
        });
        
        document.querySelectorAll('.milestone').forEach(milestone => {
            milestone.classList.remove('completed');
        });
        
        // Collapse all milestones except first
        expandedMilestones.clear();
        expandedMilestones.add(1);
        
        document.querySelectorAll('.milestone').forEach(milestone => {
            const milestoneId = parseInt(milestone.dataset.milestone);
            updateMilestoneDisplay(milestoneId);
        });
        
        // Update progress and accessibility
        updateProgress();
        updateAccessibility();
        
        // Scroll to top
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    }
}

// Utility function to get next incomplete task
function getNextIncompleteTask() {
    const allTasks = document.querySelectorAll('.task');
    
    for (let task of allTasks) {
        if (!completedTasks.has(task.dataset.task)) {
            return task;
        }
    }
    return null;
}

// Focus on next incomplete task
function focusNextTask() {
    const nextTask = getNextIncompleteTask();
    if (nextTask) {
        const milestoneId = parseInt(nextTask.dataset.task.split('-')[0]);
        
        // Expand milestone if needed
        if (!expandedMilestones.has(milestoneId)) {
            toggleMilestone(milestoneId);
        }
        
        // Scroll to task
        nextTask.scrollIntoView({
            behavior: 'smooth',
            block: 'center'
        });
        
        // Highlight task briefly
        nextTask.style.background = 'var(--color-bg-1)';
        setTimeout(() => {
            nextTask.style.background = '';
        }, 2000);
    }
}

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + K to focus next task
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        focusNextTask();
    }
    
    // Escape to collapse all milestones
    if (e.key === 'Escape') {
        expandedMilestones.clear();
        document.querySelectorAll('.milestone').forEach(milestone => {
            const milestoneId = parseInt(milestone.dataset.milestone);
            updateMilestoneDisplay(milestoneId);
        });
    }
});

// Add visual feedback for interactions
document.addEventListener('mousedown', function(e) {
    if (e.target.classList.contains('task-checkbox') || e.target.closest('.milestone-header')) {
        e.target.style.transform = 'scale(0.95)';
    }
});

document.addEventListener('mouseup', function(e) {
    if (e.target.classList.contains('task-checkbox') || e.target.closest('.milestone-header')) {
        e.target.style.transform = '';
    }
});

// Simple toast notification function
function showToast(message) {
    // Remove existing toast if any
    const existingToast = document.querySelector('.toast');
    if (existingToast) {
        existingToast.remove();
    }
    
    // Create toast element
    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.textContent = message;
    toast.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: var(--color-surface);
        color: var(--color-text);
        padding: var(--space-12) var(--space-16);
        border-radius: var(--radius-base);
        border: 1px solid var(--color-border);
        box-shadow: var(--shadow-lg);
        z-index: 1000;
        opacity: 0;
        transform: translateY(-20px);
        transition: all var(--duration-normal) var(--ease-standard);
    `;
    
    document.body.appendChild(toast);
    
    // Animate in
    requestAnimationFrame(() => {
        toast.style.opacity = '1';
        toast.style.transform = 'translateY(0)';
    });
    
    // Remove after 3 seconds
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateY(-20px)';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// Add accessibility improvements
function setupAccessibility() {
    // Add ARIA labels and roles
    document.querySelectorAll('.milestone-header').forEach((header, index) => {
        header.setAttribute('role', 'button');
        header.setAttribute('aria-expanded', 'false');
        header.setAttribute('tabindex', '0');
        header.setAttribute('aria-label', `Expand milestone ${index + 1}`);
    });
    
    document.querySelectorAll('.task-checkbox').forEach((checkbox, index) => {
        checkbox.setAttribute('role', 'checkbox');
        checkbox.setAttribute('aria-checked', 'false');
        checkbox.setAttribute('tabindex', '0');
        checkbox.setAttribute('aria-label', `Mark task ${index + 1} as complete`);
    });
}

// Update ARIA attributes when state changes
function updateAccessibility() {
    document.querySelectorAll('.milestone-header').forEach((header) => {
        const milestone = header.closest('.milestone');
        const milestoneId = parseInt(milestone.dataset.milestone);
        const isExpanded = expandedMilestones.has(milestoneId);
        header.setAttribute('aria-expanded', isExpanded.toString());
    });
    
    document.querySelectorAll('.task-checkbox').forEach((checkbox) => {
        const task = checkbox.closest('.task');
        const taskId = task.dataset.task;
        const isCompleted = completedTasks.has(taskId);
        checkbox.setAttribute('aria-checked', isCompleted.toString());
    });
}

// Export functions for global access (needed for onclick handlers)
window.toggleMilestone = toggleMilestone;
window.toggleTask = toggleTask;
window.scrollToRoadmap = scrollToRoadmap;
window.resetProgress = resetProgress;