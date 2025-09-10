// Global variables
let currentUser = null;
let groups = [];
let students = [];
let attendanceRecords = [];
let customFields = [
    { name: 'studentId', label: 'Student ID', required: true },
    { name: 'phone', label: 'Phone Number', required: false }
];

// Authentication functions

function switchTab(tabName, event) {
    document.querySelectorAll('.tab-button').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));

    event.target.classList.add('active');
    document.getElementById(tabName).classList.add('active');
}

function selectRole(role, event) {
    document.querySelectorAll('.role-option').forEach(option => option.classList.remove('selected'));

    event.currentTarget.classList.add('selected');
    document.getElementById('selectedRole').value = role;
}

// For login and signup, instead of client-side redirect, submit to Flask backend normally via forms.

// Logout calls Flask logout route
function logout() {
    // Redirect to Flask /logout route to clear server session
    window.location.href = '/logout';
}

// Dashboard functions

function showTab(tabName, event) {
    document.querySelectorAll('.nav-tab').forEach(tab => tab.classList.remove('active'));
    document.querySelectorAll('.tab-pane').forEach(pane => pane.classList.remove('active'));

    event.target.classList.add('active');
    document.getElementById(tabName).classList.add('active');

    if (tabName === 'groups') {
        loadGroups();
    } else if (tabName === 'students') {
        loadStudents();
    } else if (tabName === 'links') {
        loadLinks();
    } else if (tabName === 'attendance') {
        loadAttendanceRecords();
    } else if (tabName === 'reports') {
        loadReports();
    }
}

// Instructor Dashboard Functions

function loadGroups() {
    const container = document.getElementById('groupsGrid');
    if (!container) return;

    container.innerHTML = groups.map(group => `
        <div class="card">
            <div class="card-header" style="display: flex; justify-content: space-between; align-items: center;">
                <h4>${group.name}</h4>
                <span class="badge badge-primary">${group.studentCount} students</span>
            </div>
            <div style="margin-bottom: 1rem;">
                <p style="margin-bottom: 0.5rem; color: var(--gray-600);">${group.description}</p>
                <div style="font-size: 0.875rem; color: var(--gray-500);">
                    <p style="margin: 0;">Department: ${group.department}</p>
                    <p style="margin: 0;">Class: ${group.class} | Section: ${group.section}</p>
                </div>
            </div>
            <div style="background-color: var(--gray-50); padding: 1rem; border-radius: var(--border-radius); margin-bottom: 1rem;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-weight: 500;">Attendance Rate</span>
                    <span style="font-size: 1.125rem; font-weight: 700; color: var(--success);">${group.attendancePercentage}%</span>
                </div>
            </div>
            <div style="display: flex; gap: 0.5rem;">
                <button class="btn btn-secondary btn-small" onclick="generateRegistrationLink('${group.id}')"
                    style="flex: 1;">
                    <i class="fas fa-copy"></i>
                    Registration
                </button>
                <button class="btn btn-primary btn-small" onclick="generateAttendanceLink('${group.id}')"
                    style="flex: 1;">
                    <i class="fas fa-copy"></i>
                    Attendance
                </button>
            </div>
        </div>
    `).join('');

    const attendanceGrid = document.getElementById('groupAttendanceGrid');
    if (attendanceGrid) {
        attendanceGrid.innerHTML = groups.map(group => `
            <div style="padding: 1rem; background-color: var(--gray-50); border-radius: var(--border-radius);">
                <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 1rem;">
                    <div>
                        <h4 style="margin-bottom: 0.25rem;">${group.name}</h4>
                        <p style="font-size: 0.875rem; color: var(--gray-600); margin: 0;">${group.department} - ${group.class}-${group.section}</p>
                    </div>
                    <span class="badge badge-primary">${group.studentCount} students</span>
                </div>
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-size: 0.875rem; color: var(--gray-600);">Attendance</span>
                    <span style="font-size: 1.125rem; font-weight: 700; color: var(--success);">${group.attendancePercentage}%</span>
                </div>
            </div>
        `).join('');
    }
}

