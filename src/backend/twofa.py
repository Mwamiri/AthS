"""
Two-Factor Authentication (2FA) Module
Supports TOTP (Time-based One-Time Password) and backup codes
Optional 2FA for enhanced security
"""

import pyotp
import qrcode
from io import BytesIO
import base64
import secrets
from typing import Tuple, List, Dict, Optional
from datetime import datetime
from abc import ABC, abstractmethod


class TwoFAManager:
    """Manages two-factor authentication operations"""
    
    def __init__(self, issuer_name: str = "AthSys", totp_window: int = 1):
        """
        Initialize 2FA Manager
        
        Args:
            issuer_name: Name to display in authenticator app
            totp_window: Allow ±N time windows for TOTP (robustness)
        """
        self.issuer_name = issuer_name
        self.totp_window = totp_window
    
    def generate_secret(self) -> str:
        """
        Generate a new TOTP secret key
        
        Returns:
            Base32-encoded secret key
        """
        return pyotp.random_base32()
    
    def get_totp_provisioning_uri(
        self, 
        secret: str, 
        email: str
    ) -> str:
        """
        Generate provisioning URI for QR code
        
        Args:
            secret: TOTP secret key
            email: User email for display in authenticator app
        
        Returns:
            Provisioning URI for QR code generation
        """
        totp = pyotp.TOTP(secret)
        return totp.provisioning_uri(
            name=email,
            issuer_name=self.issuer_name
        )
    
    def generate_qr_code(self, provisioning_uri: str) -> str:
        """
        Generate QR code image as base64 data URI
        
        Args:
            provisioning_uri: Provisioning URI from get_totp_provisioning_uri()
        
        Returns:
            Base64-encoded PNG image as data URI
        """
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(provisioning_uri)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to base64
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        img_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        return f"data:image/png;base64,{img_base64}"
    
    def verify_totp(self, secret: str, token: str) -> bool:
        """
        Verify TOTP token
        
        Args:
            secret: TOTP secret key
            token: 6-digit code from authenticator app
        
        Returns:
            True if token is valid, False otherwise
        """
        try:
            totp = pyotp.TOTP(secret)
            # Allow ±totp_window time windows for robustness
            return totp.verify(token, valid_window=self.totp_window)
        except Exception:
            return False
    
    def generate_backup_codes(self, count: int = 10) -> List[str]:
        """
        Generate backup codes for 2FA recovery
        
        Args:
            count: Number of backup codes to generate
        
        Returns:
            List of backup codes
        """
        return [
            f"{secrets.token_hex(4).upper()}-{secrets.token_hex(2).upper()}"
            for _ in range(count)
        ]
    
    def hash_backup_code(self, code: str) -> str:
        """
        Hash a backup code for storage
        
        Args:
            code: Backup code
        
        Returns:
            Hashed backup code
        """
        import hashlib
        return hashlib.sha256(code.encode()).hexdigest()
    
    def verify_backup_code(self, code: str, hashed_code: str) -> bool:
        """
        Verify a backup code against stored hash
        
        Args:
            code: Backup code to verify
            hashed_code: Stored hashed backup code
        
        Returns:
            True if backup code is valid
        """
        import hashlib
        return hashlib.sha256(code.encode()).hexdigest() == hashed_code


class TwoFAValidator:
    """Validates 2FA configurations and tokens"""
    
    @staticmethod
    def validate_token_format(token: str) -> bool:
        """
        Validate TOTP token format (6 digits)
        
        Args:
            token: Token to validate
        
        Returns:
            True if format is valid
        """
        return (
            isinstance(token, str) and 
            token.isdigit() and 
            len(token) == 6
        )
    
    @staticmethod
    def validate_backup_code_format(code: str) -> bool:
        """
        Validate backup code format
        
        Args:
            code: Backup code to validate
        
        Returns:
            True if format is valid
        """
        # Format: XXXXXXXX-XXXX (8 hex chars, dash, 4 hex chars)
        import re
        pattern = r'^[A-F0-9]{8}-[A-F0-9]{4}$'
        return bool(re.match(pattern, code.upper()))
    
    @staticmethod
    def validate_secret_key(secret: str) -> bool:
        """
        Validate TOTP secret key format
        
        Args:
            secret: Secret key to validate
        
        Returns:
            True if valid base32 secret
        """
        try:
            # Try to use the secret to ensure it's valid
            pyotp.TOTP(secret)
            return True
        except Exception:
            return False


