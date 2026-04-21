import time
from typing import Dict, List
from datetime import datetime
from collections import defaultdict

class PerformanceMonitor:
    """
    Monitoring module để track performance metrics.
    """
    
    def __init__(self):
        self.metrics = defaultdict(list)
        self.start_time = datetime.now()
    
    def record_latency(self, operation: str, latency: float):
        """Record latency cho một operation."""
        self.metrics[f"{operation}_latency"].append(latency)
    
    def record_cost(self, operation: str, cost: float):
        """Record cost cho một operation."""
        self.metrics[f"{operation}_cost"].append(cost)
    
    def record_tokens(self, operation: str, tokens: int):
        """Record token usage."""
        self.metrics[f"{operation}_tokens"].append(tokens)
    
    def get_summary(self) -> Dict:
        """Lấy performance summary."""
        summary = {}
        
        for metric_name, values in self.metrics.items():
            if values:
                summary[metric_name] = {
                    "count": len(values),
                    "min": round(min(values), 4),
                    "max": round(max(values), 4),
                    "avg": round(sum(values) / len(values), 4),
                    "total": round(sum(values), 4)
                }
        
        return summary
    
    def get_uptime(self) -> str:
        """Lấy uptime."""
        elapsed = datetime.now() - self.start_time
        return str(elapsed)

class AlertingSystem:
    """
    Alerting system để phát hiện anomalies.
    """
    
    def __init__(self):
        self.alerts = []
        self.thresholds = {
            "latency_ms": 5000,  # 5 seconds
            "cost_per_query": 0.01,  # $0.01
            "error_rate": 0.05  # 5%
        }
    
    def check_latency(self, latency: float, operation: str) -> bool:
        """Check if latency exceeds threshold."""
        if latency > self.thresholds["latency_ms"] / 1000:
            alert = {
                "type": "LATENCY_ALERT",
                "operation": operation,
                "value": round(latency, 3),
                "threshold": self.thresholds["latency_ms"] / 1000,
                "timestamp": datetime.now().isoformat()
            }
            self.alerts.append(alert)
            return True
        return False
    
    def check_cost(self, cost: float, operation: str) -> bool:
        """Check if cost exceeds threshold."""
        if cost > self.thresholds["cost_per_query"]:
            alert = {
                "type": "COST_ALERT",
                "operation": operation,
                "value": round(cost, 4),
                "threshold": self.thresholds["cost_per_query"],
                "timestamp": datetime.now().isoformat()
            }
            self.alerts.append(alert)
            return True
        return False
    
    def check_error_rate(self, errors: int, total: int) -> bool:
        """Check if error rate exceeds threshold."""
        if total > 0:
            error_rate = errors / total
            if error_rate > self.thresholds["error_rate"]:
                alert = {
                    "type": "ERROR_RATE_ALERT",
                    "errors": errors,
                    "total": total,
                    "rate": round(error_rate, 4),
                    "threshold": self.thresholds["error_rate"],
                    "timestamp": datetime.now().isoformat()
                }
                self.alerts.append(alert)
                return True
        return False
    
    def get_alerts(self) -> List[Dict]:
        """Lấy tất cả alerts."""
        return self.alerts
    
    def clear_alerts(self):
        """Xóa alerts."""
        self.alerts.clear()

class DistributedProcessingCoordinator:
    """
    Coordinator cho distributed processing.
    """
    
    def __init__(self, num_workers: int = 4):
        self.num_workers = num_workers
        self.worker_stats = {i: {"processed": 0, "errors": 0} for i in range(num_workers)}
    
    def assign_task(self, task_id: int) -> int:
        """Assign task tới worker với ít work nhất."""
        worker_id = min(self.worker_stats.keys(), 
                       key=lambda w: self.worker_stats[w]["processed"])
        self.worker_stats[worker_id]["processed"] += 1
        return worker_id
    
    def record_error(self, worker_id: int):
        """Record error cho worker."""
        self.worker_stats[worker_id]["errors"] += 1
    
    def get_worker_stats(self) -> Dict:
        """Lấy worker statistics."""
        return self.worker_stats
    
    def get_load_balance(self) -> float:
        """Tính load balance score (0-1, 1 = perfect balance)."""
        processed = [s["processed"] for s in self.worker_stats.values()]
        if not processed or max(processed) == 0:
            return 1.0
        
        avg = sum(processed) / len(processed)
        variance = sum((p - avg) ** 2 for p in processed) / len(processed)
        
        # Normalize variance to 0-1 scale
        max_variance = (max(processed) ** 2)
        if max_variance == 0:
            return 1.0
        
        return 1.0 - (variance / max_variance)

if __name__ == "__main__":
    monitor = PerformanceMonitor()
    monitor.record_latency("retrieval", 0.5)
    monitor.record_latency("retrieval", 0.6)
    monitor.record_cost("generation", 0.001)
    
    print(monitor.get_summary())
    
    alerting = AlertingSystem()
    alerting.check_latency(6.0, "retrieval")
    print(alerting.get_alerts())
