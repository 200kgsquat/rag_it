import argparse
from datetime import datetime, timedelta
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

def main():
    from config import config
    from qabot.repository.log_repository import LogRepository

    parser = argparse.ArgumentParser(description="Fetch logs from the database.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--session-id", help="Fetch logs by session ID")
    group.add_argument("--time-range", nargs=2, metavar=("START", "END"),
                       help="Fetch logs by time range (ISO format, e.g., '2024-01-01T00:00:00' '2024-01-01T23:59:59')")

    args = parser.parse_args()

    config.ensure_dirs()
    repo = LogRepository()

    if args.session_id:
        records = repo.get_by_session(args.session_id)
        print(f"Logs for session '{args.session_id}':")
        for record in records:
            print(f"ID: {record.id}, Time: {record.timestamp}, Question: {record.question}, Answer: {record.answer[:100]}..., Timings: {record.retrieve_ms}/{record.llm_ms}/{record.total_ms}")
    elif args.time_range:
        start = datetime.fromisoformat(args.time_range[0])
        end = datetime.fromisoformat(args.time_range[1])
        records = repo.get_by_time_range(start, end)
        print(f"Logs between {start} and {end}:")
        for record in records:
            print(f"ID: {record.id}, Session: {record.session_id}, Time: {record.timestamp}, Question: {record.question}, Answer: {record.answer[:100]}..., Timings: {record.retrieve_ms}/{record.llm_ms}/{record.total_ms}")

if __name__ == "__main__":
    main()
