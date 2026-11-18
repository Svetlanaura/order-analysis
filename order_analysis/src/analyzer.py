import logging
from pathlib import Path

import pandas as pd


class OrderAnalyzer:
    """Пакетный анализ CSV-файлов с заказами интернет-магазина."""

    def __init__(
        self,
        data_dir,
        report_file,
        log_file,
        status_column="status",
        delivered_status="Delivered",
        amount_column="total_amount",
        required_columns=None,
        encoding="utf-8-sig",
    ):
        self.data_dir = Path(data_dir)
        self.report_file = Path(report_file)
        self.log_file = Path(log_file)
        self.status_column = status_column
        self.delivered_status = delivered_status
        self.amount_column = amount_column
        self.required_columns = set(required_columns or {
            self.status_column, self.amount_column
        })
        self.encoding = encoding
        self._configure_logger()

    def _configure_logger(self):
        """Настраивает запись ошибок в logs/errors.log."""
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(f"OrderAnalyzer.{id(self)}")
        self.logger.setLevel(logging.ERROR)
        self.logger.propagate = False

        # Не добавляем повторные обработчики для одного экземпляра.
        if not self.logger.handlers:
            handler = logging.FileHandler(self.log_file, encoding="utf-8")
            handler.setFormatter(logging.Formatter(
                "%(asctime)s | %(levelname)s | %(message)s"
            ))
            self.logger.addHandler(handler)

    def load_file(self, file_path):
        """Загружает CSV и проверяет структуру и тип суммы."""
        file_path = Path(file_path)

        try:
            df = pd.read_csv(
                file_path,
                encoding=self.encoding,
                on_bad_lines="error",
            )
        except pd.errors.EmptyDataError as exc:
            raise ValueError("Файл пуст или не содержит заголовков") from exc
        except UnicodeDecodeError as exc:
            raise ValueError(f"Не удалось прочитать кодировку файла: {exc}") from exc
        except pd.errors.ParserError as exc:
            raise ValueError(f"Некорректная структура CSV: {exc}") from exc

        if df.empty:
            raise ValueError("CSV не содержит записей")

        missing_columns = self.required_columns - set(df.columns)
        if missing_columns:
            raise ValueError(
                "Отсутствуют обязательные столбцы: "
                + ", ".join(sorted(missing_columns))
            )

        # Некорректное значение суммы делает файл непригодным для расчёта.
        numeric_amount = pd.to_numeric(df[self.amount_column], errors="coerce")
        invalid_mask = numeric_amount.isna()
        if invalid_mask.any():
            bad_count = int(invalid_mask.sum())
            raise ValueError(
                f"В столбце '{self.amount_column}' найдено "
                f"нечисловых или пустых значений: {bad_count}"
            )

        df[self.amount_column] = numeric_amount
        return df

    def filter_delivered(self, df):
        """Оставляет только доставленные заказы."""
        return df[
            df[self.status_column]
            .astype("string")
            .str.strip()
            .str.casefold()
            == self.delivered_status.casefold()
        ].copy()

    def calculate_metrics(self, delivered_df):
        """Рассчитывает выручку, средний чек и число доставленных заказов."""
        order_count = int(len(delivered_df))

        if order_count == 0:
            revenue = 0.0
            average_check = 0.0
        else:
            revenue = float(delivered_df[self.amount_column].sum())
            average_check = float(delivered_df[self.amount_column].mean())

        return {
            "revenue": round(revenue, 2),
            "average_check": round(average_check, 2),
            "orders_count": order_count,
        }

    def process_file(self, file_path):
        """Обрабатывает один файл и возвращает строку отчёта."""
        df = self.load_file(file_path)
        delivered_df = self.filter_delivered(df)
        metrics = self.calculate_metrics(delivered_df)

        return {
            "file_name": Path(file_path).name,
            **metrics,
        }

    def process_all_files(self):
        """Обрабатывает все CSV в data/, пропуская файлы с ошибками."""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.report_file.parent.mkdir(parents=True, exist_ok=True)

        csv_files = sorted(self.data_dir.glob("*.csv"))
        results = []
        error_count = 0

        for file_path in csv_files:
            try:
                results.append(self.process_file(file_path))
                print(f"[OK] Обработан файл: {file_path.name}")
            except Exception as exc:
                error_count += 1
                self.logger.exception(
                    "Файл '%s' пропущен. Причина: %s",
                    file_path.name,
                    exc,
                )
                print(f"[ERROR] Файл пропущен: {file_path.name}. Причина: {exc}")

        report_columns = [
            "file_name", "revenue", "average_check", "orders_count"
        ]
        report_df = pd.DataFrame(results, columns=report_columns)
        report_df.to_csv(
            self.report_file,
            index=False,
            encoding=self.encoding,
        )

        processed_count = len(results)
        print("\nОбработка завершена.")
        print(f"Успешно обработано файлов: {processed_count}")
        print(f"Файлов с ошибками: {error_count}")
        print(f"Всего найдено CSV-файлов: {len(csv_files)}")
        print(f"Отчёт сохранён: {self.report_file}")

        return {
            "processed_count": processed_count,
            "error_count": error_count,
            "total_files": len(csv_files),
            "report": report_df,
        }
