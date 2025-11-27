#!/usr/bin/env python3
"""
Setup script to download and configure NLP models

This script helps download and set up spaCy models and other dependencies
required for the NLP task extraction system.
"""
import sys
import subprocess
import os
from pathlib import Path


def run_command(command, description):
    """Run a shell command and handle errors"""
    print(f"\n{'=' * 70}")
    print(f"{description}")
    print(f"{'=' * 70}")
    print(f"Running: {command}\n")

    try:
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            capture_output=True,
            text=True
        )
        print(result.stdout)
        if result.stderr:
            print(result.stderr)
        print(f"\n✓ {description} - SUCCESS\n")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n✗ {description} - FAILED")
        print(f"Error: {e}")
        if e.stdout:
            print(f"Output: {e.stdout}")
        if e.stderr:
            print(f"Error output: {e.stderr}")
        return False


def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("Error: Python 3.8+ is required")
        return False

    print(f"✓ Python version {version.major}.{version.minor}.{version.micro} is compatible")
    return True


def check_spacy_installed():
    """Check if spaCy is installed"""
    try:
        import spacy
        print(f"✓ spaCy {spacy.__version__} is installed")
        return True
    except ImportError:
        print("✗ spaCy is not installed")
        return False


def download_spacy_model(model_name, language_name):
    """Download a spaCy model"""
    print(f"\nDownloading spaCy model: {model_name} ({language_name})")

    # Check if model is already installed
    try:
        import spacy
        spacy.load(model_name)
        print(f"✓ Model {model_name} is already installed")
        return True
    except OSError:
        pass

    # Download the model
    command = f"python -m spacy download {model_name}"
    return run_command(
        command,
        f"Downloading {language_name} model ({model_name})"
    )


def setup_directories():
    """Create necessary directories for models and data"""
    print("\nSetting up directories...")

    base_dir = Path(__file__).parent.parent / "app" / "ml" / "nlp_task_extractor"

    directories = [
        base_dir / "models",
        base_dir / "data" / "training",
        base_dir / "data" / "evaluation",
    ]

    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        print(f"  ✓ Created {directory}")

    return True


def verify_installation():
    """Verify that everything is set up correctly"""
    print("\n" + "=" * 70)
    print("VERIFICATION")
    print("=" * 70)

    all_good = True

    # Check spaCy
    try:
        import spacy
        print(f"✓ spaCy {spacy.__version__} is available")
    except ImportError:
        print("✗ spaCy is not available")
        all_good = False

    # Check models
    models_to_check = [
        ("fr_core_news_lg", "French Large"),
        ("en_core_web_lg", "English Large")
    ]

    for model_name, display_name in models_to_check:
        try:
            import spacy
            nlp = spacy.load(model_name)
            print(f"✓ {display_name} model ({model_name}) is ready")
        except OSError:
            print(f"⚠ {display_name} model ({model_name}) is not available (optional)")
        except ImportError:
            print(f"✗ Cannot check {model_name} - spaCy not available")
            all_good = False

    # Check transformers (optional)
    try:
        import transformers
        print(f"✓ Transformers {transformers.__version__} is available")
    except ImportError:
        print("⚠ Transformers not available (optional, for advanced features)")

    return all_good


def main():
    """Main setup routine"""
    print("\n" + "=" * 70)
    print("B2P.AI - NLP Models Setup")
    print("=" * 70)

    # Check Python version
    if not check_python_version():
        sys.exit(1)

    # Check if spaCy is installed
    if not check_spacy_installed():
        print("\nPlease install spaCy first:")
        print("  pip install spacy")
        sys.exit(1)

    # Setup directories
    if not setup_directories():
        print("\nFailed to create directories")
        sys.exit(1)

    # Download models
    print("\n" + "=" * 70)
    print("DOWNLOADING MODELS")
    print("=" * 70)

    models = [
        ("fr_core_news_lg", "French (Large)"),
        ("en_core_web_lg", "English (Large)")
    ]

    print("\nThis will download the following models:")
    for model_name, display_name in models:
        print(f"  - {display_name}: {model_name}")

    print("\nNote: These models are large (100-500 MB each).")
    print("They will be downloaded from the spaCy repository.\n")

    response = input("Do you want to continue? (y/n): ").lower().strip()
    if response != 'y':
        print("\nSetup cancelled.")
        sys.exit(0)

    # Download each model
    success_count = 0
    for model_name, display_name in models:
        if download_spacy_model(model_name, display_name):
            success_count += 1

    # If French large model failed, try French small
    if success_count == 0:
        print("\n" + "=" * 70)
        print("Trying smaller models...")
        print("=" * 70)

        fallback_models = [
            ("fr_core_news_sm", "French (Small)"),
            ("en_core_web_sm", "English (Small)")
        ]

        for model_name, display_name in fallback_models:
            if download_spacy_model(model_name, display_name):
                success_count += 1

    # Verify installation
    print("\n" + "=" * 70)
    print("FINAL VERIFICATION")
    print("=" * 70)

    if verify_installation():
        print("\n" + "=" * 70)
        print("✓ SETUP COMPLETE!")
        print("=" * 70)
        print("\nAll NLP models are set up and ready to use.")
        print("\nNext steps:")
        print("  1. Review the training data in: backend/app/ml/nlp_task_extractor/data/")
        print("  2. Train a custom model (optional):")
        print("     python -m app.ml.nlp_task_extractor.training.trainer train data/training_data_example.json")
        print("  3. Run tests:")
        print("     pytest backend/tests/test_nlp_extractor.py")
        print("  4. Start using the TaskExtractor in your code:")
        print("     from app.ml.nlp_task_extractor import TaskExtractor")
        print("     extractor = TaskExtractor()")
        print("     tasks = extractor.extract_tasks('Développer l'API REST')")
    else:
        print("\n" + "=" * 70)
        print("⚠ SETUP COMPLETED WITH WARNINGS")
        print("=" * 70)
        print("\nSome components may not be available.")
        print("The system will work with reduced functionality.")
        print("\nYou can manually install missing models with:")
        print("  python -m spacy download fr_core_news_lg")
        print("  python -m spacy download en_core_web_lg")


if __name__ == "__main__":
    main()
