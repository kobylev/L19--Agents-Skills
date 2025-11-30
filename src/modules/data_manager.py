"""Data manager for Excel file operations."""

from pathlib import Path
from typing import List, Dict, Any
import pandas as pd
from openpyxl import Workbook, load_workbook

from src.utils.logger import logger


class DataManager:
    """Manages Excel file operations."""

    @staticmethod
    def write_to_excel(data: List[Dict[str, Any]], output_path: str, sheet_name: str = 'Data'):
        """
        Write data to Excel file.

        Args:
            data: List of dictionaries to write
            output_path: Output file path
            sheet_name: Sheet name
        """
        try:
            if not data:
                logger.warning(f"No data to write to {output_path}")
                # Create empty file with headers
                df = pd.DataFrame()
            else:
                df = pd.DataFrame(data)

            # Ensure output directory exists
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)

            # Write to Excel
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name=sheet_name)

            logger.info(f"Wrote {len(data)} row(s) to {output_path}")

        except Exception as e:
            logger.error(f"Failed to write Excel file {output_path}: {e}")
            raise

    @staticmethod
    def read_from_excel(input_path: str, sheet_name: str = 'Data') -> pd.DataFrame:
        """
        Read data from Excel file.

        Args:
            input_path: Input file path
            sheet_name: Sheet name

        Returns:
            DataFrame with data
        """
        try:
            if not Path(input_path).exists():
                raise FileNotFoundError(f"File not found: {input_path}")

            df = pd.read_excel(input_path, sheet_name=sheet_name)
            logger.debug(f"Read {len(df)} row(s) from {input_path}")
            return df

        except Exception as e:
            logger.error(f"Failed to read Excel file {input_path}: {e}")
            raise

    @staticmethod
    def filter_ready_rows(df: pd.DataFrame) -> pd.DataFrame:
        """
        Filter rows with status='Ready'.

        Args:
            df: DataFrame to filter

        Returns:
            Filtered DataFrame
        """
        if 'status' not in df.columns:
            logger.warning("No 'status' column found in DataFrame")
            return df

        ready_df = df[df['status'] == 'Ready'].copy()
        logger.debug(f"Filtered {len(ready_df)} 'Ready' rows from {len(df)} total rows")
        return ready_df

    @staticmethod
    def delete_file(file_path: str) -> bool:
        """
        Delete a file.

        Args:
            file_path: Path to file to delete

        Returns:
            True if successful, False otherwise
        """
        try:
            path = Path(file_path)
            if path.exists():
                path.unlink()
                logger.info(f"Deleted: {file_path}")
                return True
            else:
                logger.debug(f"File not found: {file_path}")
                return False
        except Exception as e:
            logger.error(f"Failed to delete {file_path}: {e}")
            return False

    @staticmethod
    def load_student_mapping(mapping_file: str) -> Dict[str, str]:
        """
        Load student email to name mapping.

        Args:
            mapping_file: Path to students_mapping.xlsx

        Returns:
            Dictionary mapping email to name
        """
        try:
            if not Path(mapping_file).exists():
                logger.warning(f"Student mapping file not found: {mapping_file}")
                return {}

            df = pd.read_excel(mapping_file)

            if 'email_address' not in df.columns or 'name' not in df.columns:
                logger.error("Student mapping file must have 'email_address' and 'name' columns")
                return {}

            # Create mapping (lowercase emails for case-insensitive matching)
            mapping = {
                str(row['email_address']).strip().lower(): str(row['name']).strip()
                for _, row in df.iterrows()
            }

            logger.info(f"Loaded {len(mapping)} student name mappings")
            return mapping

        except Exception as e:
            logger.error(f"Failed to load student mapping: {e}")
            return {}
