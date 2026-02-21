"""
Email Notifications Module
Send emails for user registration, password reset, alerts, and notifications
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from abc import ABC, abstractmethod
import logging
import os
from datetime import datetime


@dataclass
class EmailTemplate:
    """Email template definition"""
    name: str
    subject: str
    html_body: str
    text_body: str
    required_variables: List[str]


class EmailConfig:
    """Email configuration"""
    
    def __init__(self):
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.smtp_username = os.getenv('SMTP_USERNAME', '')
        self.smtp_password = os.getenv('SMTP_PASSWORD', '')
        self.from_email = os.getenv('FROM_EMAIL', 'noreply@athsys.com')
        self.from_name = os.getenv('FROM_NAME', 'AthSys')
        self.enabled = os.getenv('EMAIL_ENABLED', 'False') == 'True'
        self.logger = logging.getLogger('athsys.email')


class EmailService:
    """Email service for sending notifications"""
    
    def __init__(self, config: Optional[EmailConfig] = None):
        self.config = config or EmailConfig()
        self.templates: Dict[str, EmailTemplate] = {}
        self._register_templates()
    
    def _register_templates(self):
        """Register email templates"""
        
        # Welcome email
        self.add_template('welcome', EmailTemplate(
            name='welcome',
            subject='Welcome to AthSys',
            html_body='''
            <html>
                <body style="font-family: Arial, sans-serif;">
                    <h2>Welcome to AthSys, {user_name}!</h2>
                    <p>Your account has been created successfully.</p>
                    <p>
                        <a href="{activation_link}" style="background-color: #06d6a0; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
                            Activate Your Account
                        </a>
                    </p>
                    <p>If you didn't create this account, please ignore this email.</p>
                </body>
            </html>
            ''',
            text_body='Welcome to AthSys, {user_name}!\nYour account has been created.\nActivation link: {activation_link}',
            required_variables=['user_name', 'activation_link']
        ))
        
        # Password reset email
        self.add_template('password_reset', EmailTemplate(
            name='password_reset',
            subject='Reset Your AthSys Password',
            html_body='''
            <html>
                <body style="font-family: Arial, sans-serif;">
                    <h2>Password Reset Request</h2>
                    <p>We received a request to reset your password.</p>
                    <p>
                        <a href="{reset_link}" style="background-color: #06d6a0; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
                            Reset Password
                        </a>
                    </p>
                    <p style="color: #666; font-size: 12px;">This link expires in 24 hours.</p>
                    <p>If you didn't request this, please ignore this email.</p>
                </body>
            </html>
            ''',
            text_body='Reset your password here: {reset_link}\nThis link expires in 24 hours.',
            required_variables=['reset_link']
        ))
        
        # 2FA setup confirmation
        self.add_template('twofa_enabled', EmailTemplate(
            name='twofa_enabled',
            subject='Two-Factor Authentication Enabled',
            html_body='''
            <html>
                <body style="font-family: Arial, sans-serif;">
                    <h2>Two-Factor Authentication Enabled</h2>
                    <p>Two-factor authentication (2FA) has been enabled on your account.</p>
                    <p>From now on, you'll need to provide a verification code from your authenticator app when logging in.</p>
                    <p style="color: #f7931e;">If this wasn't you, change your password immediately.</p>
                </body>
            </html>
            ''',
            text_body='Two-factor authentication has been enabled on your account.',
            required_variables=[]
        ))
        
        # Alert notification
        self.add_template('alert', EmailTemplate(
            name='alert',
            subject='AthSys Alert: {alert_type}',
            html_body='''
            <html>
                <body style="font-family: Arial, sans-serif;">
                    <h2>Alert: {alert_type}</h2>
                    <p>{alert_message}</p>
                    <p style="color: #666; font-size: 12px;">Time: {timestamp}</p>
                </body>
            </html>
            ''',
            text_body='Alert: {alert_type}\n{alert_message}\nTime: {timestamp}',
            required_variables=['alert_type', 'alert_message', 'timestamp']
        ))
    
    def add_template(self, name: str, template: EmailTemplate):
        """Register an email template"""
        self.templates[name] = template
    
    def send_email(
        self,
        to: str,
        subject: str,
        html_body: str = '',
        text_body: str = '',
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None
    ) -> bool:
        """Send email directly"""
        
        if not self.config.enabled:
            self.config.logger.warning("Email disabled - not sending")
            return False
        
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{self.config.from_name} <{self.config.from_email}>"
            msg['To'] = to
            
            if cc:
                msg['Cc'] = ', '.join(cc)
            if bcc:
                msg['Bcc'] = ', '.join(bcc)
            
            # Attach text and HTML versions
            if text_body:
                msg.attach(MIMEText(text_body, 'plain'))
            if html_body:
                msg.attach(MIMEText(html_body, 'html'))
            
            # Send email
            with smtplib.SMTP(self.config.smtp_server, self.config.smtp_port) as server:
                server.starttls()
                server.login(self.config.smtp_username, self.config.smtp_password)
                server.sendmail(
                    self.config.from_email,
                    [to] + (cc or []) + (bcc or []),
                    msg.as_string()
                )
            
            self.config.logger.info(f"Email sent to {to}")
            return True
        
        except Exception as e:
            self.config.logger.error(f"Failed to send email: {e}")
            return False
    
    def send_from_template(
        self,
        to: str,
        template_name: str,
        variables: Dict[str, Any],
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None
    ) -> bool:
        """Send email from registered template"""
        
        if template_name not in self.templates:
            self.config.logger.error(f"Template not found: {template_name}")
            return False
        
        template = self.templates[template_name]
        
        # Validate required variables
        for var in template.required_variables:
            if var not in variables:
                self.config.logger.error(f"Missing required variable: {var}")
                return False
        
        # Format template
        subject = template.subject.format(**variables)
        html_body = template.html_body.format(**variables)
        text_body = template.text_body.format(**variables)
        
        return self.send_email(to, subject, html_body, text_body, cc, bcc)


# Email notification types
class NotificationType:
    USER_WELCOME = 'welcome'
    PASSWORD_RESET = 'password_reset'
    TWOFA_ENABLED = 'twofa_enabled'
    TWOFA_DISABLED = 'twofa_disabled'
    LOGIN_FROM_NEW_DEVICE = 'login_new_device'
    FAILED_LOGIN_ATTEMPTS = 'failed_login_attempts'
    PERMISSION_GRANTED = 'permission_granted'
    PERMISSION_REVOKED = 'permission_revoked'
    SYSTEM_ALERT = 'system_alert'
    RACE_RESULT = 'race_result'
    ATHLETE_INVITATION = 'athlete_invitation'


class NotificationPreferences:
    """User notification preferences"""
    
    PREFERENCES = {
        'email_welcome': True,
        'email_password_reset': True,
        'email_twofa_changes': True,
        'email_security_alerts': True,
        'email_failed_logins': True,
        'email_race_updates': False,
        'email_athlete_invitations': True,
        'email_weekly_digest': False,
    }


# Global email service instance
_email_service = None


def get_email_service() -> EmailService:
    """Get or create email service instance"""
    global _email_service
    if _email_service is None:
        _email_service = EmailService()
    return _email_service


# Helper function for sending notifications
def send_notification(
    to: str,
    notification_type: str,
    variables: Dict[str, Any],
    cc: Optional[List[str]] = None,
    bcc: Optional[List[str]] = None
) -> bool:
    """Send notification email"""
    
    service = get_email_service()
    
    # Map notification type to template
    template_map = {
        NotificationType.USER_WELCOME: 'welcome',
        NotificationType.PASSWORD_RESET: 'password_reset',
        NotificationType.TWOFA_ENABLED: 'twofa_enabled',
        NotificationType.SYSTEM_ALERT: 'alert',
    }
    
    template_name = template_map.get(notification_type)
    if not template_name:
        return False
    
    return service.send_from_template(to, template_name, variables, cc, bcc)
