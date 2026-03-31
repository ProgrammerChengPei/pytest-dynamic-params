"""
Performance test runner and report generator.

Provides utilities for running performance tests and generating reports.
"""

import pytest
import time
import json
import sys
from pathlib import Path
from datetime import datetime


class PerformanceReport:
    """Generate performance test reports."""
    
    def __init__(self, output_dir=None):
        self.output_dir = output_dir or Path(__file__).parent
        self.results = []
        self.start_time = None
        self.end_time = None
    
    def start(self):
        """Start timing."""
        self.start_time = datetime.now()
    
    def end(self):
        """End timing."""
        self.end_time = datetime.now()
    
    def add_result(self, test_name, duration, status, metrics=None):
        """Add a test result."""
        self.results.append({
            "test_name": test_name,
            "duration_ms": duration * 1000,
            "status": status,
            "metrics": metrics or {},
            "timestamp": datetime.now().isoformat()
        })
    
    def generate_json_report(self, filename="performance_report.json"):
        """Generate JSON report."""
        report = {
            "metadata": {
                "start_time": self.start_time.isoformat() if self.start_time else None,
                "end_time": self.end_time.isoformat() if self.end_time else None,
                "total_tests": len(self.results),
                "passed": sum(1 for r in self.results if r["status"] == "passed"),
                "failed": sum(1 for r in self.results if r["status"] == "failed"),
                "skipped": sum(1 for r in self.results if r["status"] == "skipped"),
            },
            "results": self.results,
            "summary": self._generate_summary()
        }
        
        output_path = self.output_dir / filename
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        return output_path
    
    def generate_markdown_report(self, filename="performance_report.md"):
        """Generate Markdown report."""
        lines = []
        lines.append("# Performance Test Report\n")
        lines.append(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        if self.start_time and self.end_time:
            duration = (self.end_time - self.start_time).total_seconds()
            lines.append(f"**Total Duration**: {duration:.2f}s\n")
        
        lines.append("\n## Summary\n")
        lines.append(f"- Total Tests: {len(self.results)}")
        lines.append(f"- Passed: {sum(1 for r in self.results if r['status'] == 'passed')}")
        lines.append(f"- Failed: {sum(1 for r in self.results if r['status'] == 'failed')}")
        lines.append(f"- Skipped: {sum(1 for r in self.results if r['status'] == 'skipped')}\n")
        
        # Group by category
        categories = {}
        for result in self.results:
            category = result["test_name"].split("::")[0].replace("test_", "")
            if category not in categories:
                categories[category] = []
            categories[category].append(result)
        
        lines.append("\n## Results by Category\n")
        
        for category, results in categories.items():
            lines.append(f"\n### {category.title()}\n")
            lines.append("| Test | Duration (ms) | Status |")
            lines.append("|------|---------------|--------|")
            
            for result in sorted(results, key=lambda x: x["duration_ms"], reverse=True)[:20]:
                test_name = result["test_name"].split("::")[-1][:50]
                duration = result["duration_ms"]
                status = "✅" if result["status"] == "passed" else "❌"
                lines.append(f"| {test_name} | {duration:.2f} | {status} |")
        
        # Performance highlights
        lines.append("\n## Performance Highlights\n")
        
        if self.results:
            slowest = max(self.results, key=lambda x: x["duration_ms"])
            fastest = min(self.results, key=lambda x: x["duration_ms"])
            avg_duration = sum(r["duration_ms"] for r in self.results) / len(self.results)
            
            lines.append(f"\n- **Slowest Test**: {slowest['test_name']} ({slowest['duration_ms']:.2f}ms)")
            lines.append(f"- **Fastest Test**: {fastest['test_name']} ({fastest['duration_ms']:.2f}ms)")
            lines.append(f"- **Average Duration**: {avg_duration:.2f}ms")
        
        output_path = self.output_dir / filename
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        
        return output_path
    
    def _generate_summary(self):
        """Generate summary statistics."""
        if not self.results:
            return {}
        
        durations = [r["duration_ms"] for r in self.results]
        
        return {
            "total_tests": len(self.results),
            "avg_duration_ms": sum(durations) / len(durations),
            "min_duration_ms": min(durations),
            "max_duration_ms": max(durations),
            "median_duration_ms": sorted(durations)[len(durations) // 2],
            "pass_rate": sum(1 for r in self.results if r["status"] == "passed") / len(self.results)
        }


def run_performance_tests(
    test_dir=None,
    output_format="all",
    verbose=True,
    addopts=None
):
    """
    Run performance tests and generate reports.
    
    Args:
        test_dir: Directory containing performance tests
        output_format: Output format ('json', 'markdown', 'all')
        verbose: Print verbose output
        addopts: Additional pytest options
    
    Returns:
        PerformanceReport: Report object
    """
    test_dir = test_dir or Path(__file__).parent
    report = PerformanceReport(output_dir=test_dir)
    
    report.start()
    
    # Build pytest arguments
    args = [
        str(test_dir),
        "-v",
        "--tb=short",
        f"--json-report={test_dir / 'performance_results.json'}",
    ]
    
    if addopts:
        args.extend(addopts)
    
    # Run tests
    exit_code = pytest.main(args)
    
    report.end()
    
    # Parse results from JSON report
    json_report_path = test_dir / "performance_results.json"
    if json_report_path.exists():
        with open(json_report_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        for test in data.get("tests", []):
            report.add_result(
                test_name=test.get("nodeid", "unknown"),
                duration=test.get("duration", 0),
                status=test.get("outcome", "unknown"),
                metrics=test.get("metadata", {})
            )
    
    # Generate reports
    if output_format in ["json", "all"]:
        json_path = report.generate_json_report()
        if verbose:
            print(f"\nJSON report generated: {json_path}")
    
    if output_format in ["markdown", "all"]:
        md_path = report.generate_markdown_report()
        if verbose:
            print(f"Markdown report generated: {md_path}")
    
    return report, exit_code


if __name__ == "__main__":
    print("Running performance tests...")
    report, exit_code = run_performance_tests()
    
    if exit_code == 0:
        print("\n✅ All performance tests passed!")
    else:
        print(f"\n❌ Some performance tests failed (exit code: {exit_code})")
    
    sys.exit(exit_code)
