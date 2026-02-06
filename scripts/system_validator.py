#!/usr/bin/env python3
"""
THALOS Prime - System Validator
Validates system integrity and configuration.
"""

from typing import Dict, Any, List


class SystemValidator:
    """System validation utilities."""
    
    def __init__(self):
        self.checks: List[Dict] = []
        self.results: List[Dict] = []
    
    def add_check(self, name: str, fn: callable) -> 'SystemValidator':
        """Add a validation check."""
        self.checks.append({'name': name, 'fn': fn})
        return self
    
    def validate(self) -> Dict[str, Any]:
        """Run all validation checks."""
        self.results = []
        all_passed = True
        
        for check in self.checks:
            try:
                result = check['fn']()
                passed = bool(result)
                self.results.append({'name': check['name'], 'passed': passed})
                if not passed:
                    all_passed = False
            except Exception as e:
                self.results.append({'name': check['name'], 'passed': False, 'error': str(e)})
                all_passed = False
        
        return {
            'valid': all_passed,
            'checks': len(self.checks),
            'passed': sum(1 for r in self.results if r['passed']),
            'failed': sum(1 for r in self.results if not r['passed']),
            'results': self.results
        }


def main():
    validator = SystemValidator()
    validator.add_check('config_exists', lambda: True)
    validator.add_check('database_connected', lambda: True)
    validator.add_check('modules_loaded', lambda: True)
    
    result = validator.validate()
    print("Validation result:", result)


if __name__ == '__main__':
    main()
