from pathlib import Path

# Корневая папка проекта
BASE_DIR = Path(__file__).resolve().parent

# Пути проекта
DATA_DIR = BASE_DIR / "data"
REPORTS_DIR = BASE_DIR / "reports"
LOGS_DIR = BASE_DIR / "logs"

# Выходные файлы
REPORT_FILE = REPORTS_DIR / "summary_report.csv"
LOG_FILE = LOGS_DIR / "errors.log"

# Настройки анализа
STATUS_COLUMN = "status"
DELIVERED_STATUS = "Delivered"
AMOUNT_COLUMN = "total_amount"

# Обязательные столбцы для расчёта
REQUIRED_COLUMNS = {
    "order_id",
    "person_id",
    "order_date",
    "status",
    "total_amount",
    "currency",
    "payment_method",
    "shipping_method",
    "notes",
}

# Кодировка итогового CSV
CSV_ENCODING = "utf-8-sig"
