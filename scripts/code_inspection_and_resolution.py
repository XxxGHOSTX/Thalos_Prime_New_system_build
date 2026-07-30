#!/usr/bin/env python3
"""
THALOS Prime - Code Inspection and Resolution
Code analysis and issue resolution utilities.
"""

from typing import Dict, Any, List
import re


class CodeInspector:
    """Code inspection utilities."""
    
    def __init__(self):
        self.rules: List[Dict] = []
        self.findings: List[Dict] = []
    
    def add_rule(self, name: str, pattern: str, severity: str = 'warning') -> None:
        """Add an inspection rule."""
        self.rules.append({
            'name': name,
            'pattern': pattern,
            'severity': severity
        })
    
    def inspect(self, code: str) -> List[Dict]:
        """Inspect code for issues."""
        self.findings = []
        lines = code.split('\n')
        
        for i, line in enumerate(lines, 1):
            for rule in self.rules:
                if re.search(rule['pattern'], line):
                    self.findings.append({
                        'line': i,
                        'rule': rule['name'],
                        'severity': rule['severity'],
                        'content': line.strip()
                    })
        
        return self.findings
    
    def get_summary(self) -> Dict[str, Any]:
        """Get inspection summary."""
        return {
            'total_issues': len(self.findings),
            'by_severity': {
                'error': sum(1 for f in self.findings if f['severity'] == 'error'),
                'warning': sum(1 for f in self.findings if f['severity'] == 'warning'),
                'info': sum(1 for f in self.findings if f['severity'] == 'info')
            }
        }


class IssueResolver:
    """Resolve code issues."""
    
    def __init__(self):
        self.resolutions: Dict[str, callable] = {}
    
    def register_resolution(self, rule_name: str, fn: callable) -> None:
        """Register a resolution function."""
        self.resolutions[rule_name] = fn
    
    def resolve(self, code: str, finding: Dict) -> str:
        """Attempt to resolve an issue."""
        resolver = self.resolutions.get(finding['rule'])
        if resolver:
            return resolver(code, finding)
        return code


def main():
    inspector = CodeInspector()
    inspector.add_rule('print_statement', r'\bprint\(', 'info')
    inspector.add_rule('todo_comment', r'#\s*TODO', 'warning')
    
    code = '''
def hello():
    print("Hello")  # TODO: Remove this
    return True
'''
    
    findings = inspector.inspect(code)
    print("Findings:", findings)
    print("Summary:", inspector.get_summary())


if __name__ == '__main__':
    main()
