"""
Example usage of the NLP Task Extractor

This file contains practical examples demonstrating various features
of the task extraction system.
"""

from datetime import datetime
from pathlib import Path
from typing import List

from .extractor import TaskExtractor, TaskEntity
from .config import NLPConfig


def example_1_basic_extraction():
    """Example 1: Basic task extraction from text"""
    print("\n" + "=" * 70)
    print("EXAMPLE 1: Basic Task Extraction")
    print("=" * 70)

    # Initialize extractor
    extractor = TaskExtractor()

    # Simple text
    text = "Développer l'API REST pour le module de facturation avant vendredi"

    # Extract tasks
    tasks = extractor.extract_tasks(text)

    # Display results
    print(f"\nInput text: {text}\n")
    print(f"Extracted {len(tasks)} task(s):\n")

    for i, task in enumerate(tasks, 1):
        print(f"Task {i}:")
        print(f"  Text: {task.text}")
        print(f"  Action: {task.action}")
        print(f"  Object: {task.object}")
        print(f"  Urgency: {task.urgency}/5")
        print(f"  Deadline: {task.deadline}")
        print(f"  Confidence: {task.confidence:.2%}")
        print()


def example_2_email_extraction():
    """Example 2: Extract tasks from email"""
    print("\n" + "=" * 70)
    print("EXAMPLE 2: Email Task Extraction")
    print("=" * 70)

    extractor = TaskExtractor()

    email = """
    Subject: Action Items - Client Meeting

    Bonjour l'équipe,

    Suite à la réunion client de ce matin, voici les actions à réaliser :

    - Développer l'API REST pour le module de facturation urgent
    - Préparer la présentation pour la démo client avant jeudi
    - Contacter le support technique pour résoudre le bug critique
    - Mettre à jour la documentation utilisateur

    Merci de confirmer la prise en compte de ces tâches.

    Cordialement,
    """

    tasks = extractor.extract_tasks(email, source_type="email")

    print(f"\nExtracted {len(tasks)} task(s) from email:\n")

    for task in tasks:
        print(f"✓ {task.text}")
        print(f"  Priority: {'🔴' if task.urgency >= 4 else '🟡' if task.urgency == 3 else '🟢'} {task.urgency}/5")
        if task.deadline:
            print(f"  Deadline: {task.deadline.strftime('%Y-%m-%d')}")
        print(f"  Effort: ~{task.estimated_effort:.1f}h")
        print()


def example_3_meeting_notes():
    """Example 3: Extract from meeting notes with assignees"""
    print("\n" + "=" * 70)
    print("EXAMPLE 3: Meeting Notes Extraction")
    print("=" * 70)

    extractor = TaskExtractor()

    meeting_notes = """
    Sprint Planning Meeting - 2024-12-18

    Attendees: Jean, Marie, Pierre, Sophie

    Action Items:
    1. Jean doit développer la nouvelle feature d'authentification JWT urgent
    2. Marie va tester l'intégration avec l'API de paiement cette semaine
    3. Pierre doit mettre à jour la documentation technique avant vendredi
    4. Sophie va créer les maquettes UI pour le tableau de bord

    Next meeting: Friday 10:00 AM
    """

    tasks = extractor.extract_tasks(meeting_notes, source_type="meeting")

    print(f"\nExtracted {len(tasks)} action item(s):\n")

    for task in tasks:
        assignee = f" ({task.assignee})" if task.assignee else ""
        print(f"• {task.text}{assignee}")
        if task.deadline:
            days_until = (task.deadline - datetime.now()).days
            print(f"  ⏰ Due in {days_until} days")
        print()


def example_4_custom_config():
    """Example 4: Using custom configuration"""
    print("\n" + "=" * 70)
    print("EXAMPLE 4: Custom Configuration")
    print("=" * 70)

    # Create custom config
    config = NLPConfig(
        min_confidence=0.8,      # Higher confidence threshold
        max_task_length=150,      # Shorter task descriptions
        min_task_words=5,         # Longer minimum length
        enable_caching=True,      # Enable caching
        cache_size=50             # Smaller cache
    )

    extractor = TaskExtractor(config=config)

    text = """
    Tasks for today:
    - Quick email to client
    - Develop comprehensive API documentation with examples and use cases
    - Test new features
    """

    tasks = extractor.extract_tasks(text)

    print("\nWith strict configuration:")
    print(f"  min_confidence: {config.min_confidence}")
    print(f"  min_task_words: {config.min_task_words}")
    print(f"\nExtracted {len(tasks)} high-confidence task(s):\n")

    for task in tasks:
        print(f"✓ {task.text} (confidence: {task.confidence:.2%})")


def example_5_filtering_tasks():
    """Example 5: Filtering and sorting extracted tasks"""
    print("\n" + "=" * 70)
    print("EXAMPLE 5: Filtering and Sorting Tasks")
    print("=" * 70)

    extractor = TaskExtractor()

    text = """
    Project tasks:
    - Fix critical security vulnerability asap
    - Update documentation when possible
    - Implement new payment gateway important
    - Refactor legacy code
    - Deploy to production this week urgent
    """

    tasks = extractor.extract_tasks(text)

    print(f"\nExtracted {len(tasks)} total tasks\n")

    # Filter urgent tasks
    urgent_tasks = [t for t in tasks if t.urgency >= 4]
    print(f"Urgent tasks ({len(urgent_tasks)}):")
    for task in urgent_tasks:
        print(f"  🔴 {task.text}")

    # Filter tasks with deadlines
    deadline_tasks = [t for t in tasks if t.deadline is not None]
    print(f"\nTasks with deadlines ({len(deadline_tasks)}):")
    for task in sorted(deadline_tasks, key=lambda t: t.deadline):
        print(f"  📅 {task.text} - Due: {task.deadline.strftime('%Y-%m-%d')}")

    # High confidence tasks
    reliable_tasks = [t for t in tasks if t.confidence >= 0.8]
    print(f"\nHigh-confidence tasks ({len(reliable_tasks)}):")
    for task in reliable_tasks:
        print(f"  ✓ {task.text} ({task.confidence:.0%})")


