// Complaints Management JavaScript

// Initialize complaints functionality
document.addEventListener('DOMContentLoaded', function() {
    if (document.getElementById('complaintsList')) {
        loadComplaints();
    }
    
    if (document.getElementById('complaintStats')) {
        loadComplaintStats();
    }
    
    // New complaint form
    const complaintForm = document.getElementById('complaintForm');
    if (complaintForm) {
        complaintForm.addEventListener('submit', submitComplaint);
    }
    
    // File upload handling
    const fileInput = document.getElementById('complaintAttachments');
    if (fileInput) {
        fileInput.addEventListener('change', handleFileUpload);
    }
});

// Load complaints
async function loadComplaints(filter = 'all') {
    const container = document.getElementById('complaintsList');
    if (!container) return;
    
    showLoading(container);
    
    try {
        const url = filter === 'all' ? '/complaints' : `/complaints?status=${filter}`;
        const response = await apiRequest(url, 'GET');
        
        hideLoading(container);
        
        if (response.success && response.complaints.length > 0) {
            displayComplaints(response.complaints);
        } else {
            loadFallbackComplaints(filter);
        }
    } catch (error) {
        hideLoading(container);
        loadFallbackComplaints(filter);
    }
}

// Display complaints
function displayComplaints(complaints) {
    const container = document.getElementById('complaintsList');
    if (!container) return;
    
    container.innerHTML = complaints.map(complaint => `
        <div class="complaint-card ${complaint.priority}">
            <div class="complaint-header">
                <div>
                    <span class="complaint-id">#${complaint.id}</span>
                    <span class="complaint-date">${formatDate(complaint.created_at)}</span>
                </div>
                <span class="complaint-status status-${complaint.status}">
                    ${formatStatus(complaint.status)}
                </span>
            </div>
            
            <div class="complaint-customer">
                <div class="customer-avatar">${complaint.user_name?.charAt(0) || 'U'}</div>
                <div>
                    <strong>${complaint.user_name || 'Customer'}</strong>
                    ${complaint.provider_name ? `<div style="font-size: 0.85rem; color: #666;">Provider: ${complaint.provider_name}</div>` : ''}
                </div>
            </div>

            <div class="complaint-subject">${complaint.subject}</div>
            <div class="complaint-desc">${complaint.description.substring(0, 100)}${complaint.description.length > 100 ? '...' : ''}</div>
            
            <div class="complaint-meta">
                <span><i class="fas fa-tag"></i> ${formatCategory(complaint.category)}</span>
                <span><i class="fas fa-flag"></i> ${complaint.priority} priority</span>
                <span><i class="fas fa-comment"></i> ${complaint.message_count || 0} messages</span>
            </div>

            <div class="complaint-actions">
                <button class="btn-action btn-view" onclick="viewComplaint('${complaint.id}')">
                    <i class="fas fa-eye"></i> View Details
                </button>
                ${complaint.status !== 'resolved' ? `
                    <button class="btn-action btn-resolve" onclick="resolveComplaint('${complaint.id}')">
                        <i class="fas fa-check"></i> Resolve
                    </button>
                ` : ''}
                ${complaint.status !== 'escalated' && complaint.priority === 'urgent' ? `
                    <button class="btn-action btn-escalate" onclick="escalateComplaint('${complaint.id}')">
                        <i class="fas fa-exclamation-triangle"></i> Escalate
                    </button>
                ` : ''}
            </div>
        </div>
    `).join('');
}

// Format status for display
function formatStatus(status) {
    return status.split('-').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ');
}

// Format category for display
function formatCategory(category) {
    const categories = {
        'food_quality': 'Food Quality',
        'delivery_delay': 'Delivery Delay',
        'wrong_order': 'Wrong Order',
        'missing_items': 'Missing Items',
        'packaging': 'Packaging Issue',
        'payment': 'Payment Issue',
        'subscription': 'Subscription Issue',
        'staff_behavior': 'Staff Behavior',
        'other': 'Other'
    };
    return categories[category] || category;
}

