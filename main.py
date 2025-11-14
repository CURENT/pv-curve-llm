#!/usr/bin/env python3
import sys

if __name__ == "__main__":
    try:
        from cli import run_cli
        run_cli()
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nUsage:")
        print("  python main.py          # Run CLI")
