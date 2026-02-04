#!/usr/bin/env python3
"""
Comprehensive Test Suite for THALOS Prime Complete Application
Tests all integrated components and workflows
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

print("=" * 70)
print("THALOS Prime Complete System Test Suite")
print("=" * 70)

# Test 1: Configuration System
print("\n[1/8] Testing Configuration System...")
try:
    from thalos import init_config, get_config
    
    config = init_config()
    assert config is not None
    assert config.get('application.name') == 'THALOS Prime'
    assert config.get('application.version') is not None
    
    # Test nested access
    logging_level = config.get('logging.level')
    assert logging_level in ['DEBUG', 'INFO', 'WARNING', 'ERROR']
    
    print("✓ Configuration system working correctly")
    print(f"  - Application: {config.get('application.name')}")
    print(f"  - Version: {config.get('application.version')}")
    print(f"  - Environment: {config.get('application.environment')}")
except Exception as e:
    print(f"✗ Configuration test failed: {e}")
    sys.exit(1)

# Test 2: Logging System
print("\n[2/8] Testing Logging System...")
try:
    from thalos import init_logging, get_logger
    
    log_config = config.get_section('logging')
    init_logging(log_config)
    logger = get_logger('TestLogger')
    
    logger.debug("Debug message")
    logger.info("Info message")
    logger.warning("Warning message")
    
    print("✓ Logging system working correctly")
    print(f"  - Log level: {log_config.get('level')}")
    print(f"  - Console output: {log_config.get('console')}")
except Exception as e:
    print(f"✗ Logging test failed: {e}")
    sys.exit(1)

# Test 3: Matrix Codex Engine
print("\n[3/8] Testing Matrix Codex Engine...")
try:
    from thalos.engine import MatrixCodex, MatrixRenderer
    
    codex = MatrixCodex(dimensions=(128, 128, 128), complexity=2)
    codex.start()
    
    # Run a few updates
    for _ in range(5):
        codex.update()
    
    stats = codex.get_stats()
    assert stats['running'] == True
    assert stats['active_cells'] > 0
    assert stats['frame_count'] == 5
    
    # Test data processing
    test_data = [1.0, 2.0, 3.0, 4.0, 5.0]
    processed = codex.process_data(test_data)
    assert len(processed) == len(test_data)
    
    # Test visualization
    viz_data = codex.get_visualization_data()
    assert len(viz_data) > 0
    
    codex.stop()
    
    print("✓ Matrix Codex Engine working correctly")
    print(f"  - Dimensions: {stats['dimensions']}")
    print(f"  - Active cells: {stats['active_cells']}")
    print(f"  - Frames processed: {stats['frame_count']}")
except Exception as e:
    print(f"✗ Matrix Codex test failed: {e}")
    sys.exit(1)

# Test 4: Background Engine
print("\n[4/8] Testing Background Engine...")
try:
    from thalos.engine import BackgroundEngine
    
    engine = BackgroundEngine(resolution=(1920, 1080), particle_count=1000)
    engine.start()
    
    # Test different effects
    for effect in ['stars', 'waves', 'tunnel', 'swarm']:
        engine.set_effect(effect)
        for _ in range(3):
            engine.update()
        
        stats = engine.get_stats()
        assert stats['effect_mode'] == effect
        assert stats['particle_count'] > 0
    
    # Test render data
    render_data = engine.get_render_data()
    assert len(render_data) > 0
    assert 'position' in render_data[0]
    assert 'color' in render_data[0]
    
    engine.stop()
    
    print("✓ Background Engine working correctly")
    print(f"  - Resolution: {stats['resolution']}")
    print(f"  - Particles: {stats['particle_count']}")
    print(f"  - Effects tested: 4/4")
except Exception as e:
    print(f"✗ Background Engine test failed: {e}")
    sys.exit(1)

# Test 5: GUI System
print("\n[5/8] Testing GUI System...")
try:
    from thalos.gui import GUISystem, MenuItem
    
    gui = GUISystem(theme='dark')
    gui.start()
    
    # Test menu navigation
    gui.handle_input('down')
    assert gui.selected_index == 1
    
    gui.handle_input('up')
    assert gui.selected_index == 0
    
    # Test stats
    stats = gui.get_stats()
    assert stats['running'] == True
    assert stats['theme'] == 'dark'
    
    gui.stop()
    
    print("✓ GUI System working correctly")
    print(f"  - Theme: {stats['theme']}")
    print(f"  - Menu items: {stats['current_menu']}")
except Exception as e:
    print(f"✗ GUI System test failed: {e}")
    sys.exit(1)

# Test 6: Core Modules (from previous implementation)
print("\n[6/8] Testing Core Modules...")
try:
    from thalos_prime.math import Tensor, randn, Activations
    from thalos_prime.encoding import CharacterTokenizer
    from thalos_prime.crypto import SecureHash
    from thalos_prime.kernel import MemoryAllocator
    from thalos_prime.nn import Linear
    from thalos_prime.reasoning import SemanticBehavioralIntegration
    
    # Quick checks
    t = randn(3, 4)
    assert t.shape.dims == (3, 4)
    
    tok = CharacterTokenizer()
    tok.build_vocab(['test'])
    assert tok.vocab_size > 0
    
    hash_val = SecureHash.sha256('test')
    assert len(hash_val) == 64
    
    mem = MemoryAllocator(1024)
    addr = mem.allocate(100)
    assert addr == 0
    
    linear = Linear(10, 5)
    assert linear.in_features == 10
    
    sbi = SemanticBehavioralIntegration()
    result = sbi.process_input('test')
    assert 'analysis' in result
    
    print("✓ Core modules working correctly")
    print(f"  - 6/6 modules verified")
except Exception as e:
    print(f"✗ Core modules test failed: {e}")
    sys.exit(1)

# Test 7: Integration Test
print("\n[7/8] Testing Component Integration...")
try:
    # Test that all components can work together
    codex = MatrixCodex(dimensions=(64, 64, 64), complexity=1)
    engine = BackgroundEngine(resolution=(800, 600), particle_count=500)
    gui = GUISystem()
    
    codex.start()
    engine.start()
    gui.start()
    
    # Simulate a few frames
    for frame in range(10):
        codex.update()
        engine.update(0.016)
        # GUI would normally render here
    
    # Verify all still running
    assert codex.get_stats()['running'] == True
    assert engine.get_stats()['running'] == True
    assert gui.get_stats()['running'] == True
    
    # Cleanup
    codex.stop()
    engine.stop()
    gui.stop()
    
    print("✓ Component integration working correctly")
    print(f"  - Simulated 10 frames")
    print(f"  - All components synchronized")
except Exception as e:
    print(f"✗ Integration test failed: {e}")
    sys.exit(1)

# Test 8: Stress Test
print("\n[8/8] Running Stress Test...")
try:
    codex = MatrixCodex(dimensions=(256, 256, 256), complexity=3)
    engine = BackgroundEngine(particle_count=5000)
    
    codex.start()
    engine.start()
    
    # Run 100 frames
    for _ in range(100):
        codex.update()
        engine.update(0.016)
    
    codex_stats = codex.get_stats()
    engine_stats = engine.get_stats()
    
    assert codex_stats['frame_count'] == 100
    assert engine_stats['frame_count'] == 100
    
    codex.stop()
    engine.stop()
    
    print("✓ Stress test passed")
    print(f"  - Processed 100 frames")
    print(f"  - Matrix cells: {codex_stats['active_cells']}")
    print(f"  - Particles: {engine_stats['particle_count']}")
except Exception as e:
    print(f"✗ Stress test failed: {e}")
    sys.exit(1)

print("\n" + "=" * 70)
print("All Tests Passed! ✓")
print("=" * 70)
print("\nTHALOS Prime complete system is ready for deployment.")
print("Run 'python thalos_app.py' to start the full application.")