// Load fallback complaints
function loadFallbackComplaints(filter = 'all') {
    const fallbackComplaints = [
        {
            id: 'CMP001',
            created_at: new Date(),
            user_name: 'Rahul Sharma',
            provider_name: 'Spice Kitchen',
            subject: 'Food Quality Issue',
            description: 'The butter chicken was cold and had too much oil. The gravy was separated.',
            category: 'food_quality',
            priority: 'high',
            status: 'pending',
            message_count: 2
        },
        {
            id: 'CMP002',
            created_at: new Date(Date.now() - 86400000),
            user_name: 'Priya Patel',
            provider_name: 'Madras Cafe',
            subject: 'Delivery Delay',
            description: 'Order arrived 45 minutes late. Food was cold.',
            category: 'delivery_delay',
            priority: 'medium',
            status: 'in-progress',
            message_count: 3
        },
        {
            id: 'CMP003',
            created_at: new Date(Date.now() - 172800000),
            user_name: 'Amit Kumar',
            provider_name: 'Punjab Grill',
            subject: 'Wrong Order',
            description: 'Received chicken biryani instead of veg biryani.',
            category: 'wrong_order',
            priority: 'high',
            status: 'escalated',
            message_count: 4
        },
        {
            id: 'CMP004',
            created_at: new Date(Date.now() - 259200000),
            user_name: 'Sneha Reddy',
            provider_name: 'Biryani House',
            subject: 'Missing Items',
            description: 'Raita and salad were missing from the order.',
            category: 'missing_items',
            priority: 'low',
            status: 'resolved',
            message_count: 2
        }
    ];
    
    let filtered = fallbackComplaints;
    if (filter !== 'all') {
        filtered = fallbackComplaints.filter(c => c.status === filter);
    }
    
    displayComplaints(filtered);
}

// Load complaint stats
async function loadComplaintStats() {
    try {
        const response = await apiRequest('/complaints/stats', 'GET');
        
        if (response.success) {
            document.getElementById('totalComplaints').textContent = response.stats.total || 0;
            document.getElementById('pendingComplaints').textContent = response.stats.pending || 0;
            document.getElementById('inProgressComplaints').textContent = response.stats.in_progress || 0;
            document.getElementById('resolvedComplaints').textContent = response.stats.resolved || 0;
            document.getElementById('escalatedComplaints').textContent = response.stats.escalated || 0;
        }
    } catch (error) {
        // Set fallback stats
        document.getElementById('totalComplaints').textContent = '156';
        document.getElementById('pendingComplaints').textContent = '43';
        document.getElementById('inProgressComplaints').textContent = '67';
        document.getElementById('resolvedComplaints').textContent = '34';
        document.getElementById('escalatedComplaints').textContent = '12';
    }
}

// Filter complaints
function filterComplaints(status) {
    document.querySelectorAll('.filter-btn').forEach(btn => btn.classList.remove('active'));
    event.target.classList.add('active');
    loadComplaints(status);
}

// View complaint details
async function viewComplaint(complaintId) {
    try {
        const response = await apiRequest(`/complaints/${complaintId}`, 'GET');
        
        if (response.success) {
            showComplaintModal(response.complaint);
        } else {
            showFallbackComplaintDetails(complaintId);
        }
    } catch (error) {
        showFallbackComplaintDetails(complaintId);
    }
}

// Show complaint modal
function showComplaintModal(complaint) {
    const modal = document.getElementById('complaintModal');
    if (!modal) return;
    
    const messagesHtml = complaint.messages?.map(msg => `
        <div class="message-item">
            <div class="message-avatar">${msg.sender.charAt(0)}</div>
            <div class="message-content">
                <div class="message-header">
                    <span class="message-sender">${msg.sender}</span>
                    <span class="message-time">${formatTime(msg.created_at)}</span>
                </div>
                <div class="message-text">${msg.message}</div>
            </div>
        </div>
    `).join('') || '<p>No messages yet</p>';
    
    const details = document.getElementById('complaintDetails');
    details.innerHTML = `
        <div class="complaint-detail-header">
            <h3>#${complaint.id} - ${complaint.subject}</h3>
            <span class="complaint-status status-${complaint.status}">${formatStatus(complaint.status)}</span>
        </div>
        <div class="complaint-detail-info">
            <p><strong>Customer:</strong> ${complaint.user_name}</p>
            <p><strong>Provider:</strong> ${complaint.provider_name || 'N/A'}</p>
            <p><strong>Category:</strong> ${formatCategory(complaint.category)}</p>
            <p><strong>Priority:</strong> <span class="priority-${complaint.priority}">${complaint.priority}</span></p>
            <p><strong>Description:</strong> ${complaint.description}</p>
        </div>
        <div class="message-thread">
            <h4>Messages</h4>
            ${messagesHtml}
        </div>
    `;
    
    modal.style.display = 'flex';
    modal.classList.add('show');
    
    // Store current complaint ID for reply
    modal.dataset.complaintId = complaint.id;
}

