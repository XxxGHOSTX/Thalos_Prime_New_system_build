#!/usr/bin/env python3
"""
THALOS Prime - SBI Reasoning Core
Semantic Behavioral Integration reasoning engine.
"""

from typing import Dict, Any, List, Optional


class SBIReasoningCore:
    """Core reasoning engine for SBI."""
    
    def __init__(self):
        self.rules: List[Dict] = []
        self.knowledge: Dict[str, Any] = {}
        self.inference_chain: List[str] = []
    
    def add_rule(self, condition: str, action: str, weight: float = 1.0) -> None:
        """Add a reasoning rule."""
        self.rules.append({
            'condition': condition,
            'action': action,
            'weight': weight
        })
    
    def add_knowledge(self, key: str, value: Any) -> None:
        """Add knowledge to the engine."""
        self.knowledge[key] = value
    
    def reason(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply reasoning to input."""
        self.inference_chain = []
        
        # Apply rules
        applicable_rules = []
        for rule in self.rules:
            if self._matches(rule['condition'], input_data):
                applicable_rules.append(rule)
                self.inference_chain.append(f"Applied: {rule['condition']} -> {rule['action']}")
        
        # Select best action
        if applicable_rules:
            best_rule = max(applicable_rules, key=lambda r: r['weight'])
            return {
                'action': best_rule['action'],
                'confidence': best_rule['weight'],
                'chain': self.inference_chain
            }
        
        return {
            'action': 'default',
            'confidence': 0.5,
            'chain': self.inference_chain
        }
    
    def _matches(self, condition: str, data: Dict[str, Any]) -> bool:
        """Check if condition matches data."""
        return condition.lower() in str(data).lower()


def main():
    core = SBIReasoningCore()
    core.add_rule("greeting", "respond_greeting", 0.9)
    core.add_rule("question", "answer_question", 0.8)
    
    result = core.reason({'text': 'Hello, how are you?'})
    print("Reasoning result:", result)


if __name__ == '__main__':
    main()
