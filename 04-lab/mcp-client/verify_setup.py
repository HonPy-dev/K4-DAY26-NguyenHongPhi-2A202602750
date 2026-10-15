#!/usr/bin/env python3
"""
Verification script for Weather Agent setup
Checks if all components are configured correctly
"""
import os
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

def check_environment():
    """Check if .env file exists and is configured"""
    print("[CHECK] Checking environment configuration...")
    
    env_file = Path(".env")
    if not env_file.exists():
        print("[FAIL] .env file not found")
        print("   Add DEEPSEEK_API_KEY=your_key to .env")
        return False
    
    # Check if DEEPSEEK_API_KEY is set
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key or api_key == "your_deepseek_api_key_here":
        print("[FAIL] DEEPSEEK_API_KEY not configured in .env")
        print("   Get key from: https://platform.deepseek.com/api_keys")
        return False

    print("[OK] DEEPSEEK_API_KEY configured")
    return True

def check_dependencies():
    """Check if required packages are installed"""
    print("\n[CHECK] Checking dependencies...")
    
    required_packages = [
        ("google.adk", "Google ADK"),
        ("google.genai", "Google GenAI runtime"),
        ("litellm", "LiteLLM (DeepSeek adapter)"),
        ("mcp", "MCP"),
        ("fastmcp", "FastMCP"),
        ("dotenv", "python-dotenv"),
        ("httpx", "httpx"),
    ]
    
    all_installed = True
    for package, name in required_packages:
        try:
            __import__(package)
            print(f"[OK] {name}")
        except ImportError:
            print(f"[FAIL] {name} not installed")
            all_installed = False
    
    if not all_installed:
        print("\n   Install the locked dependencies, then run this check again:")
        print("   uv sync --locked")
    
    return all_installed

def check_agent_structure():
    """Check if agent directory structure is correct"""
    print("\n[CHECK] Checking agent structure...")
    
    required_files = [
        "weather_agent/agent.py",
        "weather_agent/__init__.py",
    ]
    
    all_exist = True
    for file_path in required_files:
        path = Path(file_path)
        if path.exists():
            print(f"[OK] {file_path}")
        else:
            print(f"[FAIL] {file_path} not found")
            all_exist = False
    
    return all_exist

def check_mcp_server():
    """Check if MCP server is accessible"""
    print("\n[CHECK] Checking MCP server connectivity...")

    # Cùng URL mà weather_agent/agent.py dùng (biến môi trường MCP_SERVER_URL)
    from dotenv import load_dotenv
    load_dotenv()
    server_url = os.getenv("MCP_SERVER_URL", "http://127.0.0.1:18085/mcp")

    try:
        import httpx

        response = httpx.get(server_url, timeout=10.0)
        # GET thuần lên endpoint MCP thường bị từ chối (400/405/406) vì thiếu
        # header/session MCP — nhưng có phản hồi nghĩa là server đang chạy.
        if response.status_code < 500:
            print(f"[OK] MCP server reachable at {server_url} (HTTP {response.status_code})")
            return True
        print(f"[WARN]  MCP server returned status {response.status_code}")
        return False

    except Exception as e:
        print(f"[FAIL] Cannot reach MCP server at {server_url}: {e}")
        print("   Start it: cd ../mcp-server && uv run python weather.py")
        return False

def check_agent_import():
    """Try to import the agent"""
    print("\n[CHECK] Checking agent import...")
    
    try:
        # Suppress warnings during import
        import warnings
        warnings.filterwarnings("ignore")
        
        from weather_agent import root_agent
        print(f"[OK] Agent imported successfully: {root_agent.name}")
        print(f"   Model: {root_agent.model}")
        return True
    except Exception as e:
        print(f"[FAIL] Failed to import agent: {e}")
        return False

def main():
    """Run all verification checks"""
    print("=" * 60)
    print("Weather Agent Setup Verification")
    print("=" * 60)
    print()
    
    checks = [
        check_environment(),
        check_dependencies(),
        check_agent_structure(),
        check_mcp_server(),
        check_agent_import(),
    ]
    
    print("\n" + "=" * 60)
    if all(checks):
        print("[OK] All checks passed!")
        print("\n[READY] Ready to start!")
        print("   Run: adk web")
        print("\nOpen: http://localhost:8000")
        return 0
    else:
        print("[FAIL] Some checks failed")
        print("\n[WARN]  Fix the issues above and run this script again")
        return 1

if __name__ == "__main__":
    sys.exit(main())

