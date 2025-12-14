# Contributing to Exam Proctoring System

Thank you for your interest in contributing to the Exam Proctoring System!

## Development Setup

Please follow the setup instructions in [QUICK_START.md](QUICK_START.md) to get your development environment ready.

## Code Standards

### Backend (Python/FastAPI)

- Follow PEP 8 style guide
- Use type hints for all function parameters and return values
- Write docstrings for all public functions and classes
- Keep functions focused and small (< 50 lines ideally)
- Use meaningful variable and function names

**Example:**

```python
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.
    
    Args:
        data: Dictionary containing token claims
        expires_delta: Optional custom expiration time
        
    Returns:
        Encoded JWT token string
    """
    # Implementation
```

### Frontend (TypeScript/Next.js)

- Use TypeScript for all new code
- Follow React best practices (functional components, hooks)
- Use meaningful component and variable names
- Keep components focused and reusable
- Add proper TypeScript types for props and state

**Example:**

```typescript
interface LoginFormProps {
  onSuccess?: () => void;
  onError?: (error: string) => void;
}

export default function LoginForm({ onSuccess, onError }: LoginFormProps) {
  // Implementation
}
```

## Testing

### Backend Tests

All new features must include tests:

```bash
cd backend
source venv/bin/activate
pytest
```

**Test Coverage Requirements:**
- Unit tests for all business logic
- Integration tests for all API endpoints
- Minimum 80% code coverage

**Writing Tests:**

```python
def test_feature_name():
    """Test description of what this test validates."""
    # Arrange
    # Act
    # Assert
```

### Running Tests with Coverage

```bash
pytest --cov=app --cov-report=term-missing
```

## Git Workflow

### Branch Naming

- Feature: `feature/description`
- Bug fix: `fix/description`
- Hotfix: `hotfix/description`

### Commit Messages

Follow conventional commits format:

```
type(scope): description

[optional body]

[optional footer]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**

```
feat(auth): add password reset functionality

fix(users): prevent admin from deleting self

docs(api): update authentication endpoint documentation

test(auth): add tests for token refresh flow
```

### Pull Request Process

1. Create a feature branch from `main`
2. Make your changes with clear commit messages
3. Write/update tests
4. Ensure all tests pass
5. Update documentation if needed
6. Create a pull request with:
   - Clear title and description
   - Reference to related issues
   - Screenshots (if UI changes)

## Code Review Guidelines

### For Reviewers

- Be respectful and constructive
- Focus on code quality, not coding style preferences
- Check for:
  - Security vulnerabilities
  - Performance implications
  - Test coverage
  - Documentation completeness

### For Contributors

- Respond to feedback promptly
- Ask for clarification if feedback is unclear
- Be open to suggestions

## Security

### Reporting Security Issues

**DO NOT** create public issues for security vulnerabilities.

Instead:
1. Email security details to [security contact]
2. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

### Security Best Practices

- Never commit sensitive data (passwords, API keys, etc.)
- Always use parameterized queries
- Validate all user input
- Use proper authentication and authorization
- Keep dependencies up to date

## API Changes

### Breaking Changes

Breaking changes require:
1. Discussion in issue tracker
2. Version bump (major version)
3. Migration guide for users
4. Deprecated version support period

### Adding New Endpoints

1. Update OpenAPI documentation (automatic via FastAPI)
2. Add integration tests
3. Update API_DOCUMENTATION.md
4. Add usage examples

## Database Changes

### Schema Migrations

When adding database migrations (Phase 2):

1. Create migration script
2. Test migration on sample data
3. Include rollback script
4. Document changes in migration notes

### Database Guidelines

- Always use transactions for multi-step operations
- Add appropriate indexes for query performance
- Use foreign keys for referential integrity
- Document complex queries

## Documentation

### Required Documentation

- **Code Comments**: Complex logic, non-obvious decisions
- **Docstrings**: All public functions and classes
- **API Documentation**: All endpoints in API_DOCUMENTATION.md
- **README**: Major feature additions
- **CHANGELOG**: All user-facing changes

## Performance

### Performance Considerations

- Profile code before optimizing
- Consider database query efficiency
- Use caching where appropriate
- Optimize frontend bundle size

### Performance Testing

```bash
# Backend load testing (to be added)
# Frontend performance audit
npm run build
npm run analyze
```

## Accessibility

### Frontend Accessibility

- Use semantic HTML
- Provide ARIA labels where needed
- Ensure keyboard navigation works
- Test with screen readers
- Maintain good color contrast

## Questions?

- Check existing documentation
- Search closed issues
- Create a new issue with the `question` label

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.
