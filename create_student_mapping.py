"""Helper script to create students_mapping.xlsx file."""

import pandas as pd
from pathlib import Path

def create_student_mapping_example():
    """Create example students_mapping.xlsx file."""

    # Example student data
    students = [
        {"email_address": "student1@university.edu", "name": "Alex Johnson"},
        {"email_address": "student2@university.edu", "name": "Maria Garcia"},
        {"email_address": "student3@university.edu", "name": "John Smith"},
        {"email_address": "student4@university.edu", "name": "Emma Wilson"},
        {"email_address": "student5@university.edu", "name": "David Lee"},
    ]

    # Create DataFrame
    df = pd.DataFrame(students)

    # Ensure data directory exists
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)

    # Save to Excel
    output_file = data_dir / "students_mapping.xlsx"
    df.to_excel(output_file, index=False, sheet_name="Students")

    print(f"✓ Created: {output_file}")
    print(f"  Added {len(students)} example students")
    print("\nPlease edit this file with your actual student data:")
    print("  - Replace example emails with real student emails")
    print("  - Replace example names with real student names")
    print("  - Add more rows as needed")
    print("\nEmail addresses must match the sender addresses of homework emails.")


if __name__ == "__main__":
    create_student_mapping_example()
