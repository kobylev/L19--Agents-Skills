"""Main application with interactive menu system."""

import sys
import shutil
from pathlib import Path
from typing import Optional
import time

from colorama import Fore, Style, init

from config.settings import settings
from src.utils.logger import setup_logger, logger
from src.services.gmail_service import GmailService
from src.services.gemini_service import GeminiService
from src.services.git_service import GitService
from src.modules.email_processor import EmailProcessor
from src.modules.repo_analyzer import RepoAnalyzer
from src.modules.feedback_generator import FeedbackGenerator
from src.modules.draft_creator import DraftCreator
from src.modules.data_manager import DataManager

# Initialize colorama
init(autoreset=True)


class HomeworkGradingSystem:
    """Main application class."""

    def __init__(self):
        """Initialize the homework grading system."""
        self.mode = None
        self.mode_limit = None

        # Initialize services (lazy loading)
        self._gmail_service = None
        self._gemini_service = None
        self._git_service = None

        # File paths
        self.file_1_2 = settings.get_output_path(settings.file_1_2_name)
        self.file_2_3 = settings.get_output_path(settings.file_2_3_name)
        self.file_3_4 = settings.get_output_path(settings.file_3_4_name)

    @property
    def gmail_service(self):
        """Lazy-load Gmail service."""
        if self._gmail_service is None:
            try:
                self._gmail_service = GmailService(
                    settings.gmail_credentials_path,
                    settings.gmail_token_path
                )
            except Exception as e:
                logger.error(f"Failed to initialize Gmail service: {e}")
                print(f"{Fore.RED}Error: Failed to connect to Gmail. Please check credentials.{Style.RESET_ALL}")
                sys.exit(1)
        return self._gmail_service

    @property
    def gemini_service(self):
        """Lazy-load Gemini service."""
        if self._gemini_service is None:
            try:
                if not settings.gemini_api_key:
                    raise ValueError("Gemini API key not configured")
                self._gemini_service = GeminiService(settings.gemini_api_key)
            except Exception as e:
                logger.error(f"Failed to initialize Gemini service: {e}")
                print(f"{Fore.RED}Error: Failed to initialize Gemini API. Please check API key.{Style.RESET_ALL}")
                sys.exit(1)
        return self._gemini_service

    def show_mode_selection_menu(self):
        """Display mode selection menu and get user choice."""
        while True:
            self.clear_screen()
            print(f"{Fore.CYAN}{'='*60}")
            print(f"{Fore.CYAN}   Homework Grading System - Mode Selection")
            print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n")

            print(f"{Fore.GREEN}1.{Style.RESET_ALL} Test Mode      - Process only the 1 most recent email")
            print(f"{Fore.GREEN}2.{Style.RESET_ALL} Batch Mode     - Process a specified number of emails")
            print(f"{Fore.GREEN}3.{Style.RESET_ALL} Full Mode      - Process all unread matching emails")
            print(f"{Fore.GREEN}4.{Style.RESET_ALL} Exit\n")

            choice = input(f"{Fore.YELLOW}Enter your choice (1-4): {Style.RESET_ALL}").strip()

            if choice == '1':
                self.mode = 'test'
                self.mode_limit = 1
                logger.info("Mode selected: Test (1 email)")
                break
            elif choice == '2':
                try:
                    count = int(input(f"{Fore.YELLOW}Enter number of emails to process (1-{settings.max_batch_size}): {Style.RESET_ALL}"))
                    if 1 <= count <= settings.max_batch_size:
                        self.mode = 'batch'
                        self.mode_limit = count
                        logger.info(f"Mode selected: Batch ({count} emails)")
                        break
                    else:
                        print(f"{Fore.RED}Invalid number. Must be between 1 and {settings.max_batch_size}{Style.RESET_ALL}")
                        input("Press Enter to continue...")
                except ValueError:
                    print(f"{Fore.RED}Invalid input. Please enter a number.{Style.RESET_ALL}")
                    input("Press Enter to continue...")
            elif choice == '3':
                self.mode = 'full'
                self.mode_limit = None
                logger.info("Mode selected: Full (all emails)")
                break
            elif choice == '4':
                print(f"{Fore.CYAN}Exiting...{Style.RESET_ALL}")
                sys.exit(0)
            else:
                print(f"{Fore.RED}Invalid choice. Please try again.{Style.RESET_ALL}")
                input("Press Enter to continue...")

    def show_main_menu(self):
        """Display main menu and get user choice."""
        while True:
            self.clear_screen()
            mode_display = f"Test" if self.mode == 'test' else f"Batch({self.mode_limit})" if self.mode == 'batch' else "Full"

            print(f"{Fore.CYAN}{'='*60}")
            print(f"{Fore.CYAN}     Homework Grading System - Main Menu")
            print(f"{Fore.CYAN}     Current Mode: {Fore.YELLOW}{mode_display}{Fore.CYAN}")
            print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n")

            print(f"{Fore.GREEN}1.{Style.RESET_ALL} Search Emails              - Execute Step 1 only")
            print(f"{Fore.GREEN}2.{Style.RESET_ALL} Clone & Grade Repositories - Execute Step 2 only")
            print(f"{Fore.GREEN}3.{Style.RESET_ALL} Generate Feedback          - Execute Step 3 only")
            print(f"{Fore.GREEN}4.{Style.RESET_ALL} Create Email Drafts        - Execute Step 4 only")
            print(f"{Fore.GREEN}5.{Style.RESET_ALL} Run All Steps (1-4)        - Execute complete workflow")
            print(f"{Fore.GREEN}6.{Style.RESET_ALL} Reset                      - Delete all generated files")
            print(f"{Fore.GREEN}7.{Style.RESET_ALL} Change Mode                - Return to mode selection")
            print(f"{Fore.GREEN}8.{Style.RESET_ALL} Exit\n")

            choice = input(f"{Fore.YELLOW}Enter your choice (1-8): {Style.RESET_ALL}").strip()

            if choice == '1':
                self.run_step_1()
            elif choice == '2':
                self.run_step_2()
            elif choice == '3':
                self.run_step_3()
            elif choice == '4':
                self.run_step_4()
            elif choice == '5':
                self.run_all_steps()
            elif choice == '6':
                self.reset()
            elif choice == '7':
                self.show_mode_selection_menu()
            elif choice == '8':
                print(f"{Fore.CYAN}Exiting...{Style.RESET_ALL}")
                sys.exit(0)
            else:
                print(f"{Fore.RED}Invalid choice. Please try again.{Style.RESET_ALL}")
                input("Press Enter to continue...")

    def run_step_1(self):
        """Execute Step 1: Email Search."""
        print(f"\n{Fore.CYAN}{'='*60}")
        print(f"{Fore.CYAN}Step 1: Searching Emails")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n")

        try:
            processor = EmailProcessor(self.gmail_service)
            result = processor.process_emails(limit=self.mode_limit)

            if result['processed'] > 0:
                processor.save_to_excel(result['data'], str(self.file_1_2))
                print(f"\n{Fore.GREEN}✓ Success: Processed {result['processed']} email(s)")
                print(f"  Output: {self.file_1_2}{Style.RESET_ALL}")
            else:
                print(f"\n{Fore.YELLOW}⚠ Warning: No matching emails found{Style.RESET_ALL}")

        except Exception as e:
            logger.error(f"Step 1 failed: {e}")
            print(f"\n{Fore.RED}✗ Error: {e}{Style.RESET_ALL}")

        input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")

    def run_step_2(self):
        """Execute Step 2: Clone and Grade Repositories."""
        print(f"\n{Fore.CYAN}{'='*60}")
        print(f"{Fore.CYAN}Step 2: Cloning and Grading Repositories")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n")

        # Check dependency
        if not self.file_1_2.exists():
            print(f"{Fore.RED}✗ Error: {self.file_1_2.name} not found. Please run Step 1 first.{Style.RESET_ALL}")
            input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
            return

        try:
            analyzer = RepoAnalyzer()
            result = analyzer.analyze_repositories(
                str(self.file_1_2),
                str(self.file_2_3),
                max_workers=settings.max_clone_workers
            )

            print(f"\n{Fore.GREEN}✓ Success: Graded {result['graded']} repository(ies)")
            if result['failed'] > 0:
                print(f"{Fore.YELLOW}⚠ Warning: {result['failed']} failed{Style.RESET_ALL}")
            print(f"{Fore.GREEN}  Output: {self.file_2_3}{Style.RESET_ALL}")

        except Exception as e:
            logger.error(f"Step 2 failed: {e}")
            print(f"\n{Fore.RED}✗ Error: {e}{Style.RESET_ALL}")

        input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")

    def run_step_3(self):
        """Execute Step 3: Generate Feedback."""
        print(f"\n{Fore.CYAN}{'='*60}")
        print(f"{Fore.CYAN}Step 3: Generating AI Feedback")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n")

        # Check dependency
        if not self.file_2_3.exists():
            print(f"{Fore.RED}✗ Error: {self.file_2_3.name} not found. Please run Step 2 first.{Style.RESET_ALL}")
            input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
            return

        try:
            generator = FeedbackGenerator(self.gemini_service)
            result = generator.generate_all_feedback(
                str(self.file_2_3),
                str(self.file_3_4)
            )

            print(f"\n{Fore.GREEN}✓ Success: Generated {result['generated']} feedback(s)")
            if result['failed'] > 0:
                print(f"{Fore.YELLOW}⚠ Warning: {result['failed']} failed{Style.RESET_ALL}")
            print(f"{Fore.GREEN}  Output: {self.file_3_4}{Style.RESET_ALL}")

        except Exception as e:
            logger.error(f"Step 3 failed: {e}")
            print(f"\n{Fore.RED}✗ Error: {e}{Style.RESET_ALL}")

        input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")

    def run_step_4(self):
        """Execute Step 4: Create Email Drafts."""
        print(f"\n{Fore.CYAN}{'='*60}")
        print(f"{Fore.CYAN}Step 4: Creating Email Drafts")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n")

        # Check dependencies
        if not self.file_3_4.exists():
            print(f"{Fore.RED}✗ Error: {self.file_3_4.name} not found. Please run Step 3 first.{Style.RESET_ALL}")
            input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
            return

        if not self.file_1_2.exists():
            print(f"{Fore.RED}✗ Error: {self.file_1_2.name} not found. Please run Step 1 first.{Style.RESET_ALL}")
            input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
            return

        try:
            creator = DraftCreator(self.gmail_service)
            result = creator.create_all_drafts(
                str(self.file_3_4),
                str(self.file_1_2),
                settings.students_mapping_file
            )

            print(f"\n{Fore.GREEN}✓ Success: Created {result['created']} draft(s)")
            if result['failed'] > 0:
                print(f"{Fore.YELLOW}⚠ Warning: {result['failed']} failed{Style.RESET_ALL}")
            print(f"{Fore.GREEN}  Check your Gmail drafts folder{Style.RESET_ALL}")

        except Exception as e:
            logger.error(f"Step 4 failed: {e}")
            print(f"\n{Fore.RED}✗ Error: {e}{Style.RESET_ALL}")

        input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")

    def run_all_steps(self):
        """Execute all steps sequentially."""
        print(f"\n{Fore.CYAN}{'='*60}")
        print(f"{Fore.CYAN}Running All Steps (Complete Workflow)")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n")

        start_time = time.time()

        try:
            # Step 1
            print(f"{Fore.CYAN}▶ Step 1: Searching emails...{Style.RESET_ALL}")
            processor = EmailProcessor(self.gmail_service)
            result1 = processor.process_emails(limit=self.mode_limit)

            if result1['processed'] == 0:
                print(f"{Fore.YELLOW}⚠ No emails found. Workflow stopped.{Style.RESET_ALL}")
                input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
                return

            processor.save_to_excel(result1['data'], str(self.file_1_2))
            print(f"{Fore.GREEN}✓ Step 1 complete: {result1['processed']} email(s) processed{Style.RESET_ALL}\n")

            # Step 2
            print(f"{Fore.CYAN}▶ Step 2: Cloning and grading repositories...{Style.RESET_ALL}")
            analyzer = RepoAnalyzer()
            result2 = analyzer.analyze_repositories(
                str(self.file_1_2),
                str(self.file_2_3),
                max_workers=settings.max_clone_workers
            )
            print(f"{Fore.GREEN}✓ Step 2 complete: {result2['graded']} repository(ies) graded{Style.RESET_ALL}\n")

            # Step 3
            print(f"{Fore.CYAN}▶ Step 3: Generating AI feedback...{Style.RESET_ALL}")
            generator = FeedbackGenerator(self.gemini_service)
            result3 = generator.generate_all_feedback(
                str(self.file_2_3),
                str(self.file_3_4)
            )
            print(f"{Fore.GREEN}✓ Step 3 complete: {result3['generated']} feedback(s) generated{Style.RESET_ALL}\n")

            # Step 4
            print(f"{Fore.CYAN}▶ Step 4: Creating email drafts...{Style.RESET_ALL}")
            creator = DraftCreator(self.gmail_service)
            result4 = creator.create_all_drafts(
                str(self.file_3_4),
                str(self.file_1_2),
                settings.students_mapping_file
            )
            print(f"{Fore.GREEN}✓ Step 4 complete: {result4['created']} draft(s) created{Style.RESET_ALL}\n")

            # Summary
            elapsed = time.time() - start_time
            minutes = int(elapsed // 60)
            seconds = int(elapsed % 60)

            print(f"\n{Fore.CYAN}{'='*60}")
            print(f"{Fore.CYAN}         Workflow Completion Summary")
            print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n")

            mode_display = f"Test" if self.mode == 'test' else f"Batch({self.mode_limit})" if self.mode == 'batch' else "Full"
            print(f"{Fore.YELLOW}Mode:{Style.RESET_ALL} {mode_display}")
            print(f"{Fore.YELLOW}Execution Time:{Style.RESET_ALL} {minutes}m {seconds}s\n")

            print(f"{Fore.GREEN}✓ Step 1 - Email Search:        {result1['processed']} email(s) processed")
            print(f"✓ Step 2 - Clone & Grade:       {result2['graded']} repository analyzed")
            print(f"✓ Step 3 - Generate Feedback:   {result3['generated']} feedback generated")
            print(f"✓ Step 4 - Create Drafts:       {result4['created']} draft created{Style.RESET_ALL}\n")

            print(f"{Fore.CYAN}Files Created:")
            print(f"  - {self.file_1_2}")
            print(f"  - {self.file_2_3}")
            print(f"  - {self.file_3_4}{Style.RESET_ALL}\n")

            print(f"{Fore.GREEN}Drafts: Check your Gmail drafts folder{Style.RESET_ALL}")

        except Exception as e:
            logger.error(f"Workflow failed: {e}")
            print(f"\n{Fore.RED}✗ Workflow failed: {e}{Style.RESET_ALL}")

        input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")

    def reset(self):
        """Delete all generated files."""
        print(f"\n{Fore.CYAN}{'='*60}")
        print(f"{Fore.CYAN}              Reset Confirmation")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n")

        print("This will delete the following:\n")

        files_to_delete = [
            self.file_1_2,
            self.file_2_3,
            self.file_3_4
        ]

        for file_path in files_to_delete:
            if file_path.exists():
                print(f"{Fore.GREEN}✓ {file_path.name} (exists){Style.RESET_ALL}")
            else:
                print(f"{Fore.YELLOW}✗ {file_path.name} (not found){Style.RESET_ALL}")

        repos_dir = Path(settings.temp_dir) / 'homework_repos'
        if repos_dir.exists():
            print(f"{Fore.GREEN}✓ Cloned repositories in {repos_dir}{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}✗ Cloned repositories (not found){Style.RESET_ALL}")

        confirmation = input(f"\n{Fore.RED}Are you sure you want to continue? (yes/no): {Style.RESET_ALL}").strip().lower()

        if confirmation == 'yes':
            print(f"\n{Fore.CYAN}Deleting files...{Style.RESET_ALL}\n")

            # Delete Excel files
            for file_path in files_to_delete:
                if file_path.exists():
                    try:
                        file_path.unlink()
                        print(f"{Fore.GREEN}✓ Deleted: {file_path.name}{Style.RESET_ALL}")
                    except Exception as e:
                        print(f"{Fore.RED}✗ Failed to delete {file_path.name}: {e}{Style.RESET_ALL}")

            # Delete repositories directory
            if repos_dir.exists():
                try:
                    shutil.rmtree(repos_dir)
                    print(f"{Fore.GREEN}✓ Deleted: Cloned repositories{Style.RESET_ALL}")
                except Exception as e:
                    print(f"{Fore.RED}✗ Failed to delete repositories: {e}{Style.RESET_ALL}")

            print(f"\n{Fore.GREEN}Reset complete!{Style.RESET_ALL}")
        else:
            print(f"\n{Fore.YELLOW}Reset cancelled.{Style.RESET_ALL}")

        input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")

    @staticmethod
    def clear_screen():
        """Clear the terminal screen."""
        import os
        os.system('cls' if os.name == 'nt' else 'clear')


def main():
    """Main entry point."""
    try:
        # Setup logger
        setup_logger(log_level=settings.log_level)

        # Create application instance
        app = HomeworkGradingSystem()

        # Show mode selection
        app.show_mode_selection_menu()

        # Show main menu
        app.show_main_menu()

    except KeyboardInterrupt:
        print(f"\n\n{Fore.CYAN}Interrupted by user. Exiting...{Style.RESET_ALL}")
        sys.exit(0)
    except Exception as e:
        logger.critical(f"Application error: {e}", exc_info=True)
        print(f"\n{Fore.RED}Critical error: {e}{Style.RESET_ALL}")
        sys.exit(1)


if __name__ == "__main__":
    main()
