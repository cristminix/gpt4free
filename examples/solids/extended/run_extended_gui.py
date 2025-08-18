"""
Custom web interface to run the GUI with extended providers.
"""
from g4f.gui import run_gui

# The extended provider is automatically registered when the backend API is imported
# You can now use "ExtendedLMArenaBeta" as a provider name in the GUI

if __name__ == "__main__":
    print("Starting GUI with extended providers...")
    print("You can now select 'ExtendedLMArenaBeta' as a provider in the GUI")
    run_gui(port=7000)