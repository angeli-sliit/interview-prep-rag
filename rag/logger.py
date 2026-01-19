import json
import os
from datetime import datetime
from pathlib import Path

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

def log_query(question, answer, sources_count=0, answer_mode="default", evaluation=None):
    """Log query and answer for monitoring"""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "question": question,
        "answer_length": len(answer),
        "sources_count": sources_count,
        "answer_mode": answer_mode,
        "evaluation": evaluation,
    }
    
    log_file = LOG_DIR / f"queries_{datetime.now().strftime('%Y-%m-%d')}.jsonl"
    
    try:
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
    except Exception as e:
        # Silently fail if logging doesn't work
        pass

def get_stats():
    """Get usage statistics"""
    try:
        stats = {
            "total_queries": 0,
            "total_days": 0,
            "files": []
        }
        
        if LOG_DIR.exists():
            log_files = list(LOG_DIR.glob("queries_*.jsonl"))
            stats["total_days"] = len(log_files)
            stats["files"] = [f.name for f in log_files]
            
            for log_file in log_files:
                try:
                    with open(log_file, "r", encoding="utf-8") as f:
                        stats["total_queries"] += len(f.readlines())
                except:
                    pass
        
        return stats
    except:
        return {"total_queries": 0, "total_days": 0, "files": []}
