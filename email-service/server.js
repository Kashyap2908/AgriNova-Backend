const express = require('express');
const nodemailer = require('nodemailer');
const cors = require('cors');
const path = require('path');
const dotenv = require('dotenv');

// Load environment variables from backend .env file
dotenv.config({ path: path.join(__dirname, '../agrinova/.env') });

const app = express();
app.use(cors());
app.use(express.json());

const PORT = process.env.PORT || 5001;

// Create Nodemailer Transporter reading credentials strictly from process environment
const getTransporter = () => {
  const host = process.env.MAIL_HOST;
  const port = parseInt(process.env.MAIL_PORT || '587', 10);
  const user = process.env.MAIL_USER;
  const pass = process.env.MAIL_PASSWORD;

  return nodemailer.createTransport({
    host: host,
    port: port,
    secure: port === 465, // true for 465, false for other ports
    auth: (user && pass) ? { user, pass } : undefined,
    tls: {
      rejectUnauthorized: false
    }
  });
};

app.post('/send-otp', async (req, res) => {
  try {
    const { to, email, otp } = req.body;
    const recipientEmail = to || email;

    if (!recipientEmail || !otp) {
      return res.status(400).json({
        success: false,
        message: 'Recipient email and OTP code are required.'
      });
    }

    const mailFrom = process.env.MAIL_FROM || 'AgriNova <noreply@agrinova.com>';

    const htmlContent = `
      <div style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; max-width: 550px; margin: 0 auto; padding: 30px; background-color: #0f172a; border-radius: 16px; color: #f8fafc; border: 1px solid #334155;">
        <div style="text-align: center; margin-bottom: 25px;">
          <h1 style="color: #10b981; font-size: 28px; margin: 0; font-weight: 800; letter-spacing: -0.5px;">AgriNova</h1>
          <p style="color: #94a3b8; font-size: 14px; margin-top: 4px;">Smart Agriculture Management</p>
        </div>
        <div style="background-color: #1e293b; padding: 25px; border-radius: 12px; border: 1px solid #334155; text-align: center;">
          <h2 style="color: #f1f5f9; font-size: 20px; margin-top: 0;">Password Reset Request</h2>
          <p style="color: #cbd5e1; font-size: 14px; line-height: 1.6;">
            We received a request to reset your password. Use the Verification Code below to complete your password reset:
          </p>
          <div style="margin: 25px 0;">
            <span style="font-family: monospace; font-size: 36px; font-weight: 800; letter-spacing: 8px; color: #10b981; background-color: #0f172a; padding: 12px 24px; border-radius: 8px; border: 1px border-style: dashed; border-color: #10b981;">${otp}</span>
          </div>
          <p style="color: #ef4444; font-size: 13px; font-weight: 600; margin-bottom: 0;">
            ⏰ This OTP will expire in 5 minutes.
          </p>
        </div>
        <p style="color: #64748b; font-size: 12px; text-align: center; margin-top: 25px; line-height: 1.5;">
          If you did not request a password reset, please ignore this email. Your account remains secure.<br/>
          &copy; ${new Date().getFullYear()} AgriNova AI Platform.
        </p>
      </div>
    `;

    const transporter = getTransporter();

    const mailOptions = {
      from: mailFrom,
      to: recipientEmail,
      subject: `AgriNova - Your Password Reset OTP is ${otp}`,
      html: htmlContent,
    };

    // Attempt to send email using configured Nodemailer transporter
    const info = await transporter.sendMail(mailOptions);
    console.log(`[Email Service] OTP email sent to ${recipientEmail}. MessageId: ${info.messageId}`);

    return res.status(200).json({
      success: true,
      message: 'OTP email sent successfully.',
      messageId: info.messageId
    });
  } catch (error) {
    console.error('[Email Service Error]:', error);

    // If SMTP fails or credentials are not yet configured in local environment, log error cleanly
    return res.status(500).json({
      success: false,
      message: 'Failed to send OTP email via SMTP provider.',
      error: error.message
    });
  }
});

app.get('/health', (req, res) => {
  res.json({ status: 'ok', service: 'AgriNova Node Mailer Microservice' });
});

app.listen(PORT, () => {
  console.log(`[AgriNova Mailer Microservice] Running on port ${PORT}`);
});
