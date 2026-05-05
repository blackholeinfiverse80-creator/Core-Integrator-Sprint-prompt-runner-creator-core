"""
Quick Component Validation
Tests each component individually to identify issues
"""

import sys
import importlib.util

def test_imports():
    """Test if all required modules can be imported"""
    print("=" * 60)
    print("TESTING IMPORTS")
    print("=" * 60)
    
    tests = {
        "FastAPI": "fastapi",
        "Requests": "requests",
        "Pydantic": "pydantic",
        "Uvicorn": "uvicorn"
    }
    
    all_passed = True
    for name, module in tests.items():
        try:
            __import__(module)
            print(f"[PASS] {name}")
        except ImportError as e:
            print(f"[FAIL] {name}: {e}")
            all_passed = False
    
    return all_passed

def test_file_structure():
    """Test if all required files exist"""
    print("\n" + "=" * 60)
    print("TESTING FILE STRUCTURE")
    print("=" * 60)
    
    from pathlib import Path
    
    required_files = [
        "main.py",
        "integration_bridge.py",
        "bhiv_bucket.py",
        "ttg_ttv_api.py",
        "src/adapters/tantra_bridge.py",
        "src/adapters/ttg_input_normalizer.py",
        "src/adapters/ttv_input_normalizer.py",
        "src/adapters/ttg_output_adapter.py",
        "src/adapters/ttv_output_adapter.py",
        "prompt-runner01/api.py",
        "prompt-runner01/run_server.py"
    ]
    
    all_exist = True
    for file_path in required_files:
        path = Path(file_path)
        if path.exists():
            print(f"[PASS] {file_path}")
        else:
            print(f"[FAIL] {file_path} - NOT FOUND")
            all_exist = False
    
    return all_exist

def test_adapter_syntax():
    """Test if adapter files have valid Python syntax"""
    print("\n" + "=" * 60)
    print("TESTING ADAPTER SYNTAX")
    print("=" * 60)
    
    from pathlib import Path
    
    adapter_files = [
        "src/adapters/tantra_bridge.py",
        "src/adapters/ttg_input_normalizer.py",
        "src/adapters/ttv_input_normalizer.py",
        "src/adapters/ttg_output_adapter.py",
        "src/adapters/ttv_output_adapter.py"
    ]
    
    all_valid = True
    for file_path in adapter_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                compile(f.read(), file_path, 'exec')
            print(f"[PASS] {file_path}")
        except SyntaxError as e:
            print(f"[FAIL] {file_path}: {e}")
            all_valid = False
        except FileNotFoundError:
            print(f"[FAIL] {file_path}: File not found")
            all_valid = False
    
    return all_valid

def test_adapter_imports():
    """Test if adapters can be imported"""
    print("\n" + "=" * 60)
    print("TESTING ADAPTER IMPORTS")
    print("=" * 60)
    
    adapters = [
        ("TTG Input Normalizer", "src.adapters.ttg_input_normalizer", "TTGInputNormalizer"),
        ("TTV Input Normalizer", "src.adapters.ttv_input_normalizer", "TTVInputNormalizer"),
        ("TTG Output Adapter", "src.adapters.ttg_output_adapter", "TTGOutputAdapter"),
        ("TTV Output Adapter", "src.adapters.ttv_output_adapter", "TTVOutputAdapter"),
        ("TANTRA Bridge", "src.adapters.tantra_bridge", "TANTRAIntegrationBridge")
    ]
    
    all_imported = True
    for name, module_path, class_name in adapters:
        try:
            module = __import__(module_path, fromlist=[class_name])
            cls = getattr(module, class_name)
            print(f"[PASS] {name}")
        except Exception as e:
            print(f"[FAIL] {name}: {e}")
            all_imported = False
    
    return all_imported

def test_adapter_instantiation():
    """Test if adapters can be instantiated"""
    print("\n" + "=" * 60)
    print("TESTING ADAPTER INSTANTIATION")
    print("=" * 60)
    
    try:
        from src.adapters.ttg_input_normalizer import TTGInputNormalizer
        from src.adapters.ttv_input_normalizer import TTVInputNormalizer
        from src.adapters.ttg_output_adapter import TTGOutputAdapter
        from src.adapters.ttv_output_adapter import TTVOutputAdapter
        from src.adapters.tantra_bridge import TANTRAIntegrationBridge
        
        tests = [
            ("TTG Input Normalizer", TTGInputNormalizer),
            ("TTV Input Normalizer", TTVInputNormalizer),
            ("TTG Output Adapter", TTGOutputAdapter),
            ("TTV Output Adapter", TTVOutputAdapter),
            ("TANTRA Bridge", TANTRAIntegrationBridge)
        ]
        
        all_instantiated = True
        for name, cls in tests:
            try:
                instance = cls()
                print(f"[PASS] {name}")
            except Exception as e:
                print(f"[FAIL] {name}: {e}")
                all_instantiated = False
        
        return all_instantiated
    except Exception as e:
        print(f"[FAIL] Import error: {e}")
        return False

