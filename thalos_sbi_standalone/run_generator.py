"""
THALOS SBI Standalone - Run Generator
Command-line interface for running the SBI generator.
"""

import sys
from typing import Optional, Dict, Any


def main():
    """Main entry point for run generator."""
    print("=" * 60)
    print("THALOS SBI Standalone Generator")
    print("=" * 60)
    
    # Import local modules
    try:
        from .core_engine import SBICoreEngine, SemanticProcessor, BehavioralProcessor
        from .code_generator import CodeGenerator
    except ImportError:
        # Running standalone
        from core_engine import SBICoreEngine, SemanticProcessor, BehavioralProcessor
        from code_generator import CodeGenerator
    
    # Initialize engine
    engine = SBICoreEngine()
    engine.add_processor(SemanticProcessor())
    engine.add_processor(BehavioralProcessor())
    
    # Initialize code generator
    code_gen = CodeGenerator()
    
    print("\nSystem initialized. Available commands:")
    print("  - 'process <text>' - Process text through SBI")
    print("  - 'generate <description>' - Generate code")
    print("  - 'status' - Show system status")
    print("  - 'quit' - Exit the generator")
    print()
    
    while True:
        try:
            user_input = input(">>> ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("Goodbye!")
                break
            
            if user_input.lower() == 'status':
                print(engine.get_status())
                continue
            
            if user_input.lower().startswith('process '):
                text = user_input[8:]
                result = engine.process({'text': text})
                print(f"Result: {result}")
                continue
            
            if user_input.lower().startswith('generate '):
                description = user_input[9:]
                code = code_gen.generate(description)
                print(f"\nGenerated code:\n{code}")
                continue
            
            # Default: process as text
            result = engine.process({'text': user_input})
            print(f"Processed: {result}")
            
        except KeyboardInterrupt:
            print("\nInterrupted. Goodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")


def run_batch(inputs: list) -> list:
    """Run batch processing on inputs."""
    try:
        from .core_engine import SBICoreEngine, SemanticProcessor, BehavioralProcessor
    except ImportError:
        from core_engine import SBICoreEngine, SemanticProcessor, BehavioralProcessor
    
    engine = SBICoreEngine()
    engine.add_processor(SemanticProcessor())
    engine.add_processor(BehavioralProcessor())
    
    results = []
    for item in inputs:
        result = engine.process({'text': item})
        results.append(result)
    
    return results


if __name__ == '__main__':
    main()
