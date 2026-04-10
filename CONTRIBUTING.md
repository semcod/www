# Contributing to Semcod

## Code Quality Standards

To maintain code quality and prevent technical debt, we enforce the following standards:

### Growth Budget

- **max_file_size**: 400 lines - Files exceeding this must be split
- **max_function_cc**: 12 - Cyclomatic complexity limit for functions
- **max_new_loc_per_pr**: 500 lines - Maximum new lines per pull request
- **require_test_for_new_module**: true - Tests required for new modules
- **split_threshold**: 300 lines - Consider splitting when approaching this limit

### Quality Gate

The project uses a quality gate that runs before commits:
- Checks file line count against max_file_size
- Validates function cyclomatic complexity
- Tracks CC mean delta to prevent regression
- Enforces critical function count limits

Run quality gate manually: `python backend/quality_gate.py`

## Development Workflow

1. Create a feature branch from main
2. Make your changes respecting the growth budget
3. Add tests for new functionality
4. Run quality gate: `python backend/quality_gate.py`
5. Submit a pull request for review
