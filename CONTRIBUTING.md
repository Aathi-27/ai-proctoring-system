# Contributing to Exam Activity Monitoring System

Thank you for your interest in contributing to the Exam Activity Monitoring System! This document provides guidelines and instructions for contributing.

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Respect privacy and security considerations
- Follow best practices for secure coding

## Getting Started

### Prerequisites

- Node.js 18+ and npm
- Python 3.11+
- MongoDB 7.0+
- Git
- Docker & Docker Compose (optional)

### Development Setup

1. **Fork and Clone**
   ```bash
   git clone https://github.com/your-username/exam-monitoring.git
   cd exam-monitoring
   ```

2. **Install Dependencies**
   ```bash
   # Frontend
   cd frontend
   npm install
   
   # Backend
   cd ../backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Setup Environment Variables**
   ```bash
   # Backend
   cp backend/.env.example backend/.env
   
   # Frontend
   cp frontend/.env.example frontend/.env.local
   ```

4. **Start Development Servers**
   ```bash
   # Option 1: Using Docker Compose (recommended)
   docker-compose up -d
   
   # Option 2: Manual startup
   # Terminal 1 - MongoDB
   docker run -d -p 27017:27017 mongo:7.0
   
   # Terminal 2 - Backend
   cd backend
   uvicorn app.main:app --reload
   
   # Terminal 3 - Frontend
   cd frontend
   npm run dev
   ```

## Development Workflow

### Branch Naming Convention

- `feature/description` - New features
- `fix/description` - Bug fixes
- `docs/description` - Documentation updates
- `test/description` - Test additions/improvements
- `refactor/description` - Code refactoring

### Commit Message Convention

Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>(<scope>): <subject>

<body>

<footer>
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `test`: Test additions/improvements
- `refactor`: Code refactoring
- `style`: Code style changes (formatting, etc.)
- `chore`: Maintenance tasks

Examples:
```
feat(monitoring): add network request tracking
fix(websocket): resolve reconnection loop issue
docs(readme): update installation instructions
test(clipboard): add paste blocking tests
```

## Testing Guidelines

### Frontend Tests

```bash
cd frontend

# Run all tests
npm test

# Run with coverage
npm test -- --coverage

# Watch mode
npm run test:watch
```

**Test Requirements:**
- Minimum 80% code coverage
- Test all monitoring components
- Test WebSocket connection handling
- Test event emission and handling

### Backend Tests

```bash
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest app/tests/test_models.py
```

**Test Requirements:**
- Minimum 80% code coverage
- Test all API endpoints
- Test WebSocket message handling
- Test database operations

### Writing Tests

**Frontend Example:**
```typescript
import { render, waitFor } from '@testing-library/react';
import { TabVisibilityMonitor } from '../../components/monitoring/TabVisibilityMonitor';

describe('TabVisibilityMonitor', () => {
  it('should emit event on tab switch', async () => {
    // Test implementation
  });
});
```

**Backend Example:**
```python
import pytest

@pytest.mark.asyncio
async def test_handle_monitoring_event():
    # Test implementation
    pass
```

## Code Style Guidelines

### TypeScript/React

- Use TypeScript for type safety
- Use functional components with hooks
- Use interfaces for types, not type aliases
- Follow ESLint rules (run `npm run lint`)
- Use meaningful variable and function names
- Avoid inline styles where possible

**Good Example:**
```typescript
interface MonitoringConfig {
  sessionId: string;
  candidateId: string;
  inactivityThreshold: number;
}

export const ActivityMonitor: React.FC<{ config: MonitoringConfig }> = ({ config }) => {
  const { sendEvent } = useWebSocket({ url: config.websocketUrl });
  
  return <div>{/* implementation */}</div>;
};
```

### Python/FastAPI

- Use async/await for I/O operations
- Use Pydantic models for validation
- Follow PEP 8 style guide
- Use type hints
- Use descriptive function and variable names

**Good Example:**
```python
from pydantic import BaseModel
from typing import Optional

class MonitoringEvent(BaseModel):
    type: str
    timestamp: int
    session_id: Optional[str] = None

async def handle_event(event: MonitoringEvent) -> None:
    await db.insert_event(event.dict())
