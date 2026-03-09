# Reports

This directory contains test reports for the pytest-dynamic-params plugin.

## Report Types

- Allure reports: Detailed test execution reports
- Coverage reports: Code coverage analysis

## Generated Reports

### Allure Report
- Location: `allure-report/index.html`
- Contains detailed test execution results, charts, and statistics

### Coverage Reports
- HTML: `coverage-html/index.html`
- XML: `coverage.xml`
- Provides code coverage metrics and visualization

### Summary
- Summary: `SUMMARY.md`
- Contains an overview of test results and coverage metrics

## Report Generation

To regenerate reports, run:
```bash
python -m pytest --alluredir=reports/allure-results --cov=src.dynamic_params --cov-report=html:reports/coverage-html --cov-report=xml:reports/coverage.xml --cov-report=term
allure generate reports/allure-results -o reports/allure-report --clean
```