def example_6_multilingual():
    """Example 6: Mixed French and English text"""
    print("\n" + "=" * 70)
    print("EXAMPLE 6: Multilingual Support")
    print("=" * 70)

    config = NLPConfig(support_multilingual=True)
    extractor = TaskExtractor(config=config)

    text = """
    Sprint tasks:
    - Développer l'API REST endpoint
    - Create the user documentation
    - Tester les nouvelles fonctionnalités
    - Review the pull request #234
    - Déployer sur le serveur de staging
    """

    tasks = extractor.extract_tasks(text)

    print(f"\nExtracted {len(tasks)} task(s) from mixed FR/EN text:\n")

    for task in tasks:
        # Detect language (simple heuristic)
        lang = "🇫🇷" if any(word in task.text.lower() for word in ["l'", "le", "la", "les"]) else "🇬🇧"
        print(f"{lang} {task.text}")


def example_7_stats_and_cache():
    """Example 7: Using statistics and caching"""
    print("\n" + "=" * 70)
    print("EXAMPLE 7: Statistics and Caching")
    print("=" * 70)

    config = NLPConfig(enable_caching=True)
    extractor = TaskExtractor(config=config)

    # Get initial stats
    stats = extractor.get_stats()
    print("Initial statistics:")
    print(f"  spaCy available: {stats['spacy_available']}")
    print(f"  Model loaded: {stats['model_loaded']}")
    print(f"  Cache size: {stats['cache_size']}")

    # Extract tasks (will be cached)
    text = "Développer l'API REST"
    tasks1 = extractor.extract_tasks(text)

    # Extract again (uses cache)
    tasks2 = extractor.extract_tasks(text)

    # Check cache
    stats = extractor.get_stats()
    print(f"\nAfter extraction:")
    print(f"  Cache size: {stats['cache_size']}")
    print(f"  Cache hit: {len(tasks1) == len(tasks2)}")

    # Clear cache
    extractor.clear_cache()
    stats = extractor.get_stats()
    print(f"\nAfter clearing cache:")
    print(f"  Cache size: {stats['cache_size']}")


def example_8_batch_processing():
    """Example 8: Batch processing multiple texts"""
    print("\n" + "=" * 70)
    print("EXAMPLE 8: Batch Processing")
    print("=" * 70)

    extractor = TaskExtractor()

    # Multiple emails/texts
    texts = [
        "Développer l'API REST urgent",
        "Tester les nouvelles fonctionnalités cette semaine",
        "Préparer la présentation client avant vendredi",
        "Contacter le support technique",
        "Mettre à jour la documentation"
    ]

    print(f"Processing {len(texts)} texts...\n")

    all_tasks = []
    for i, text in enumerate(texts, 1):
        tasks = extractor.extract_tasks(text)
        all_tasks.extend(tasks)
        print(f"Text {i}: {len(tasks)} task(s) extracted")

    print(f"\nTotal: {len(all_tasks)} tasks extracted")

    # Aggregate statistics
    urgent_count = sum(1 for t in all_tasks if t.urgency >= 4)
    with_deadline = sum(1 for t in all_tasks if t.deadline)
    avg_confidence = sum(t.confidence for t in all_tasks) / len(all_tasks)

    print(f"\nStatistics:")
    print(f"  Urgent tasks: {urgent_count}")
    print(f"  With deadlines: {with_deadline}")
    print(f"  Average confidence: {avg_confidence:.2%}")


def example_9_error_handling():
    """Example 9: Handling edge cases and errors"""
    print("\n" + "=" * 70)
    print("EXAMPLE 9: Error Handling")
    print("=" * 70)

    extractor = TaskExtractor()

    # Test various edge cases
    test_cases = [
        ("", "Empty string"),
        ("   ", "Whitespace only"),
        ("Hello", "Too short"),
        ("What should we do?", "Question"),
        ("This is just information", "No action verb"),
        ("Développer développer développer" * 50, "Very long text"),
    ]

    print("\nTesting edge cases:\n")

    for text, description in test_cases:
        tasks = extractor.extract_tasks(text)
        status = "✓ OK" if len(tasks) == 0 else f"⚠ {len(tasks)} task(s) extracted"
        print(f"{description:30s} → {status}")


def run_all_examples():
    """Run all examples"""
    print("\n" + "=" * 70)
    print("NLP TASK EXTRACTOR - EXAMPLES")
    print("=" * 70)

    examples = [
        example_1_basic_extraction,
        example_2_email_extraction,
        example_3_meeting_notes,
        example_4_custom_config,
        example_5_filtering_tasks,
        example_6_multilingual,
        example_7_stats_and_cache,
        example_8_batch_processing,
        example_9_error_handling,
    ]

    for example in examples:
        try:
            example()
        except Exception as e:
            print(f"\n❌ Error in {example.__name__}: {e}")

    print("\n" + "=" * 70)
    print("ALL EXAMPLES COMPLETED")
    print("=" * 70)


if __name__ == "__main__":
    # Run all examples
    run_all_examples()

    # Or run individual examples:
    # example_1_basic_extraction()
    # example_2_email_extraction()
    # etc.
