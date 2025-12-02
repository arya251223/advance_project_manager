from crewai import Agent, Task
from langchain_ollama import OllamaLLM
from backend.config import settings
from typing import Dict, Any, List
import json

from backend.utils.llm_factory import create_llm

class IntegratorTesterAgent:
    def __init__(self):
        self.llm = create_llm("integrator_tester") 
        
        self.agent = Agent(
            role="Integration Test Engineer",
            goal="Test integrated components and fix integration issues",
            backstory="""You are an experienced test engineer specializing in integration 
            testing. You write comprehensive tests to ensure all components work together 
            correctly and fix any issues found.""",
            llm=self.llm,
            verbose=True
        )
    
    def test_integration(self, files: Dict[str, str]) -> Dict[str, Any]:
        """Test the integrated system"""
        
        task = Task(
            description=f"""
            Create integration tests for these files:
            {list(files.keys())}
            
            Create:
            1. API endpoint tests
            2. Frontend-backend communication tests
            3. Data flow tests
            4. Error handling tests
            
            Also identify and fix any integration issues found.
            
            Return JSON with:
            - test_files: dict of test filename to code
            - fixes: dict of filename to fixed code (if any)
            - test_results: list of test results
            """,
            agent=self.agent,
            expected_output="JSON with tests and fixes"
        )
        
        result = task.execute()
        
        try:
            test_data = json.loads(result)
        except:
            test_data = self._create_default_tests()
        
        return test_data
    
    def _create_default_tests(self) -> Dict[str, Any]:
        """Create default integration tests"""
        
        test_files = {}
        
        # API integration tests
        test_files["test_api_integration.py"] = """import pytest
import requests
import json
from fastapi.testclient import TestClient
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app

client = TestClient(app)

class TestAPIIntegration:
    def test_health_endpoint(self):
        \"\"\"Test health check endpoint\"\"\"
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}
    
    def test_root_endpoint(self):
        \"\"\"Test root endpoint\"\"\"
        response = client.get("/")
        assert response.status_code == 200
        assert "message" in response.json()
    
    def test_process_endpoint_valid_data(self):
        \"\"\"Test process endpoint with valid data\"\"\"
        test_data = {
            "data": "test input",
            "options": {"key": "value"}
        }
        response = client.post("/process", json=test_data)
        assert response.status_code == 200
        assert response.json()["status"] == "success"
    
    def test_process_endpoint_invalid_data(self):
        \"\"\"Test process endpoint with invalid data\"\"\"
        response = client.post("/process", json={})
        assert response.status_code == 422
    
    def test_cors_headers(self):
        \"\"\"Test CORS headers are properly set\"\"\"
        response = client.options("/")
        assert "access-control-allow-origin" in response.headers
    
    def test_error_handling(self):
        \"\"\"Test API error handling\"\"\"
        response = client.get("/nonexistent")
        assert response.status_code == 404

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
"""
        # Frontend integration tests
        test_files["test_frontend_integration.js"] = """// Frontend Integration Tests
class FrontendIntegrationTests {
    constructor() {
        this.apiUrl = 'http://localhost:8000';
        this.testResults = [];
    }
    
    async runAllTests() {
        console.log('Running Frontend Integration Tests...');
        
        await this.testAPIConnection();
        await this.testDataProcessing();
        await this.testErrorHandling();
        await this.testUIUpdates();
        
        this.printResults();
    }
    
    async testAPIConnection() {
        try {
            const response = await fetch(`${this.apiUrl}/health`);
            const data = await response.json();
            
            this.addResult('API Connection', data.status === 'healthy', 
                'API is reachable and healthy');
        } catch (error) {
            this.addResult('API Connection', false, error.message);
        }
    }
    
    async testDataProcessing() {
        try {
            const testData = { data: 'test', options: {} };
            const response = await fetch(`${this.apiUrl}/process`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(testData)
            });
            
            const result = await response.json();
            this.addResult('Data Processing', result.status === 'success',
                'Data processing endpoint works correctly');
        } catch (error) {
            this.addResult('Data Processing', false, error.message);
        }
    }
    
    async testErrorHandling() {
        try {
            const response = await fetch(`${this.apiUrl}/invalid-endpoint`);
            this.addResult('Error Handling', response.status === 404,
                'Invalid endpoints return 404');
        } catch (error) {
            this.addResult('Error Handling', false, error.message);
        }
    }
    
    async testUIUpdates() {
        const resultsDiv = document.getElementById('results');
        const inputField = document.getElementById('inputData');
        
        this.addResult('UI Elements', 
            resultsDiv !== null && inputField !== null,
            'Required UI elements exist');
    }
    
    addResult(testName, passed, message) {
        this.testResults.push({
            test: testName,
            passed: passed,
            message: message
        });
    }
    
    printResults() {
        console.log('\\n=== Test Results ===');
        this.testResults.forEach(result => {
            const status = result.passed ? '✓ PASS' : '✗ FAIL';
            console.log(`${status} - ${result.test}: ${result.message}`);
        });
        
        const passed = this.testResults.filter(r => r.passed).length;
        const total = this.testResults.length;
        console.log(`\\nTotal: ${passed}/${total} tests passed`);
    }
}
window.addEventListener('load', () => {
    const tester = new FrontendIntegrationTests();
    tester.runAllTests();
});
"""
        # Integration test runner
        test_files["run_integration_tests.py"] = """#!/usr/bin/env python3
\"\"\"
Integration Test Runner
Runs all integration tests and generates a report
\"\"\"
import subprocess
import sys
import json
import time
from datetime import datetime
class IntegrationTestRunner:
    def __init__(self):
        self.results = []
        self.start_time = None
        self.end_time = None
    def run_python_tests(self):
        \"\"\"Run Python integration tests\"\"\"
        print("Running Python integration tests...")
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pytest", "test_api_integration.py", "-v", "--json-report"],
                capture_output=True,
                text=True
            )
            
            self.results.append({
                "test_suite": "Python API Tests",
                "passed": result.returncode == 0,
                "output": result.stdout,
                "errors": result.stderr
            })
        except Exception as e:
            self.results.append({
                "test_suite": "Python API Tests",
                "passed": False,
                "output": "",
                "errors": str(e)
            })
    def check_services(self):
        \"\"\"Check if required services are running\"\"\"
        print("Checking services...")
        
        # Check if API is running
        try:
            import requests
            response = requests.get("http://localhost:8000/health", timeout=5)
            api_running = response.status_code == 200
        except:
            api_running = False
        
        self.results.append({
            "test_suite": "Service Health",
            "passed": api_running,
            "output": "API is running" if api_running else "API is not running",
            "errors": "" if api_running else "Failed to connect to API"
        })
    
    def generate_report(self):
        \"\"\"Generate test report\"\"\"
        report = {
            "timestamp": datetime.now().isoformat(),
            "duration": (self.end_time - self.start_time).total_seconds(),
            "total_suites": len(self.results),
            "passed_suites": len([r for r in self.results if r["passed"]]),
            "results": self.results
        }
        
        # Save report
        with open("integration_test_report.json", "w") as f:
            json.dump(report, f, indent=2)
        
        # Print summary
        print("\\n" + "="*50)
        print("INTEGRATION TEST SUMMARY")
        print("="*50)
        print(f"Total Test Suites: {report['total_suites']}")
        print(f"Passed: {report['passed_suites']}")
        print(f"Failed: {report['total_suites'] - report['passed_suites']}")
        print(f"Duration: {report['duration']:.2f} seconds")
        print("\\nDetailed report saved to: integration_test_report.json")
    
    def run(self):
        \"\"\"Run all integration tests\"\"\"
        self.start_time = datetime.now()
        
        self.check_services()
        self.run_python_tests()
        
        self.end_time = datetime.now()
        self.generate_report()

if __name__ == "__main__":
    runner = IntegrationTestRunner()
    runner.run()
"""
        test_files["test_requirements.txt"] = """pytest==7.4.3
pytest-json-report==1.5.0
requests==2.31.0
"""
        return {
            "test_files": test_files,
            "fixes": {},
            "test_results": [
                {"test": "API Health Check", "status": "pending"},
                {"test": "Frontend-Backend Integration", "status": "pending"},
                {"test": "Data Flow", "status": "pending"},
                {"test": "Error Handling", "status": "pending"}
            ]
        }