// Show fallback complaint details
function showFallbackComplaintDetails(complaintId) {
    const complaint = {
        id: complaintId,
        user_name: 'Rahul Sharma',
        provider_name: 'Spice Kitchen',
        subject: 'Food Quality Issue',
        description: 'The butter chicken was cold and had too much oil.',
        category: 'food_quality',
        priority: 'high',
        status: 'pending',
        messages: [
            { sender: 'Rahul Sharma', message: 'The food was cold and not fresh', created_at: new Date() },
            { sender: 'Support', message: 'We are investigating this issue', created_at: new Date(Date.now() - 3600000) }
        ]
    };
    showComplaintModal(complaint);
}

// Send reply
async function sendReply() {
    const modal = document.getElementById('complaintModal');
    const complaintId = modal?.dataset.complaintId;
    const message = document.getElementById('replyMessage')?.value;
    
    if (!complaintId || !message) return;
    
    try {
        const response = await apiRequest(`/complaints/${complaintId}/message`, 'POST', {
            message: message
        });
        
        if (response.success) {
            showAlert('Reply sent successfully', 'success');
            document.getElementById('replyMessage').value = '';
            viewComplaint(complaintId); // Reload complaint details
        }
    } catch (error) {
        showAlert('Failed to send reply', 'error');
    }
}

// Resolve complaint
async function resolveComplaint(complaintId) {
    if (!confirm('Mark this complaint as resolved?')) return;
    
    try {
        const response = await apiRequest(`/complaints/${complaintId}/resolve`, 'POST', {
            resolution: 'Issue resolved'
        });
        
        if (response.success) {
            showAlert('Complaint resolved successfully', 'success');
            loadComplaints();
            closeModal();
        }
    } catch (error) {
        showAlert('Failed to resolve complaint', 'error');
    }
}

// Escalate complaint
async function escalateComplaint(complaintId) {
    const reason = prompt('Reason for escalation:');
    if (!reason) return;
    
    try {
        const response = await apiRequest(`/complaints/${complaintId}/escalate`, 'POST', {
            reason: reason
        });
        
        if (response.success) {
            showAlert('Complaint escalated successfully', 'success');
            loadComplaints();
        }
    } catch (error) {
        showAlert('Failed to escalate complaint', 'error');
    }
}

// File new complaint
async function submitComplaint(e) {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const data = Object.fromEntries(formData.entries());
    
    // Handle file attachments
    const files = document.getElementById('complaintAttachments')?.files;
    if (files && files.length > 0) {
        // In a real app, you would upload files here
        data.attachments = Array.from(files).map(f => f.name);
    }
    
    try {
        const response = await apiRequest('/complaints/create', 'POST', data);
        
        if (response.success) {
            showAlert('Complaint filed successfully', 'success');
            setTimeout(() => {
                window.location.href = 'complaints.html';
            }, 1500);
        }
    } catch (error) {
        showAlert('Failed to file complaint', 'error');
    }
}

// Handle file upload
function handleFileUpload(e) {
    const files = e.target.files;
    const fileList = document.getElementById('fileList');
    
    if (!fileList) return;
    
    fileList.innerHTML = '';
    Array.from(files).forEach(file => {
        const fileItem = document.createElement('div');
        fileItem.className = 'file-item';
        fileItem.innerHTML = `
            <span><i class="fas fa-file"></i> ${file.name}</span>
            <span class="file-size">${(file.size / 1024).toFixed(2)} KB</span>
        `;
        fileList.appendChild(fileItem);
    });
}

// Close modal
function closeModal() {
    document.querySelectorAll('.modal').forEach(modal => {
        modal.style.display = 'none';
        modal.classList.remove('show');
    });
}

// Search complaints
document.getElementById('searchInput')?.addEventListener('input', function(e) {
    const searchTerm = e.target.value.toLowerCase();
    // Implement search functionality
});