function loadStudents() {
    const container = document.getElementById('studentsTable');
    if (!container) return;

    container.innerHTML = `
        <div style="overflow-x: auto;">
            <table style="width: 100%; border-collapse: collapse;">
                <thead style="background-color: var(--gray-50);">
                    <tr>
                        <th style="padding: 1rem; text-align: left; border-bottom: 1px solid var(--gray-200);">Name</th>
                        <th style="padding: 1rem; text-align: left; border-bottom: 1px solid var(--gray-200);">Email</th>
                        <th style="padding: 1rem; text-align: left; border-bottom: 1px solid var(--gray-200);">Student ID</th>
                        <th style="padding: 1rem; text-align: left; border-bottom: 1px solid var(--gray-200);">Group</th>
                        <th style="padding: 1rem; text-align: left; border-bottom: 1px solid var(--gray-200);">Attendance</th>
                        <th style="padding: 1rem; text-align: left; border-bottom: 1px solid var(--gray-200);">Actions</th>
                    </tr>
                </thead>
                <tbody>
                    ${students.map(student => {
                        const group = groups.find(g => g.id === student.groupId);
                        const attendance = Math.floor(Math.random() * 20) + 80; // Replace with real attendance data
                        return `
                            <tr style="border-bottom: 1px solid var(--gray-200);">
                                <td style="padding: 1rem;">${student.name}</td>
                                <td style="padding: 1rem;">${student.email}</td>
                                <td style="padding: 1rem;">${student.studentId}</td>
                                <td style="padding: 1rem;">${group ? group.name : 'N/A'}</td>
                                <td style="padding: 1rem;">
                                    <span class="badge ${attendance >= 90 ? 'badge-success' : attendance >= 75 ? 'badge-warning' : 'badge-error'}">
                                        ${attendance}%
                                    </span>
                                </td>
                                <td style="padding: 1rem;">
                                    <button class="btn btn-secondary btn-small">
                                        <i class="fas fa-eye"></i>
                                        View
                                    </button>
                                </td>
                            </tr>
                        `;
                    }).join('')}
                </tbody>
            </table>
        </div>
    `;
}

// Initialize dashboard on page load
document.addEventListener('DOMContentLoaded', function() {
    if (window.location.pathname.includes('instructor-dashboard')) {
        loadGroups();
        loadStudents();
    } else if (window.location.pathname.includes('student-dashboard')) {
        if (typeof loadStudentDashboard === 'function') {
            loadStudentDashboard();
        }
    }

    document.addEventListener('click', function(event) {
        if (event.target.classList.contains('modal')) {
            event.target.classList.remove('show');
        }
    });
});


async function handleCreateGroup(event) {
  event.preventDefault();

  const groupName = event.target.querySelector('input[placeholder="e.g., Computer Science - 101"]').value;
  const description = event.target.querySelector('input[placeholder="Brief description of the group"]').value;
  const department = event.target.querySelector('input[placeholder="CS"]').value;
  const className = event.target.querySelector('input[placeholder="101"]').value;
  const section = event.target.querySelector('input[placeholder="A"]').value;

  const res = await fetch('/create-group', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name: groupName, description, department, class: className, section })
  });

  const data = await res.json();
  if (res.ok) {
    alert('Group created successfully!');
    closeModal('createGroupModal');
    // Refresh groups grid or fetch new data
  } else {
    alert('Error: ' + data.error);
  }
}
// Modal open karne ke liye
function showCreateGroupModal() {
  const modal = document.getElementById('createGroupModal');
  if (modal) {
    modal.classList.add('show');
  }
}

