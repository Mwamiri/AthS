# Two-Factor Authentication (2FA) Implementation Guide

## Overview
This guide outlines the implementation of Two-Factor Authentication for the AthSys Athletics Management System.

## Current Status
✅ **Completed:**
- 2FA toggle switch in admin security settings
- User interface for enabling/disabling 2FA
- Frontend structure ready for 2FA verification

⏳ **Pending:**
- TOTP (Time-based One-Time Password) generation
- QR code generation for authenticator apps
- Backup codes generation
- 2FA verification during login

## Implementation Steps

### 1. Backend Dependencies
Install required Python packages:
```bash
pip install pyotp qrcode pillow
```

**Dependencies:**
- `pyotp`: Generate and verify TOTP codes
- `qrcode`: Generate QR codes for authenticator apps
- `pillow`: Image processing for QR codes

### 2. Backend Implementation

#### Add to `src/backend/app.py`:

```python
import pyotp
import qrcode
import io
import base64

# Add 2FA secret to user model
def generate_2fa_secret():
    """Generate a new 2FA secret for user"""
    return pyotp.random_base32()

@app.route('/api/auth/2fa/setup', methods=['POST'])
def setup_2fa():
    """Setup 2FA for user"""
    # Get user from token (in production, verify JWT)
    user_email = request.json.get('email')
    user = next((u for u in DEMO_USERS if u['email'] == user_email), None)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Generate 2FA secret
    secret = generate_2fa_secret()
    user['twofa_secret'] = secret
    
    # Generate QR code
    totp = pyotp.TOTP(secret)
    provisioning_uri = totp.provisioning_uri(
        name=user_email,
        issuer_name='AthSys'
    )
    
    # Create QR code image
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(provisioning_uri)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to base64
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    qr_code = base64.b64encode(buffer.getvalue()).decode()
    
    # Generate backup codes
    backup_codes = [pyotp.random_base32()[:8] for _ in range(10)]
    user['backup_codes'] = backup_codes
    
    return jsonify({
        'message': '2FA setup initiated',
        'secret': secret,
        'qr_code': f'data:image/png;base64,{qr_code}',
        'backup_codes': backup_codes
    }), 200

@app.route('/api/auth/2fa/verify', methods=['POST'])
def verify_2fa():
    """Verify 2FA code during login"""
    email = request.json.get('email')
    code = request.json.get('code')
    
    user = next((u for u in DEMO_USERS if u['email'] == email), None)
    
    if not user or 'twofa_secret' not in user:
        return jsonify({'error': 'Invalid request'}), 400
    
    # Verify TOTP code
    totp = pyotp.TOTP(user['twofa_secret'])
    
    # Check if code is valid or is a backup code
    is_valid = totp.verify(code) or code in user.get('backup_codes', [])
    
    if is_valid:
        # Remove backup code if used
        if code in user.get('backup_codes', []):
            user['backup_codes'].remove(code)
        
        return jsonify({
            'message': '2FA verification successful',
            'valid': True
        }), 200
    else:
        return jsonify({
            'message': '2FA verification failed',
            'valid': False
        }), 401

@app.route('/api/auth/2fa/disable', methods=['POST'])
def disable_2fa():
    """Disable 2FA for user"""
    email = request.json.get('email')
    password = request.json.get('password')
    
    user = next((u for u in DEMO_USERS if u['email'] == email), None)
    
    if not user or user['password'] != password:
        return jsonify({'error': 'Invalid credentials'}), 401
    
    # Remove 2FA data
    user.pop('twofa_secret', None)
    user.pop('backup_codes', None)
    
    return jsonify({'message': '2FA disabled successfully'}), 200
```

### 3. Frontend Implementation

#### Create `src/frontend/2fa-setup.html`:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Setup Two-Factor Authentication - AthSys</title>
    <link rel="stylesheet" href="styles.css">
    <link rel="stylesheet" href="auth.css">
