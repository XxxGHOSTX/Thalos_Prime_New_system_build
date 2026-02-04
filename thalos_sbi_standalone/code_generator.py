"""
THALOS SBI Standalone - Code Generator
Generates code based on natural language descriptions.
"""

from typing import Dict, Any, Optional, List


class CodeGenerator:
    """Generate code from natural language descriptions."""
    
    def __init__(self):
        self.templates = self._load_templates()
        self.language_configs = {
            'python': {'extension': '.py', 'comment': '#'},
            'javascript': {'extension': '.js', 'comment': '//'},
            'java': {'extension': '.java', 'comment': '//'},
            'cpp': {'extension': '.cpp', 'comment': '//'},
        }
    
    def _load_templates(self) -> Dict[str, str]:
        """Load code templates."""
        return {
            'function': '''def {name}({params}):
    """
    {description}
    """
    {body}
    return result
''',
            'class': '''class {name}:
    """
    {description}
    """
    
    def __init__(self{params}):
        {init_body}
    
    def {method_name}(self):
        {method_body}
''',
            'module': '''"""
{description}
"""

{imports}

{body}

if __name__ == '__main__':
    main()
'''
        }
    
    def generate(self, description: str, language: str = 'python',
                 template_type: str = 'function') -> str:
        """Generate code from description."""
        template = self.templates.get(template_type, self.templates['function'])
        
        # Parse description for parameters
        params = self._extract_params(description)
        name = self._extract_name(description)
        
        # Fill template
        code = template.format(
            name=name,
            params=', '.join(params),
            description=description,
            body='    result = None  # TODO: Implement',
            imports='',
            init_body='pass',
            method_name='process',
            method_body='pass'
        )
        
        return code
    
    def _extract_params(self, description: str) -> List[str]:
        """Extract parameters from description."""
        keywords = ['with', 'using', 'taking', 'accepting']
        params = []
        
        for keyword in keywords:
            if keyword in description.lower():
                # Simple extraction
                parts = description.lower().split(keyword)
                if len(parts) > 1:
                    param_text = parts[1].split()[0] if parts[1].split() else 'data'
                    params.append(param_text)
        
        return params if params else ['data']
    
    def _extract_name(self, description: str) -> str:
        """Extract function/class name from description."""
        action_words = ['create', 'generate', 'make', 'build', 'write']
        
        for word in action_words:
            if word in description.lower():
                parts = description.lower().split(word)
                if len(parts) > 1:
                    words = parts[1].strip().split()
                    if words:
                        return '_'.join(words[:2])
        
        return 'generated_function'


class TemplateEngine:
    """Template-based code generation."""
    
    def __init__(self):
        self.templates: Dict[str, str] = {}
    
    def register_template(self, name: str, template: str) -> None:
        """Register a template."""
        self.templates[name] = template
    
    def render(self, template_name: str, context: Dict[str, Any]) -> str:
        """Render a template with context."""
        template = self.templates.get(template_name, '')
        
        for key, value in context.items():
            placeholder = '{' + key + '}'
            template = template.replace(placeholder, str(value))
        
        return template


class CodeFormatter:
    """Format generated code."""
    
    @staticmethod
    def format_python(code: str) -> str:
        """Format Python code."""
        lines = code.split('\n')
        formatted = []
        indent_level = 0
        
        for line in lines:
            stripped = line.strip()
            
            # Decrease indent for certain keywords
            if stripped.startswith(('else:', 'elif', 'except:', 'finally:', 'except ')):
                indent_level = max(0, indent_level - 1)
            
            if stripped:
                formatted.append('    ' * indent_level + stripped)
            else:
                formatted.append('')
            
            # Increase indent after colons
            if stripped.endswith(':'):
                indent_level += 1
        
        return '\n'.join(formatted)


# Export classes
__all__ = [
    'CodeGenerator',
    'TemplateEngine',
    'CodeFormatter'
]
