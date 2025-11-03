"""Centralized logging configuration for Bills of Mortality processing."""

import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

from loguru import logger


def setup_logging(
    log_level: str = "INFO",
    log_dir: Optional[Path] = None,
    log_name: Optional[str] = None,
    console_output: bool = True,
) -> Path:
    """
    Set up structured logging for the processing pipeline.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_dir: Directory for log files (defaults to logs/)
        log_name: Base name for log files (defaults to timestamp)
        console_output: Whether to also output to console

    Returns:
        Path to the main log file
    """
    # Remove default logger
    logger.remove()

    # Set up log directory
    if log_dir is None:
        log_dir = Path.cwd() / "logs"
    log_dir.mkdir(exist_ok=True)

    # Generate log file name
    if log_name is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_name = f"bom_processing_{timestamp}"

    # Main log file
    main_log_file = log_dir / f"{log_name}.log"

    # Error log file
    error_log_file = log_dir / f"{log_name}_errors.log"

    # Configure loguru formats
    detailed_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )

    simple_format = (
        "<green>{time:HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<level>{message}</level>"
    )

    # Add console handler if requested
    if console_output:
        logger.add(
            sys.stderr,
            format=simple_format,
            level=log_level,
            colorize=True,
            backtrace=False,
            diagnose=False,
        )

    # Add main log file handler
    logger.add(
        main_log_file,
        format=detailed_format,
        level=log_level,
        rotation="10 MB",
        retention="30 days",
        compression="gz",
        backtrace=True,
        diagnose=True,
    )

    # Add error log file handler (only errors and critical)
    logger.add(
        error_log_file,
        format=detailed_format,
        level="ERROR",
        rotation="5 MB",
        retention="60 days",
        compression="gz",
        backtrace=True,
        diagnose=True,
    )

    # Log setup completion
    logger.info(f"Logging initialized - Main log: {main_log_file}")
    logger.info(f"Error log: {error_log_file}")

    return main_log_file


def setup_component_logging(component_name: str, log_level: str = "INFO") -> Path:
    """
    Set up logging for a specific component (e.g., 'bills_processor', 'schema_test').

    Args:
        component_name: Name of the component for log file naming
        log_level: Logging level

    Returns:
        Path to the component log file
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_name = f"{component_name}_{timestamp}"

    return setup_logging(log_level=log_level, log_name=log_name, console_output=True)


def log_processing_summary(
    input_files: int,
    input_rows: int,
    output_records: dict,
    processing_time: float,
    errors: int = 0,
):
    """Log a comprehensive processing summary."""
    logger.info("=" * 60)
    logger.info("PROCESSING SUMMARY")
    logger.info("=" * 60)
    logger.info(f"📊 Input: {input_files} files, {input_rows:,} rows")

    total_output = sum(output_records.values())
    logger.info(f"📈 Output: {total_output:,} total records")

    for table, count in output_records.items():
        logger.info(f"   • {table}: {count:,} records")

    logger.info(f"⏱️  Processing time: {processing_time:.2f} seconds")
    logger.info(f"🚀 Processing rate: {input_rows/processing_time:.0f} rows/second")

    if errors > 0:
        logger.warning(f"⚠️  Errors encountered: {errors}")
    else:
        logger.success("✅ Processing completed without errors")

    logger.info("=" * 60)


def log_validation_results(
    component: str,
    total_records: int,
    valid_records: int,
    validation_errors: list = None,
):
    """Log validation results for a component."""
    success_rate = (valid_records / total_records * 100) if total_records > 0 else 0

    logger.info(f"🔍 {component} Validation Results:")
    logger.info(f"   • Total records: {total_records:,}")
    logger.info(f"   • Valid records: {valid_records:,}")
    logger.info(f"   • Success rate: {success_rate:.1f}%")

    if validation_errors:
        logger.warning(f"   • Validation errors: {len(validation_errors)}")
        for error in validation_errors[:5]:  # Log first 5 errors
            logger.warning(f"     - {error}")
        if len(validation_errors) > 5:
            logger.warning(f"     ... and {len(validation_errors) - 5} more errors")


def log_data_quality_metrics(
    dataset_name: str,
    shape: tuple,
    null_counts: dict = None,
    unique_counts: dict = None,
    data_types: dict = None,
):
    """Log data quality metrics for a dataset."""
    logger.info(f"📋 Data Quality - {dataset_name}:")
    logger.info(f"   • Shape: {shape[0]:,} rows × {shape[1]} columns")

    if null_counts:
        high_null_cols = {k: v for k, v in null_counts.items() if v > 0}
        if high_null_cols:
            logger.info(f"   • Columns with null values: {len(high_null_cols)}")
            for col, nulls in list(high_null_cols.items())[:3]:
                pct = nulls / shape[0] * 100
                logger.info(f"     - {col}: {nulls:,} nulls ({pct:.1f}%)")
        else:
            logger.info("   • No null values found")

    if unique_counts:
        logger.info("   • Unique value counts (sample):")
        for col, unique in list(unique_counts.items())[:3]:
            logger.info(f"     - {col}: {unique:,} unique values")

    if data_types:
        type_summary = {}
        for dtype in data_types.values():
            type_summary[str(dtype)] = type_summary.get(str(dtype), 0) + 1
        logger.info(f"   • Data types: {dict(type_summary)}")


class LoggingContext:
    """Context manager for component-specific logging."""

    def __init__(self, component_name: str, log_level: str = "INFO"):
        self.component_name = component_name
        self.log_level = log_level
        self.log_file = None
        self.start_time = None

    def __enter__(self):
        self.start_time = datetime.now()
        self.log_file = setup_component_logging(self.component_name, self.log_level)
        logger.info(f"🚀 Starting {self.component_name}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()

        if exc_type is None:
            logger.success(
                f"✅ {self.component_name} completed successfully in {duration:.2f}s"
            )
        else:
            logger.error(
                f"❌ {self.component_name} failed after {duration:.2f}s: {exc_val}"
            )

        return False  # Don't suppress exceptions