```

## Privacy & Security Considerations

### Critical Rules

1. **Never Log Sensitive Data**
   - ❌ DO NOT log clipboard content
   - ❌ DO NOT log keystrokes
   - ❌ DO NOT log personal information
   - ✅ DO log event occurrence and metadata only

2. **Data Minimization**
   - Only collect data necessary for exam integrity
   - Use anonymized identifiers
   - Implement data retention policies

3. **Secure Communication**
   - Always use WebSocket with TLS in production
   - Validate origin for WebSocket connections
   - Implement proper CORS policies

4. **Input Validation**
   - Validate all event data on backend
   - Sanitize user inputs
   - Use Pydantic models for validation

### Code Review Checklist

Before submitting PR, verify:
- [ ] No sensitive data is logged
- [ ] All user inputs are validated
- [ ] Tests pass with ≥80% coverage
- [ ] Documentation is updated
- [ ] Privacy guidelines are followed
- [ ] No console.log statements (use proper logging)
- [ ] Error handling is implemented

## Pull Request Process

### Before Submitting

1. **Update from main**
   ```bash
   git checkout main
   git pull origin main
   git checkout your-feature-branch
   git rebase main
   ```

2. **Run Tests**
   ```bash
   # Frontend
   cd frontend && npm test
   
   # Backend
   cd backend && pytest
   ```

3. **Lint Code**
   ```bash
   # Frontend
   cd frontend && npm run lint
   
   # Backend (if configured)
   cd backend && flake8 app/
   ```

### PR Template

Use this template for your PR description:

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Tests added/updated
- [ ] All tests passing
- [ ] Coverage ≥80%

## Privacy & Security
- [ ] No sensitive data logged
- [ ] Input validation implemented
- [ ] Privacy guidelines followed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-reviewed code
- [ ] Commented complex logic
- [ ] Documentation updated
- [ ] No breaking changes (or documented)
```

### Review Process

1. PR submitted → Automated tests run
2. Code review by maintainers
3. Address feedback
4. Approval required from 1+ maintainers
5. Merge to main

## Adding New Features

### Frontend Components

1. Create component in `frontend/src/components/`
2. Add TypeScript types in `frontend/src/types/`
3. Write tests in `frontend/src/__tests__/`
4. Update documentation

### Backend Endpoints

1. Add route in `backend/app/main.py`
2. Create models in `backend/app/models.py`
3. Write tests in `backend/app/tests/`
4. Update API documentation

### Adding Monitoring Events

1. **Define Event Type** in `frontend/src/types/monitoring.ts`:
   ```typescript
   export enum MonitoringEventType {
     NEW_EVENT = 'NEW_EVENT',
   }
   ```

2. **Create Event Interface**:
   ```typescript
   export interface NewEvent extends BaseMonitoringEvent {
     type: MonitoringEventType.NEW_EVENT;
     customField: string;
   }
   ```

3. **Update Backend Model** in `backend/app/models.py`:
   ```python
   class MonitoringEventType(str, Enum):
       NEW_EVENT = "NEW_EVENT"
   ```

4. **Create Monitor Component**:
   ```typescript
   export const NewMonitor: React.FC<Props> = ({ enabled }) => {
     // Implementation
   };
   ```

5. **Add Tests** for new component and backend handling

6. **Update Documentation** in README.md

## Documentation

### Code Comments

- Comment complex logic only
- Use JSDoc for functions/components
- Explain "why", not "what"

**Good Example:**
```typescript
/**
 * Tracks keyboard and mouse inactivity using event listeners.
 * Emits INACTIVITY events after configurable threshold.
 * 
 * @param enabled - Whether monitoring is active
 * @param inactivityThreshold - Time in ms before considering inactive
 */
export const InactivityTracker: React.FC<Props> = ({ enabled, inactivityThreshold }) => {
  // Implementation
};
```

### README Updates

When adding features:
1. Update feature list
2. Add configuration options
3. Update API documentation
4. Add examples

## Common Issues & Solutions

### WebSocket Connection Issues

**Problem:** WebSocket not connecting

**Solution:**
- Check CORS configuration
- Verify WebSocket URL
- Check network connectivity
- Review browser console for errors

### Test Failures

**Problem:** Tests failing locally

**Solution:**
```bash
# Clear cache
rm -rf node_modules/.cache

# Reinstall dependencies
npm ci

# Run tests
npm test
```

### MongoDB Connection Issues

**Problem:** Cannot connect to MongoDB

**Solution:**
```bash
# Check MongoDB is running
docker ps | grep mongo

# Start MongoDB
docker run -d -p 27017:27017 mongo:7.0

# Test connection
mongosh mongodb://localhost:27017
```

## Questions & Support

- **Issues**: Open a GitHub issue
- **Discussions**: Use GitHub Discussions
- **Security**: Email security@example.com
- **Privacy**: Email privacy@example.com

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Recognition

Contributors will be recognized in:
- CONTRIBUTORS.md file
- Release notes
- Project documentation

Thank you for contributing! 🎉