// Modal close karne ke liye
function closeModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) {
    modal.classList.remove('show');
  }
}
async function loadGroups() {
    const container = document.getElementById('groupsGrid');
    if (!container) return;

    try {
        const response = await fetch('/get-groups');
        if (!response.ok) throw new Error('Failed to fetch groups');
        const data = await response.json();
        const groups = data.groups || [];

        container.innerHTML = groups.map(group => `
            <div class="card" style="margin-bottom: 1rem; padding: 1rem;">
                <div class="card-header" style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                    <h4>${group.name}</h4>
                    <span class="badge badge-primary">${group.studentCount} students</span>
                </div>
                <div style="margin-bottom: 1rem;">
                    <p style="margin-bottom: 0.5rem; color: var(--gray-600);">${group.description || ''}</p>
                    <div style="font-size: 0.875rem; color: var(--gray-500);">
                        <p style="margin: 0;">Department: ${group.department}</p>
                        <p style="margin: 0;">Class: ${group.class} | Section: ${group.section}</p>
                    </div>
                </div>
                <div style="background-color: var(--gray-50); padding: 1rem; border-radius: var(--border-radius); margin-bottom: 1rem;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-weight: 500;">Attendance Rate</span>
                        <span style="font-size: 1.125rem; font-weight: 700; color: var(--success);">${group.attendancecount || 0}%</span>
                    </div>
                </div>
                <div style="display: flex; gap: 0.5rem;">
                    <button class="btn btn-secondary btn-small" onclick="copyToClipboard('${window.location.origin}/register/${group.registration_link}')"
                        style="flex: 1;">
                        <i class="fas fa-copy"></i> Copy Registration Link
                    </button>
                    <button class="btn btn-primary btn-small" onclick="copyToClipboard('${window.location.origin}/attendance/${group.attendance_link}')"
                        style="flex: 1;">
                        <i class="fas fa-copy"></i> Copy Attendance Link
                    </button>
                </div>
            </div>
        `).join('');

    } catch (err) {
        console.error('Error loading groups:', err);
        container.innerHTML = '<p style="color:red;">Failed to load groups.</p>';
    }
}

function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        alert('Link copied to clipboard:\n' + text);
    }).catch(() => {
        alert('Failed to copy the link.');
    });
}

window.onload = () => {
    loadGroups();
};

// Tab switch handler (if needed)
function showTab(tabId, evt) {
    evt.preventDefault();
    document.querySelectorAll('.tab-pane').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.nav-tab').forEach(t => t.classList.remove('active'));

    document.getElementById(tabId).classList.add('active');
    evt.currentTarget.classList.add('active');
}
async function loadDashboardStats() {
    try {
        const response = await fetch('/dashboard-stats');
        if (!response.ok) throw new Error('Failed to fetch dashboard stats');
        const data = await response.json();

        document.getElementById('totalGroups').textContent = data.totalGroups || 0;
        document.getElementById('totalStudents').textContent = data.totalStudents || 0;
        document.getElementById('overallAttendance').textContent = (data.overallAttendance || 0) + '%';
        document.getElementById('activeLinks').textContent = data.activeLinks || 0;

    } catch (error) {
        console.error('Error loading dashboard stats:', error);
    }
}

window.onload = () => {
    loadGroups();       // Your existing groups load function
    loadDashboardStats(); // New stats data load function
};


async function onFaceCaptured(base64Image) {
    // 1. Identify student
    let response = await fetch('/identify-student', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({image: base64Image})
    });
    let data = await response.json();
    if (data.matched_students) {
        // Show dropdown/modal for user to select student
        showStudentSelection(data.matched_students);
    } else {
        alert(data.error || "Face not recognized");
    }
}

async function confirmAttendance(studentId) {
    let response = await fetch('/mark-attendance-confirm', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({student_id: studentId})
    });
    let data = await response.json();
    alert(data.message || data.error);
}


async function captureAndIdentify() {
    const base64Image = await captureFaceImage(); // Your camera capture function
    const response = await fetch('/identify-student', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({image: base64Image})
    });
    const data = await response.json();

    if (data.matched_students) {
        showStudentSelection(data.matched_students); // Display list & ask user to select
    } else {
        alert(data.error || 'No matching face found.');
    }
}

async function markAttendance(student_id) {
    const response = await fetch('/mark-attendance-confirm', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({student_id})
    });
    const result = await response.json();
    alert(result.message || result.error);
}
