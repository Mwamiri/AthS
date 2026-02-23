# Quick Start: App Requests & Form Marking Features

## What Was Added

### Frontend (admin-pro-complete.html)
✅ New menu items: "App Requests" and "Form Marking"  
✅ Two new pages with real-time filtering and search  
✅ Approve/Reject action buttons for each item  
✅ Status badges (pending/approved/rejected)  
✅ Loading spinners and error handling  
✅ Demo data with API integration  

### Backend (app.py)
✅ 7 new REST endpoints for app requests and form submissions  
✅ Demo data for testing  
✅ Support for approve/reject workflows with notes/reasons  

---

## Main Pages

### App Build Requests (`/admin/app-requests`)
**What it does:**
- View pending app build requests from users
- Approve requests with timestamp tracking
- Reject requests with reason

**Columns:**
- Title (app name)
- Requested By (user email)
- Priority (high/medium/low) - color coded
- Status (pending/approved/rejected) - color coded
- Created (date)
- Actions (Approve/Reject buttons)

**Filters:**
- Search box (searches title, requester, description)
- Status dropdown (All/Pending/Approved/Rejected)

### Form Submissions (`/admin/form-marking`)
**What it does:**
- View submitted forms awaiting approval
- Mark forms as approved with verification notes
- Mark forms as rejected with explanation

**Columns:**
- Form Name (name of form submitted)
- Submitted By (user email)
- Submitted Date (when submitted)
- Status (pending/approved/rejected) - color coded
- Notes (approval/rejection notes)
- Actions (Approve/Reject buttons)

**Filters:**
- Search box (searches form name, submitter)
- Status dropdown (All/Pending/Approved/Rejected)

---

## How to Use

### Approving an App Request
1. Login to dashboard
2. Click "App Requests" in sidebar
3. Find pending request in table (status = yellow "pending")
4. Click "Approve" button
5. Enter approval notes when prompted
6. Status changes to "approved" (green badge)

### Rejecting an App Request
1. Login to dashboard
2. Click "App Requests" in sidebar
3. Find pending request (status = yellow "pending")
4. Click "Reject" button
5. Enter rejection reason when prompted
6. Status changes to "rejected" (red badge)

### Approving a Form Submission
1. Login to dashboard
2. Click "Form Marking" in sidebar
3. Find pending form (status = yellow "pending")
4. Click "Approve" button
5. Enter approval/verification notes
6. Status changes to "approved" and notes saved

### Rejecting a Form Submission
1. Login to dashboard
2. Click "Form Marking" in sidebar
3. Find pending form (status = yellow "pending")
4. Click "Reject" button
5. Enter rejection explanation
6. Status changes to "rejected" and notes saved

### Filtering Data
- **Search:** Type in search box to find by title/name/submitter
- **Status Filter:** Use dropdown to show only Pending/Approved/Rejected items
- Both filters work together (AND logic)

---

## API Endpoints

### App Requests

```
GET  /api/admin/app-requests
     → Returns list of all app requests

POST /api/admin/app-requests
     Body: { title, requested_by, description, priority }
     → Creates new app request

PUT  /api/admin/app-requests/{id}/approve
     Body: { approved_by }
     → Approves request and sets timestamp

PUT  /api/admin/app-requests/{id}/reject
     Body: { rejected_reason }
     → Rejects request with reason
```

### Form Submissions

```
GET  /api/admin/form-submissions
     → Returns list of all form submissions

POST /api/admin/form-submissions
     Body: { form_name, submitted_by }
     → Creates new form submission record

PUT  /api/admin/form-submissions/{id}/approve
     Body: { notes }
     → Approves submission with review notes

PUT  /api/admin/form-submissions/{id}/reject
     Body: { notes }
     → Rejects submission with explanation
```

---

## Demo Data

### Sample App Requests
1. **School Events Tracker** (pending)
   - Requested by: coach@school.edu
   - Priority: High (red)
   - Description: Track school-wide athletic events

