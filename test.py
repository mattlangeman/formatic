#!/usr/bin/env python
"""
Simple test runner script for Formatic project.
Uses Django's built-in test runner for reliability.

Usage:
    python test.py                    # Run all tests
    python test.py --models           # Run only model tests  
    python test.py --api              # Run only API tests
    python test.py --serializers      # Run only serializer tests
    python test.py --coverage         # Run with coverage report
    python test.py --verbose          # Extra verbose output
    python test.py --fast             # Fail fast on first error
    python test.py --specific apps.form_builder.tests.DynamicFormModelTests
"""

import os
import sys
import subprocess
import argparse

def run_command(cmd, description=""):
    """Run a shell command"""
    print(f"\n{'='*50}")
    print(f"Running: {description or ' '.join(cmd)}")
    print(f"{'='*50}")
    
    return subprocess.run(cmd, cwd=os.path.dirname(__file__))

def main():
    parser = argparse.ArgumentParser(description="Formatic Test Runner")
    
    # Test selection options
    parser.add_argument('--models', action='store_true', help='Run model tests only')
    parser.add_argument('--api', action='store_true', help='Run API tests only')
    parser.add_argument('--serializers', action='store_true', help='Run serializer tests only')
    parser.add_argument('--coverage', action='store_true', help='Run with coverage report')
    parser.add_argument('--verbose', '-v', action='store_true', help='Extra verbose output')
    parser.add_argument('--fast', action='store_true', help='Fail fast on first error')
    parser.add_argument('--specific', type=str, help='Run specific test class/method')
    
    args = parser.parse_args()
    
    # Base command
    cmd = ['pipenv', 'run', 'python', 'manage.py', 'test']
    
    # Test selection
    if args.models:
        cmd.append('apps.form_builder.tests')
    elif args.api:
        cmd.append('apps.form_builder_api.tests')
    elif args.serializers:
        cmd.append('apps.form_builder_api.test_serializers')
    elif args.specific:
        cmd.append(args.specific)
    else:
        cmd.append('apps')
    
    # Options
    verbosity = '3' if args.verbose else '2'
    cmd.extend(['--verbosity', verbosity])
    
    if args.fast:
        cmd.append('--failfast')
    
    # Run with coverage if requested
    if args.coverage:
        coverage_cmd = [
            'pipenv', 'run', 'coverage', 'run',
            '--source=apps',
            '--omit=*/migrations/*,*/tests/*,*/test_*.py,*/factories.py',
            'manage.py', 'test', 'apps'
        ]
        
        result = run_command(coverage_cmd, "Running tests with coverage")
        
        if result.returncode == 0:
            run_command(['pipenv', 'run', 'coverage', 'report'], "Coverage report")
            print("\n📊 HTML coverage report generated in htmlcov/index.html")
        
        return result.returncode
    else:
        result = run_command(cmd, "Running tests")
        return result.returncode

if __name__ == '__main__':
    sys.exit(main())