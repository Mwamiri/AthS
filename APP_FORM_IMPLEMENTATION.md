# App Build Requests & Form Marking Implementation

## Overview
Added complete frontend and backend implementation for two critical v3 features:
1. **App Build Requests** - Request custom app building with approval workflow
2. **Form Marking** - Mark and approve form submissions with notes

## Frontend Changes (admin-pro-complete.html)

### New Menu Items
- **App Requests** (`id: 'app-requests'`, icon: `fa-code`)
- **Form Marking** (`id: 'form-marking'`, icon: `fa-check-square`)

### New Data Refs
```javascript
const appRequests = ref([]);
const formSubmissions = ref([]);
```

### New Loading & Error States
```javascript
isLoading: { appRequests: false, formSubmissions: false }
errors: { appRequests: '', formSubmissions: '' }
```

### New Filter States
```javascript
filters: {
    appRequestQuery: '',
    appRequestStatus: 'All Status',
    formSubmissionQuery: '',
    formSubmissionStatus: 'All Status'
}
```

### New Computed Properties
- `filteredAppRequests` - Filters by title/requested_by/description and status
- `filteredFormSubmissions` - Filters by form_name/submitted_by and status

### New Data Loader Functions
- `loadAppRequests()` - Fetches from `/api/admin/app-requests`
- `loadFormSubmissions()` - Fetches from `/api/admin/form-submissions`

### New Action Functions
```javascript
approveAppRequest(requestId)        // PUT /api/admin/app-requests/<id>/approve
rejectAppRequest(requestId)         // PUT /api/admin/app-requests/<id>/reject
approveFormSubmission(submissionId) // PUT /api/admin/form-submissions/<id>/approve
rejectFormSubmission(submissionId)  // PUT /api/admin/form-submissions/<id>/reject
```

### New UI Pages
1. **App Requests Page** (v-if="currentPage === 'app-requests'")
   - Table with columns: Title, Requested By, Priority, Status, Created, Actions
   - Filters: Search (by title/requester/description), Status dropdown
   - Status badges: pending (yellow), approved (green), rejected (red)
   - Approve/Reject buttons visible only for pending requests
   - Priority badges: high (red), medium (yellow), low (blue)

2. **Form Marking Page** (v-if="currentPage === 'form-marking'")
   - Table with columns: Form Name, Submitted By, Submitted Date, Status, Notes, Actions
   - Filters: Search (by form name/submitter), Status dropdown
   - Status badges: pending (yellow), approved (green), rejected (red)
   - Approve/Reject buttons visible only for pending submissions
   - Notes column shows submission review notes

### Data Loading Integration
Both loaders integrated into `initializeApp()` initialization:
```javascript
await Promise.all([
    // ... existing loaders
    loadAppRequests(),
    loadFormSubmissions(),
    // ... other loaders
]);
```

### Return Object Exports
All new functions/data exported in component return:
- `appRequests`, `formSubmissions`
- `filteredAppRequests`, `filteredFormSubmissions`
- `loadAppRequests`, `loadFormSubmissions`
- `approveAppRequest`, `rejectAppRequest`
- `approveFormSubmission`, `rejectFormSubmission`

## Backend Changes (src/backend/app.py)

### Demo Data
```python
DEMO_APP_REQUESTS = [
    {
        'id': 1,
        'title': 'School Events Tracker',
        'requested_by': 'coach@school.edu',
        'description': 'Track school-wide athletic events',
        'priority': 'high',
        'status': 'pending',
        'created_at': '2024-01-15'
    },
    {
        'id': 2,
        'title': 'Athlete Health Dashboard',
        'requested_by': 'admin@athsys.com',
        'description': 'Monitor athlete health metrics',
        'priority': 'medium',
        'status': 'approved',
        'created_at': '2024-01-10',
        'approved_by': 'admin@athsys.com',
        'approved_at': '2024-01-12'
    }
]

DEMO_FORM_SUBMISSIONS = [
    {
        'id': 1,
        'form_name': 'Athlete Registration',
        'submitted_by': 'athlete@example.com',
        'submitted_at': '2024-01-20',
        'status': 'pending',
        'notes': ''
    },
    {
        'id': 2,
        'form_name': 'Event Participation',
        'submitted_by': 'coach@school.edu',
        'submitted_at': '2024-01-18',
        'status': 'approved',
        'notes': 'Approved - all documents verified'
    }
]
```

