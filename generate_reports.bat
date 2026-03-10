@echo off
REM 生成测试报告的批处理脚本

echo 正在运行测试并生成报告...

REM 运行测试并生成 Allure 结果和覆盖率报告
python -m pytest tests/ --alluredir=reports/allure-results --cov=src.dynamic_params --cov-report=html:reports/coverage-html --cov-report=xml:reports/coverage.xml --cov-report=term

if %errorlevel% neq 0 (
    echo 测试执行失败
    exit /b %errorlevel%
)

echo 生成 Allure 报告...
allure generate reports/allure-results -o reports/allure-report --clean

if %errorlevel% neq 0 (
    echo Allure 报告生成失败
    exit /b %errorlevel%
)

echo Report generation completed!
echo - Allure report: reports/allure-report/index.html
echo - Coverage HTML report: reports/coverage-html/index.html
echo - Coverage XML report: reports/coverage.xml