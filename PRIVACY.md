# Privacy & Data Protection Policy

## Overview

The Exam Activity Monitoring System is designed with privacy as a core principle. This document outlines what data we collect, how we use it, and the safeguards in place to protect candidate privacy.

## What We Monitor

### ✅ Data We Collect

1. **Tab Switching Events**
   - When the exam tab loses focus (timestamp)
   - When the exam tab regains focus (timestamp)
   - Duration of time the tab was inactive (milliseconds)
   - Purpose: Detect potential cheating via external resources

2. **Copy/Paste Events**
   - When copy action occurs (timestamp)
   - When paste action occurs (timestamp)
   - Length of content copied/pasted (bytes only)
   - Purpose: Detect potential unauthorized content transfer

3. **Inactivity Events**
   - When keyboard becomes inactive for >30 seconds (timestamp)
   - When mouse becomes inactive for >30 seconds (timestamp)
   - Duration of inactivity (seconds)
   - Purpose: Detect candidate absence or unusual behavior

4. **Session Information**
   - Session ID (unique identifier for exam session)
   - Candidate ID (anonymized identifier)
   - Timestamps (client and server time)

### ❌ Data We DO NOT Collect

1. **No Clipboard Content**
   - We NEVER capture the actual text being copied or pasted
   - Only the occurrence and length (in bytes) are logged
   - Clipboard data remains private on the candidate's device

2. **No Keystroke Logging**
   - We do not record what keys are pressed
   - We only detect the presence/absence of keyboard activity
   - Exam answers and typing content are NOT captured by monitoring

3. **No Screen Recording**
   - We do not capture screenshots
   - We do not record screen video
   - Visual content on the screen is NOT monitored

4. **No Browser History**
   - We do not access or log browser history
   - We do not track websites visited outside the exam

5. **No Personal Information**
   - We do not collect names, emails, or contact information through monitoring
   - Candidate ID is an anonymized identifier
   - No PII (Personally Identifiable Information) is captured

6. **No Biometric Data**
   - No facial recognition (unless explicitly enabled as separate feature)
   - No fingerprint or voice data
   - No health or biometric information

## How We Use the Data

### Primary Use Cases

1. **Exam Integrity**
   - Detect suspicious behavior patterns
   - Flag potential cheating attempts
   - Generate integrity reports for exam administrators

2. **Risk Scoring**
   - Calculate risk scores based on behavior patterns
   - Identify candidates requiring manual review
   - Provide evidence for academic integrity investigations

3. **Audit Trail**
   - Maintain records for dispute resolution
   - Provide evidence if exam integrity is questioned
   - Support fair evaluation processes

### Data Access

- **Exam Administrators**: Can view aggregated monitoring data
- **Candidates**: Can request their monitoring data
- **Third Parties**: NO access to raw monitoring data

## Data Storage & Retention

### Storage

- All monitoring events are stored in MongoDB
- Data is stored with encryption at rest
- Server infrastructure follows industry security standards

### Retention Policy

- **Active Exams**: Data retained for duration of exam + appeals period
- **Default Retention**: 90 days after exam completion
- **Flagged Cases**: Extended retention for academic integrity investigations
- **After Retention**: Data is permanently deleted

### Data Deletion Rights

Candidates can request:
- Access to their monitoring data
- Explanation of their monitoring events
- Deletion of their data (subject to legal requirements)

## Legal Basis & Consent

### Consent Requirements

1. **Explicit Consent**
   - Candidates must provide explicit consent before exam starts
   - Consent banner clearly explains all monitoring activities
   - Declining consent prevents exam access

2. **Informed Consent**
   - Clear explanation of what is monitored
   - Clear explanation of what is NOT monitored
   - Explanation of how data is used

3. **Withdrawal of Consent**
   - Candidates can withdraw consent (but cannot complete exam)
   - Data from before withdrawal is retained per policy

### Legal Compliance

- **GDPR** (European Union): Full compliance with data protection regulations
- **CCPA** (California): Compliance with consumer privacy rights
- **FERPA** (US Education): Compliance with educational records privacy
- **Local Laws**: Compliance with applicable local data protection laws

## Security Measures