class TwoFAStatus:
    """Helper class for 2FA status information"""
    
    @staticmethod
    def format_response(
        enabled: bool,
        secret: Optional[str] = None,
        qr_code: Optional[str] = None,
        backup_codes: Optional[List[str]] = None,
        verified: bool = False
    ) -> Dict:
        """
        Format 2FA status response
        
        Args:
            enabled: Whether 2FA is enabled
            secret: TOTP secret (only return during setup)
            qr_code: QR code data URI
            backup_codes: Backup codes (only return during setup)
            verified: Whether 2FA has been verified
        
        Returns:
            Formatted response dictionary
        """
        response = {
            'twofa_enabled': enabled,
            'verified': verified
        }
        
        if secret:
            response['secret'] = secret
        
        if qr_code:
            response['qr_code'] = qr_code
        
        if backup_codes:
            response['backup_codes'] = backup_codes
        
        return response


# 2FA Setup Flow Helper
class TwoFASetupFlow:
    """Helper for managing 2FA setup flow"""
    
    @staticmethod
    def initiate_setup(
        email: str,
        issuer_name: str = "AthSys"
    ) -> Dict:
        """
        Initiate 2FA setup for a user
        
        Args:
            email: User email
            issuer_name: Name for authenticator app
        
        Returns:
            Dictionary with secret, QR code, and backup codes
        """
        manager = TwoFAManager(issuer_name=issuer_name)
        
        # Generate secret and backup codes
        secret = manager.generate_secret()
        backup_codes = manager.generate_backup_codes()
        
        # Generate QR code
        uri = manager.get_totp_provisioning_uri(secret, email)
        qr_code = manager.generate_qr_code(uri)
        
        return {
            'secret': secret,
            'qr_code': qr_code,
            'backup_codes': backup_codes,
            'provisioning_uri': uri
        }
    
    @staticmethod
    def verify_setup(
        secret: str,
        token: str,
        issuer_name: str = "AthSys"
    ) -> Tuple[bool, str]:
        """
        Verify 2FA setup with TOTP token
        
        Args:
            secret: TOTP secret from setup initiation
            token: 6-digit token from authenticator app
            issuer_name: Name for authenticator app
        
        Returns:
            Tuple of (is_valid, message)
        """
        # Validate token format
        if not TwoFAValidator.validate_token_format(token):
            return False, "Invalid token format. Use 6-digit code."
        
        # Verify token
        manager = TwoFAManager(issuer_name=issuer_name)
        if not manager.verify_totp(secret, token):
            return False, "Invalid token. Please check your authenticator app."
        
        return True, "2FA successfully enabled"


# Example usage and documentation
TWOFA_EXAMPLES = """
# 2FA Integration Examples

## 1. Initiate 2FA Setup (User starts setup)
manager = TwoFAManager(issuer_name="AthSys")
secret = manager.generate_secret()
uri = manager.get_totp_provisioning_uri(secret, user.email)
qr_code = manager.generate_qr_code(uri)
backup_codes = manager.generate_backup_codes()

Response to frontend:
{
    'secret': 'JBSWY3DPEBLW64TMMQ======',
    'qr_code': 'data:image/png;base64,...',
    'backup_codes': ['12345678-ABCD', ...],
    'provisioning_uri': 'otpauth://totp/...'
}

## 2. Verify Setup (User confirms with TOTP token)
is_valid, message = TwoFASetupFlow.verify_setup(secret, token)
if is_valid:
    # Save secret to user database
    user.twofa_secret = secret
    user.twofa_enabled = True
    user.backup_codes = [manager.hash_backup_code(code) for code in backup_codes]
    db.session.commit()

## 3. Daily Login with 2FA
def login_with_twofa(user_id, token):
    user = User.query.get(user_id)
    if user.twofa_enabled:
        manager = TwoFAManager()
        if manager.verify_totp(user.twofa_secret, token):
            # Grant access
            return True
        return False

## 4. Backup Code Login
def login_with_backup_code(user_id, code):
    user = User.query.get(user_id)
    manager = TwoFAManager()
    for backup_hash in user.backup_codes:
        if manager.verify_backup_code(code, backup_hash):
            # Mark code as used, remove from list
            user.backup_codes.remove(backup_hash)
            db.session.commit()
            return True
    return False

## 5. Disable 2FA
def disable_twofa(user_id):
    user = User.query.get(user_id)
    user.twofa_enabled = False
    user.twofa_secret = None
    user.backup_codes = []
    db.session.commit()
"""

if __name__ == '__main__':
    # Quick test
    manager = TwoFAManager()
    secret = manager.generate_secret()
    print(f"Secret: {secret}")
    print(f"Is valid secret: {TwoFAValidator.validate_secret_key(secret)}")
    
    backup_codes = manager.generate_backup_codes()
    print(f"Backup codes: {backup_codes}")