def test_normalizer_logic():
    """Test normalizer logic with sample data"""
    print("\n" + "=" * 60)
    print("TESTING NORMALIZER LOGIC")
    print("=" * 60)
    
    try:
        from src.adapters.ttg_input_normalizer import TTGInputNormalizer
        from src.adapters.ttv_input_normalizer import TTVInputNormalizer
        
        # Test TTG normalizer
        ttg_norm = TTGInputNormalizer()
        ttg_input = {
            "game_type": "puzzle",
            "theme": "ancient_egypt",
            "difficulty": "medium",
            "player_count": 1,
            "description": "A puzzle game"
        }
        
        if ttg_norm.validate_ttg_input(ttg_input):
            prompt = ttg_norm.normalize(ttg_input)
            if prompt and isinstance(prompt, str):
                print(f"[PASS] TTG Normalizer - Generated prompt: {prompt[:50]}...")
            else:
                print(f"[FAIL] TTG Normalizer - Invalid prompt output")
                return False
        else:
            print(f"[FAIL] TTG Normalizer - Validation failed")
            return False
        
        # Test TTV normalizer
        ttv_norm = TTVInputNormalizer()
        ttv_input = {
            "video_type": "tutorial",
            "topic": "Python basics",
            "duration": 300,
            "style": "educational",
            "voice": "professional",
            "description": "Python tutorial"
        }
        
        if ttv_norm.validate_ttv_input(ttv_input):
            prompt = ttv_norm.normalize(ttv_input)
            if prompt and isinstance(prompt, str):
                print(f"[PASS] TTV Normalizer - Generated prompt: {prompt[:50]}...")
            else:
                print(f"[FAIL] TTV Normalizer - Invalid prompt output")
                return False
        else:
            print(f"[FAIL] TTV Normalizer - Validation failed")
            return False
        
        return True
    except Exception as e:
        print(f"[FAIL] Normalizer logic test: {e}")
        return False

def test_adapter_logic():
    """Test adapter logic with sample data"""
    print("\n" + "=" * 60)
    print("TESTING ADAPTER LOGIC")
    print("=" * 60)
    
    try:
        from src.adapters.ttg_output_adapter import TTGOutputAdapter
        from src.adapters.ttv_output_adapter import TTVOutputAdapter
        
        # Test TTG adapter
        ttg_adapter = TTGOutputAdapter()
        core_output = {
            "status": "success",
            "result": {"content": "Game content here"}
        }
        
        ttg_output = ttg_adapter.transform(core_output)
        if ttg_output and "game_content" in ttg_output:
            print(f"[PASS] TTG Adapter - Transformed output")
        else:
            print(f"[FAIL] TTG Adapter - Missing game_content")
            return False
        
        # Test TTV adapter
        ttv_adapter = TTVOutputAdapter()
        ttv_output = ttv_adapter.transform(core_output)
        if ttv_output and "video_script" in ttv_output:
            print(f"[PASS] TTV Adapter - Transformed output")
        else:
            print(f"[FAIL] TTV Adapter - Missing video_script")
            return False
        
        return True
    except Exception as e:
        print(f"[FAIL] Adapter logic test: {e}")
        return False

def main():
    """Run all validation tests"""
    print("\n" + "=" * 60)
    print("QUICK COMPONENT VALIDATION")
    print("=" * 60)
    print()
    
    results = {
        "Imports": test_imports(),
        "File Structure": test_file_structure(),
        "Adapter Syntax": test_adapter_syntax(),
        "Adapter Imports": test_adapter_imports(),
        "Adapter Instantiation": test_adapter_instantiation(),
        "Normalizer Logic": test_normalizer_logic(),
        "Adapter Logic": test_adapter_logic()
    }
    
    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)
    
    for test_name, passed in results.items():
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{status} {test_name}")
    
    all_passed = all(results.values())
    
    print("\n" + "=" * 60)
    if all_passed:
        print("[SUCCESS] All validation tests passed!")
        print("You can now start the services with: start_and_test_all.bat")
    else:
        print("[WARNING] Some validation tests failed!")
        print("Fix the issues above before starting services.")
    print("=" * 60)
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
