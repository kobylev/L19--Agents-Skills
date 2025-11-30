"""Repository analysis module - Step 2."""

from pathlib import Path
from typing import List, Dict, Tuple
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

from src.services.git_service import GitService
from src.modules.data_manager import DataManager
from src.utils.logger import logger
from config.settings import settings


class RepoAnalyzer:
    """Handles repository cloning and analysis - Step 2."""

    def __init__(self):
        """Initialize repository analyzer."""
        self.git_service = GitService()
        self.data_manager = DataManager()

    def analyze_repositories(self, input_file: str, output_file: str, max_workers: int = 5):
        """
        Analyze repositories from input file.

        Args:
            input_file: Path to file_1_2.xlsx
            output_file: Path to file_2_3.xlsx
            max_workers: Number of concurrent workers
        """
        try:
            logger.info(f"Starting repository analysis (max_workers: {max_workers})")

            # Read input file
            df = self.data_manager.read_from_excel(input_file)

            # Filter rows with status='Ready'
            ready_df = self.data_manager.filter_ready_rows(df)

            if ready_df.empty:
                logger.warning("No 'Ready' rows found in input file")
                self.data_manager.write_to_excel([], output_file)
                return {'graded': 0, 'failed': 0}

            repos = ready_df.to_dict('records')
            logger.info(f"Processing {len(repos)} repositories")

            # Clone and analyze in parallel
            results = self._clone_and_analyze_parallel(repos, max_workers)

            # Save results
            self.data_manager.write_to_excel(results['data'], output_file)

            logger.info(f"Repository analysis complete: {results['successful']} graded, {results['failed']} failed")

            return {
                'graded': results['successful'],
                'failed': results['failed']
            }

        except Exception as e:
            logger.error(f"Repository analysis failed: {e}")
            raise

    def _clone_and_analyze_parallel(self, repos: List[Dict], max_workers: int) -> Dict:
        """
        Clone and analyze repositories in parallel.

        Args:
            repos: List of repository data
            max_workers: Number of concurrent workers

        Returns:
            Dictionary with results
        """
        results = {
            'successful': 0,
            'failed': 0,
            'data': []
        }

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_repo = {
                executor.submit(self._clone_and_analyze_single, repo): repo
                for repo in repos
            }

            # Process completed tasks
            for future in as_completed(future_to_repo):
                repo = future_to_repo[future]
                try:
                    result = future.result()
                    results['data'].append(result)
                    if result['grade'] is not None:
                        results['successful'] += 1
                    else:
                        results['failed'] += 1

                except Exception as e:
                    logger.error(f"Failed to process {repo['email_id']}: {e}")
                    results['failed'] += 1
                    results['data'].append({
                        'email_id': repo['email_id'],
                        'grade': None,
                        'status': 'Missing: grade'
                    })

        return results

    def _clone_and_analyze_single(self, repo: Dict) -> Dict:
        """
        Clone and analyze a single repository.

        Args:
            repo: Repository data dictionary

        Returns:
            Analysis result dictionary
        """
        thread_id = threading.get_ident()
        email_id = repo['email_id']
        repo_url = repo['repo_url']

        logger.debug(f"[Thread {thread_id}] Processing {email_id}")

        try:
            # Create target directory
            target_dir = Path(settings.temp_dir) / 'homework_repos' / email_id
            target_dir.mkdir(parents=True, exist_ok=True)

            # Clone repository
            logger.debug(f"[Thread {thread_id}] Cloning {repo_url}")
            self.git_service.clone_repository(
                repo_url,
                str(target_dir),
                timeout=settings.clone_timeout
            )

            # Analyze Python files
            python_files = self.find_python_files(target_dir)
            logger.debug(f"[Thread {thread_id}] Found {len(python_files)} Python files")

            if not python_files:
                logger.warning(f"[Thread {thread_id}] No Python files found in {repo_url}")
                grade = 0.0
            else:
                grade = self.calculate_grade(python_files)
                logger.debug(f"[Thread {thread_id}] Calculated grade: {grade:.2f}")

            return {
                'email_id': email_id,
                'grade': round(grade, 2),
                'status': 'Ready'
            }

        except Exception as e:
            logger.error(f"[Thread {thread_id}] Error analyzing {email_id}: {e}")
            return {
                'email_id': email_id,
                'grade': None,
                'status': 'Missing: grade'
            }

    def find_python_files(self, directory: Path) -> List[Path]:
        """
        Find all Python files in directory.

        Args:
            directory: Directory to search

        Returns:
            List of Python file paths
        """
        exclude_dirs = {'__pycache__', '.venv', 'venv', 'env', '.git', 'node_modules'}

        python_files = []
        for py_file in directory.rglob('*.py'):
            # Check if any parent directory is in exclude list
            if not any(excluded in py_file.parts for excluded in exclude_dirs):
                python_files.append(py_file)

        return python_files

    def count_lines(self, file_path: Path) -> int:
        """
        Count non-blank, non-comment lines in a Python file.

        Args:
            file_path: Path to Python file

        Returns:
            Number of lines
        """
        count = 0
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    stripped = line.strip()
                    # Count lines that are not empty and not comments
                    if stripped and not stripped.startswith('#'):
                        count += 1
        except Exception as e:
            logger.warning(f"Error reading {file_path}: {e}")

        return count

    def calculate_grade(self, python_files: List[Path]) -> float:
        """
        Calculate grade based on file line counts.

        Grade = (sum of lines in files >150 lines) / (total lines) * 100

        Args:
            python_files: List of Python file paths

        Returns:
            Grade (0-100)
        """
        total_lines = 0
        large_files_lines = 0

        for py_file in python_files:
            line_count = self.count_lines(py_file)
            total_lines += line_count

            if line_count > 150:
                large_files_lines += line_count
                logger.debug(f"Large file: {py_file.name} ({line_count} lines)")

        if total_lines == 0:
            return 0.0

        grade = (large_files_lines / total_lines) * 100
        logger.debug(f"Grade calculation: {large_files_lines}/{total_lines} = {grade:.2f}%")

        return grade
