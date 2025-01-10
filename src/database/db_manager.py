import sqlite3
from datetime import datetime
import json
import os
from typing import Dict, List, Any, Optional

class DatabaseManager:
    def __init__(self, db_path: str = "data/reports.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self._init_db()

    def _init_db(self):
        """Initialize the database with required tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create reports table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS reports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    filename TEXT NOT NULL,
                    report_path TEXT NOT NULL,
                    report_type TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    analysis_results TEXT,
                    metadata TEXT
                )
            """)
            
            # Create quick_summaries table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS quick_summaries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    report_id INTEGER,
                    summary_text TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (report_id) REFERENCES reports (id)
                )
            """)
            
            conn.commit()

    def save_report(self, filename: str, report_path: str, report_type: str, 
                   analysis_results: Dict[str, Any], metadata: Dict[str, Any]) -> int:
        """Save a new report to the database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO reports (filename, report_path, report_type, analysis_results, metadata)
                VALUES (?, ?, ?, ?, ?)
            """, (
                filename,
                report_path,
                report_type,
                json.dumps(analysis_results),
                json.dumps(metadata)
            ))
            conn.commit()
            return cursor.lastrowid

    def save_quick_summary(self, report_id: int, summary_text: str) -> int:
        """Save a quick summary for a report"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO quick_summaries (report_id, summary_text)
                VALUES (?, ?)
            """, (report_id, summary_text))
            conn.commit()
            return cursor.lastrowid

    def get_recent_reports(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get the most recent reports"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, filename, report_type, created_at, metadata
                FROM reports
                ORDER BY created_at DESC
                LIMIT ?
            """, (limit,))
            
            reports = []
            for row in cursor.fetchall():
                report = dict(row)
                report['metadata'] = json.loads(report['metadata'])
                reports.append(report)
            
            return reports

    def get_report_details(self, report_id: int) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific report"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get report details
            cursor.execute("""
                SELECT *
                FROM reports
                WHERE id = ?
            """, (report_id,))
            
            report = cursor.fetchone()
            if not report:
                return None
                
            report_dict = dict(report)
            report_dict['analysis_results'] = json.loads(report_dict['analysis_results'])
            report_dict['metadata'] = json.loads(report_dict['metadata'])
            
            # Get associated summaries
            cursor.execute("""
                SELECT id, summary_text, created_at
                FROM quick_summaries
                WHERE report_id = ?
                ORDER BY created_at DESC
            """, (report_id,))
            
            summaries = [dict(row) for row in cursor.fetchall()]
            report_dict['summaries'] = summaries
            
            return report_dict

    def search_reports(self, query: str) -> List[Dict[str, Any]]:
        """Search reports based on filename or metadata"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            search_term = f"%{query}%"
            cursor.execute("""
                SELECT id, filename, report_type, created_at, metadata
                FROM reports
                WHERE filename LIKE ? OR metadata LIKE ?
                ORDER BY created_at DESC
            """, (search_term, search_term))
            
            reports = []
            for row in cursor.fetchall():
                report = dict(row)
                report['metadata'] = json.loads(report['metadata'])
                reports.append(report)
            
            return reports

    def get_report_summary_stats(self) -> Dict[str, Any]:
        """Get summary statistics about reports"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Get total reports
            cursor.execute("SELECT COUNT(*) FROM reports")
            total_reports = cursor.fetchone()[0]
            
            # Get reports by type
            cursor.execute("""
                SELECT report_type, COUNT(*) as count
                FROM reports
                GROUP BY report_type
            """)
            report_types = dict(cursor.fetchall())
            
            # Get reports in last 24 hours
            cursor.execute("""
                SELECT COUNT(*) 
                FROM reports 
                WHERE created_at >= datetime('now', '-1 day')
            """)
            recent_reports = cursor.fetchone()[0]
            
            return {
                "total_reports": total_reports,
                "report_types": report_types,
                "recent_reports": recent_reports
            }