### Technical Safeguards

1. **Encryption**
   - WebSocket connections use TLS/SSL encryption
   - Data at rest is encrypted in MongoDB
   - Secure key management practices

2. **Access Control**
   - Role-based access control (RBAC)
   - Audit logging of data access
   - Multi-factor authentication for administrators

3. **Network Security**
   - CORS policies to prevent unauthorized access
   - Origin validation for WebSocket connections
   - Rate limiting to prevent abuse

### Organizational Safeguards

1. **Privacy by Design**
   - Minimal data collection principle
   - Data minimization built into system
   - Regular privacy impact assessments

2. **Staff Training**
   - Privacy and security training for administrators
   - Clear data handling procedures
   - Incident response protocols

3. **Third-Party Vendors**
   - Vendor security assessments
   - Data processing agreements
   - Regular security audits

## Candidate Rights

### Right to Access

- Request copy of monitoring data
- Receive data in machine-readable format
- Understand how data is processed

### Right to Rectification

- Correct inaccurate data
- Complete incomplete data
- Challenge incorrect interpretations

### Right to Erasure

- Request deletion of data
- Subject to legal retention requirements
- Applies after retention period

### Right to Object

- Object to data processing
- Provide justification for objection
- May prevent exam participation

### Right to Data Portability

- Receive data in portable format
- Transfer data to another controller
- Does not affect others' data

## Transparency & Accountability

### Data Processing Records

- We maintain detailed records of:
  - What data is collected
  - Why it is collected
  - How long it is retained
  - Who has access to it

### Privacy Impact Assessments

- Regular assessments of privacy risks
- Updates to policies and procedures
- Documentation of risk mitigation

### Incident Response

- Data breach notification procedures
- Candidate notification within 72 hours
- Regulatory notification as required

## Contact & Questions

### Data Protection Officer

For privacy-related questions or concerns:
- Email: privacy@example.com
- Mail: [Address]

### Data Subject Requests

To exercise your rights:
- Email: datasubject@example.com
- Online Portal: [URL]
- Response time: Within 30 days

### Complaints

If you believe your privacy rights have been violated:
- Internal complaint process
- Supervisory authority in your jurisdiction
- Legal remedies available

## Updates to This Policy

- Policy is reviewed annually
- Changes communicated to candidates
- Continued use implies acceptance
- Material changes require new consent

## Exam-Specific Disclosures

Before each exam, candidates will see:
- What monitoring features are enabled for this exam
- Whether paste is blocked
- Inactivity threshold settings
- Any exam-specific privacy considerations

## Technical Details

### Event Data Structure

Example monitoring event (what is actually stored):

```json
{
  "event_type": "TAB_SWITCHED",
  "timestamp": 1703001234567,
  "session_id": "anon-session-abc123",
  "candidate_id": "anon-candidate-xyz789",
  "inactive_duration": 5000,
  "received_at": "2024-01-01T12:34:56Z",
  "server_timestamp": 1703001234890
}
```

### No Content Examples

**Copy Event** (what we store):
```json
{
  "event_type": "COPY_DETECTED",
  "content_length": 150  // bytes only, NOT content
}
```

**NOT stored**: "The actual text that was copied"

## Best Practices for Candidates

### Minimize False Positives

1. **Before Exam**
   - Close unnecessary browser tabs
   - Disable notifications
   - Ensure stable internet connection

2. **During Exam**
   - Stay focused on exam tab
   - Avoid switching tabs/windows
   - Keep keyboard/mouse active when working

3. **If Interrupted**
   - Brief interruptions are expected and acceptable
   - Extended absences will be flagged for review
   - Contact proctor if technical issues occur

### Understanding Your Data

- You can request your monitoring data after exam
- Review what was logged
- Understand how events are interpreted
- Provide context for any flagged events

## Conclusion

We are committed to:
- Protecting candidate privacy
- Transparent data practices
- Minimal data collection
- Secure data handling
- Compliance with regulations
- Respecting candidate rights

If you have any questions or concerns about privacy, please contact us before taking the exam.

---

**Last Updated**: 2024-01-01  
**Version**: 1.0  
**Next Review**: 2025-01-01