### New API Endpoints

#### App Requests
- **GET** `/api/admin/app-requests` - List all requests
  - Response: `{ requests: [], count: N }`
  
- **POST** `/api/admin/app-requests` - Create new request
  - Body: `{ title, requested_by, description, priority }`
  - Response: `{ message, request: {} }`
  
- **PUT** `/api/admin/app-requests/<id>/approve` - Approve request
  - Body: `{ approved_by }`
  - Response: `{ message: '✅ App request approved', request: {} }`
  
- **PUT** `/api/admin/app-requests/<id>/reject` - Reject request
  - Body: `{ rejected_reason }`
  - Response: `{ message: '✅ App request rejected', request: {} }`

#### Form Submissions
- **GET** `/api/admin/form-submissions` - List all submissions
  - Response: `{ submissions: [], count: N }`
  
- **POST** `/api/admin/form-submissions` - Create new submission
  - Body: `{ form_name, submitted_by }`
  - Response: `{ message, submission: {} }`
  
- **PUT** `/api/admin/form-submissions/<id>/approve` - Approve submission
  - Body: `{ notes }`
  - Response: `{ message: '✅ Form submission approved', submission: {} }`
  
- **PUT** `/api/admin/form-submissions/<id>/reject` - Reject submission
  - Body: `{ notes }`
  - Response: `{ message: '✅ Form submission rejected', submission: {} }`

## User Workflow

### App Requests
1. Click "App Requests" in sidebar
2. View pending requests in table
3. Filter by title/requester/description using search
4. Filter by status (pending/approved/rejected)
5. Click "Approve" button for pending requests
6. Enter approval notes (prompt)
7. Status updates to "approved" with timestamp
8. Click "Reject" button to deny with reason

### Form Marking
1. Click "Form Marking" in sidebar
2. View pending form submissions in table
3. Filter by form name/submitter using search
4. Filter by status (pending/approved/rejected)
5. Click "Approve" to mark form as approved
6. Enter approval/verification notes (prompt)
7. Status updates to "approved" with notes
8. Click "Reject" to decline with notes

## Status Indicators
- **Pending** (Yellow badge) - Awaiting review
- **Approved** (Green badge) - Approved and completed
- **Rejected** (Red badge) - Rejected with reason/notes

## Features
✅ Real-time filtering and search
✅ Status badges with color coding
✅ Inline approve/reject actions
✅ Notes/reason tracking
✅ Loading states and error handling
✅ Demo data with fallback when API unavailable
✅ Bearer token authentication
✅ Success notifications after actions
✅ Responsive table design (scrollable on mobile)
✅ Dark mode support

## Testing

### Manual Testing Steps
1. Login with valid credentials
2. Navigate to App Requests page - verify data loads
3. Search for "tracker" - should filter to School Events Tracker
4. Select "Pending" status filter - should show only pending requests
5. Click Approve button - should prompt for approval notes
6. Confirm approval - status should change to "approved"
7. Repeat for Form Marking page
8. Verify buttons disappear when status is no longer pending

### API Testing
```bash
# Get all app requests
curl -H "Authorization: Bearer <token>" http://localhost/api/admin/app-requests

# Approve a request
curl -X PUT -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"approved_by":"admin@athsys.com"}' \
  http://localhost/api/admin/app-requests/1/approve

# Get all form submissions
curl -H "Authorization: Bearer <token>" http://localhost/api/admin/form-submissions

# Approve a submission
curl -X PUT -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"notes":"Verified documents"}' \
  http://localhost/api/admin/form-submissions/1/approve
```

## What's Working
✅ Menu items visible in sidebar
✅ Pages load with demo data
✅ Filters work correctly
✅ Action buttons trigger API calls
✅ Status updates after approval/rejection
✅ Success notifications display
✅ Loading spinners show during fetch
✅ Error handling with fallback to demo data
✅ Dark mode styling applied
✅ Responsive design on all screen sizes

## Future Enhancements
- [ ] Database persistence (replace demo data with DB storage)
- [ ] Pagination for large datasets
- [ ] Batch approve/reject operations
- [ ] Export reports as CSV
- [ ] Advanced filters (date range, priority)
- [ ] Activity timeline for each request/submission
- [ ] Email notifications on approval/rejection
- [ ] Custom request form builder
- [ ] Form response review modal with attachments
