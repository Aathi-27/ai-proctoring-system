# Contributing Guide

Thank you for considering contributing to the Online Exam Proctoring system!

## Development Setup

1. **Fork and Clone**
   ```bash
   git clone <your-fork-url>
   cd project
   ```

2. **Backend Setup**
   ```bash
   cd backend
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   ```

## Code Style

### Python (Backend)
- Follow PEP 8 style guide
- Use type hints for all functions
- Async/await for I/O operations
- Docstrings for public methods
- Use snake_case for variables/functions
- Use PascalCase for classes

### TypeScript (Frontend)
- Use TypeScript strict mode
- Explicit types for props and returns
- Functional components with hooks
- camelCase for variables/functions
- PascalCase for components
- 'use client' for client-side components

## Git Workflow

1. **Create a Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Changes**
   - Write clean, documented code
   - Follow existing patterns
   - Test your changes

3. **Commit**
   ```bash
   git add .
   git commit -m "feat: description of changes"
   ```

4. **Push**
   ```bash
   git push origin feature/your-feature-name
   ```

5. **Create Pull Request**
   - Describe your changes
   - Reference any issues
   - Add screenshots if UI changes

## Commit Message Format

Use conventional commits:

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code style changes (formatting)
- `refactor:` Code refactoring
- `test:` Adding tests
- `chore:` Maintenance tasks

Examples:
```
feat: add video quality selector
fix: resolve reconnection issue
docs: update WebSocket protocol docs
```

## Testing

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend
npm test
```

### Manual Testing
- Test in Chrome, Firefox, and Edge
- Verify WebSocket connections
- Check error handling
- Test with multiple users

## Pull Request Checklist

Before submitting a PR:

- [ ] Code follows style guidelines
- [ ] Tests pass
- [ ] Documentation updated
- [ ] No console errors
- [ ] Tested in multiple browsers
- [ ] Commits are clean and descriptive
- [ ] No sensitive data in code

## Areas for Contribution

### High Priority
- [ ] Add authentication system
- [ ] Implement video recording
- [ ] Add screen sharing
- [ ] Create admin dashboard
- [ ] Add test suite

### Medium Priority
- [ ] Improve error messages
- [ ] Add more quality presets
- [ ] Optimize bandwidth usage
- [ ] Add mobile support
- [ ] Implement analytics

### Low Priority
- [ ] UI improvements
- [ ] Add dark mode
- [ ] Internationalization (i18n)
- [ ] Accessibility improvements
- [ ] Performance optimizations

## Questions?

- Review existing documentation
- Check [QUICKSTART.md](QUICKSTART.md)
- Read [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.