2. **Athlete Health Dashboard** (approved)
   - Requested by: admin@athsys.com
   - Priority: Medium (yellow)
   - Description: Monitor athlete health metrics
   - Approved by: admin@athsys.com
   - Approved on: 2024-01-12

### Sample Form Submissions
1. **Athlete Registration** (pending)
   - Submitted by: athlete@example.com
   - Date: 2024-01-20
   - Status: Pending (yellow)

2. **Event Participation** (approved)
   - Submitted by: coach@school.edu
   - Date: 2024-01-18
   - Status: Approved (green)
   - Notes: Approved - all documents verified

---

## Features

### Data Filtering
- Real-time search across multiple fields
- Status dropdown filtering
- Combined filter logic (search AND status)
- Demo data auto-loads if API unavailable

### Status Management
- Pending (yellow) - awaiting action
- Approved (green) - accepted and processed
- Rejected (red) - declined with reason

### Priority Levels (App Requests only)
- High (red) - urgent
- Medium (yellow) - normal
- Low (blue) - low priority

### User Management
- User email tracked for requests
- Approval/rejection tracking with timestamps
- Notes/reason documentation

### UI Features
- Loading spinners during data fetch
- Empty state messages
- Responsive table layout
- Dark mode support
- Success notifications on actions
- Error handling with fallback to demo data

---

## Testing Checklist

- [ ] Menu items "App Requests" and "Form Marking" visible in sidebar
- [ ] App Requests page loads with table and demo data
- [ ] Form Marking page loads with table and demo data
- [ ] Search filters work on both pages
- [ ] Status dropdown filters work correctly
- [ ] Approve button triggers action and updates status
- [ ] Reject button prompts for reason/notes
- [ ] Status badges have correct colors
- [ ] Loading spinner shows during API calls
- [ ] Actions disabled for non-pending items
- [ ] Success notifications appear after actions
- [ ] Dark mode styling applied correctly
- [ ] Page is responsive on mobile devices

---

## Technical Stack

**Frontend:**
- Vue 3 (reactive UI framework)
- Tailwind CSS (styling)
- Chart.js (future analytics)
- Bearer token auth

**Backend:**
- Flask (Python web framework)
- SQLAlchemy (ORM, easily switchable to database)
- REST API with standard JSON responses
- Demo data (easily replaceable with DB)

---

## What's Next (Optional Enhancements)

- [ ] Persist data to database instead of demo data
- [ ] Add pagination for large datasets
- [ ] Batch approve/reject operations
- [ ] Export to CSV reports
- [ ] Advanced date range filtering
- [ ] Email notifications
- [ ] Activity timeline
- [ ] File attachments for submissions
- [ ] Custom form builder
- [ ] Approval workflows with multiple levels

---

## Troubleshooting

**Q: Pages not loading?**
- Clear browser cache (Ctrl+Shift+Delete)
- Check browser console for errors (F12)
- Verify API server is running
- Check Bearer token in localStorage

**Q: Filters not working?**
- Type in search box and click outside to trigger
- Remember status must match (case-insensitive)
- Try clearing filter and reapplying

**Q: Can't approve/reject?**
- Only pending items have action buttons
- Check your authentication token
- Verify API endpoint is accessible

**Q: Demo data not showing?**
- This means API failed to load - check console
- Demo data automatically shown on error
- Verify `/api/admin/app-requests` and `/api/admin/form-submissions` endpoints exist

---

## File Structure

```
src/
├── frontend/
│   └── admin-pro-complete.html    ← Main dashboard with new pages
└── backend/
    └── app.py                      ← Flask app with new endpoints
```

## Configuration

To change demo data or API endpoints, edit these in admin-pro-complete.html:

```javascript
// Line ~1800: API endpoint
const API_BASE = window.AthSysConfig?.apiBase || '/api';

// Line ~1820: Demo app requests
const demoAppRequests = [ ... ]

// Line ~1840: Demo form submissions
const demoFormSubmissions = [ ... ]
```

---

## Support

For issues or questions:
1. Check browser console (F12) for errors
2. Verify API endpoints are accessible
3. Check authentication token in localStorage
4. Review demo data in source code for expected format
