# run.py
import sys

print("--- Starting TradeGuide AI ---")

try:
    from app import create_app
    print("1. Importing App Factory... OK")
except Exception as e:
    print(f"!!! Error importing app: {e}")
    sys.exit(1)

try:
    app = create_app()
    print("2. App Instance Created... OK")
except Exception as e:
    print(f"!!! Error creating app: {e}")
    sys.exit(1)

if __name__ == '__main__':
    print("3. Starting Server on http://127.0.0.1:5000 ...")
    # Debug=True allows you to see errors in the browser
    app.run(debug=True)