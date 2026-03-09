"""Email notification service using aiosmtplib."""
from __future__ import annotations
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.config import settings

logger = logging.getLogger(__name__)


async def send_email(to_email: str, subject: str, html_body: str) -> bool:
    """Send an email via SMTP. Returns True on success."""
    if not all([settings.SMTP_HOST, settings.SMTP_USER, settings.SMTP_PASS]):
        logger.debug("SMTP not configured, skipping email")
        return False
    try:
        import aiosmtplib
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = getattr(settings, "FROM_EMAIL", settings.SMTP_USER)
        msg["To"] = to_email
        msg.attach(MIMEText(html_body, "html"))

        await aiosmtplib.send(
            msg,
            hostname=settings.SMTP_HOST,
            port=settings.SMTP_PORT,
            username=settings.SMTP_USER,
            password=settings.SMTP_PASS,
            start_tls=True,
        )
        logger.info(f"Email sent to {to_email}: {subject}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {e}")
        return False


async def send_workflow_notification(
    to_email: str,
    workflow_name: str,
    status: str,
    run_id: str,
    tokens: int,
    cost: float,
) -> None:
    """Send workflow completion notification email."""
    status_emoji = "✅" if status == "completed" else "❌"
    status_color = "#22c55e" if status == "completed" else "#ef4444"

    html = f"""
<!DOCTYPE html>
<html>
<body style="font-family: Arial, sans-serif; background: #0f172a; color: #e2e8f0; padding: 24px;">
  <div style="max-width: 560px; margin: 0 auto; background: #1e293b; border-radius: 12px; padding: 32px;">
    <h2 style="color: #f8fafc; margin-top: 0;">
      {status_emoji} Workflow {status.capitalize()}
    </h2>
    <p style="color: #94a3b8;">Your workflow <strong style="color: #f8fafc;">{workflow_name}</strong> has finished running.</p>
    <table style="width: 100%; border-collapse: collapse; margin: 24px 0;">
      <tr>
        <td style="padding: 8px 0; color: #94a3b8;">Status</td>
        <td style="padding: 8px 0; color: {status_color}; font-weight: bold;">{status.capitalize()}</td>
      </tr>
      <tr>
        <td style="padding: 8px 0; color: #94a3b8;">Tokens Used</td>
        <td style="padding: 8px 0; color: #f8fafc;">{tokens:,}</td>
      </tr>
      <tr>
        <td style="padding: 8px 0; color: #94a3b8;">Cost</td>
        <td style="padding: 8px 0; color: #f8fafc;">${cost:.4f}</td>
      </tr>
    </table>
    <p style="color: #64748b; font-size: 12px; margin-bottom: 0;">
      AgentFlow &mdash; AI Agent Orchestration Platform
    </p>
  </div>
</body>
</html>
"""
    subject = f"{status_emoji} AgentFlow: '{workflow_name}' {status}"
    await send_email(to_email, subject, html)