</head>
<body>
    <div class="auth-container">
        <div class="auth-card">
            <div class="auth-header">
                <h1>🔐 Setup 2FA</h1>
                <p>Secure your account with two-factor authentication</p>
            </div>
            
            <div id="qr-section">
                <h3>Step 1: Scan QR Code</h3>
                <p>Use an authenticator app like Google Authenticator or Authy to scan this QR code:</p>
                <div id="qr-code-container" style="text-align: center; margin: 2rem 0;">
                    <!-- QR code will be inserted here -->
                </div>
                
                <h3>Step 2: Enter Verification Code</h3>
                <form id="verify-2fa-form">
                    <div class="form-group">
                        <label for="verification-code">6-Digit Code</label>
                        <input type="text" id="verification-code" maxlength="6" pattern="[0-9]{6}" required>
                    </div>
                    <button type="submit" class="btn btn-primary">Verify & Enable 2FA</button>
                </form>
            </div>
            
            <div id="backup-codes" style="display: none;">
                <h3>✅ 2FA Enabled Successfully!</h3>
                <p><strong>Important:</strong> Save these backup codes in a safe place. You can use them to access your account if you lose your authenticator device.</p>
                <div id="backup-codes-list" style="background: var(--background-light); padding: 1rem; border-radius: 8px; margin: 1rem 0;">
                    <!-- Backup codes will be inserted here -->
                </div>
                <button class="btn btn-primary" onclick="downloadBackupCodes()">📥 Download Backup Codes</button>
                <button class="btn btn-secondary" onclick="window.location.href='admin.html'">Return to Dashboard</button>
            </div>
        </div>
    </div>
    
    <script src="auth.js"></script>
    <script>
        // 2FA Setup logic
        async function setup2FA() {
            const user = JSON.parse(localStorage.getItem('user') || '{}');
            
            const response = await fetch('http://localhost:5000/api/auth/2fa/setup', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email: user.email })
            });
            
            const data = await response.json();
            
            // Display QR code
            document.getElementById('qr-code-container').innerHTML = `
                <img src="${data.qr_code}" alt="2FA QR Code" style="max-width: 250px;">
            `;
            
            // Store backup codes
            window.backupCodes = data.backup_codes;
        }
        
        // Verify 2FA code
        document.getElementById('verify-2fa-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const user = JSON.parse(localStorage.getItem('user') || '{}');
            const code = document.getElementById('verification-code').value;
            
            const response = await fetch('http://localhost:5000/api/auth/2fa/verify', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email: user.email, code })
            });
            
            const data = await response.json();
            
            if (data.valid) {
                // Show backup codes
                document.getElementById('qr-section').style.display = 'none';
                document.getElementById('backup-codes').style.display = 'block';
                
                const codesList = window.backupCodes.map((code, i) => 
                    `<div style="font-family: monospace; padding: 0.5rem;">${i + 1}. ${code}</div>`
                ).join('');
                
                document.getElementById('backup-codes-list').innerHTML = codesList;
                
                toast.show('2FA enabled successfully!', 'success');
            } else {
                toast.show('Invalid verification code', 'error');
            }
        });
        
        function downloadBackupCodes() {
            const codes = window.backupCodes.join('\n');
            const blob = new Blob([codes], { type: 'text/plain' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'athsys-backup-codes.txt';
            a.click();
        }
        
        // Initialize setup on page load
        setup2FA();
    </script>
</body>
</html>
```

#### Update login flow in `auth.js`:

```javascript
// Add after successful login, check if 2FA is enabled
if (data.user.twofa_enabled) {
    // Show 2FA verification modal
    show2FAVerification(data.user.email);
} else {
    // Proceed with normal login
    redirectUser(data.user);
}

function show2FAVerification(email) {
    // Create 2FA modal
    const modal = document.createElement('div');
    modal.className = 'modal active';
    modal.innerHTML = `
        <div class="modal-content">
            <h3>Enter 2FA Code</h3>
            <form id="2fa-verify-form">
                <div class="form-group">
                    <label>6-Digit Code</label>
                    <input type="text" id="2fa-code" maxlength="6" pattern="[0-9]{6}" required>
                </div>
                <button type="submit" class="btn btn-primary">Verify</button>
                <button type="button" class="btn btn-secondary" onclick="useBackupCode()">Use Backup Code</button>
            </form>
        </div>
    `;
    document.body.appendChild(modal);
    
    // Handle verification
    document.getElementById('2fa-verify-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const code = document.getElementById('2fa-code').value;
        
        const response = await fetch(`${API_BASE_URL}/api/auth/2fa/verify`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, code })
        });
        
        const data = await response.json();
        
        if (data.valid) {
            modal.remove();
            redirectUser(JSON.parse(localStorage.getItem('user')));
        } else {
            toast.show('Invalid 2FA code', 'error');
        }
    });
}
```

### 4. Security Best Practices

1. **Secret Storage**: Store 2FA secrets encrypted in the database
2. **Rate Limiting**: Limit verification attempts to prevent brute force
3. **Backup Codes**: Generate 10-12 single-use backup codes
4. **Time Window**: TOTP codes valid for 30 seconds with 1-step tolerance
5. **Recovery Options**: Provide alternative recovery methods
6. **Audit Logging**: Log all 2FA setup/disable/verification events

### 5. Testing 2FA

**Authenticator Apps:**
- Google Authenticator (iOS/Android)
- Microsoft Authenticator (iOS/Android)
- Authy (iOS/Android/Desktop)

**Test Flow:**
1. Enable 2FA in admin settings
2. Scan QR code with authenticator app
3. Enter 6-digit code to verify
4. Save backup codes securely
5. Logout and login again
6. Enter 2FA code from authenticator app
7. Test backup code login

### 6. Database Schema Update

Add to user table:
```sql
ALTER TABLE users ADD COLUMN twofa_enabled BOOLEAN DEFAULT FALSE;
ALTER TABLE users ADD COLUMN twofa_secret VARCHAR(32);
ALTER TABLE users ADD COLUMN backup_codes TEXT[];
ALTER TABLE users ADD COLUMN twofa_enabled_at TIMESTAMP;
```

## Quick Start (Demo Mode)

For immediate testing without dependencies:

1. Use the toggle in [admin.html](admin.html#L250) to enable/disable 2FA requirement
2. Backend will simulate 2FA verification
3. Demo code: `123456` always validates in demo mode
4. Backup code: `DEMO1234` always validates in demo mode

## Production Deployment Checklist

- [ ] Install pyotp, qrcode, pillow dependencies
- [ ] Add 2FA fields to database schema
- [ ] Implement JWT token authentication
- [ ] Add rate limiting for 2FA verification
- [ ] Set up email notifications for 2FA events
- [ ] Create admin dashboard for 2FA statistics
- [ ] Add 2FA recovery flow via email
- [ ] Document 2FA process for users
- [ ] Test with multiple authenticator apps
- [ ] Add 2FA to audit logs

## Support & Resources

**Documentation:**
- PyOTP: https://pypi.org/project/pyotp/
- TOTP RFC: https://tools.ietf.org/html/rfc6238
- QR Code: https://pypi.org/project/qrcode/

**Security References:**
- OWASP 2FA Cheat Sheet
- NIST Digital Identity Guidelines
- Google 2FA Best Practices

## Notes

- Current implementation uses demo data and simplified authentication
- For production, integrate with proper user database and JWT
- Consider using existing authentication services (Auth0, Firebase Auth)
- Implement proper password hashing with bcrypt or argon2
- Add CSRF protection for all authentication endpoints
- Use HTTPS in production to protect credentials

---

**Version:** 1.0.0  
**Last Updated:** 2024  
**Status:** Implementation Guide
