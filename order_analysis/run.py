from config import (
    DATA_DIR,
    REPORT_FILE,
    LOG_FILE,
    STATUS_COLUMN,
    DELIVERED_STATUS,
    AMOUNT_COLUMN,
    REQUIRED_COLUMNS,
    CSV_ENCODING,
)
from src.analyzer import OrderAnalyzer


def main():
    analyzer = OrderAnalyzer(
        data_dir=DATA_DIR,
        report_file=REPORT_FILE,
        log_file=LOG_FILE,
        status_column=STATUS_COLUMN,
        delivered_status=DELIVERED_STATUS,
        amount_column=AMOUNT_COLUMN,
        required_columns=REQUIRED_COLUMNS,
        encoding=CSV_ENCODING,
    )
    analyzer.process_all_files()


if __name__ == "__main__":
    main()
