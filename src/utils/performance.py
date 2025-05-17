import time
from typing import Dict, List
import statistics

class PerformanceMonitor:
    def __init__(self):
        self.metrics: Dict[str, List[float]] = {
            'data_processing': [],
            'ui_update': [],
            'end_to_end': []
        }
        self.start_times: Dict[str, float] = {}

    def start_measurement(self, metric_name: str):
        """Start measuring a specific metric"""
        self.start_times[metric_name] = time.perf_counter()

    def end_measurement(self, metric_name: str):
        """End measuring a specific metric and record the duration"""
        if metric_name in self.start_times:
            duration = (time.perf_counter() - self.start_times[metric_name]) * 1000  # Convert to ms
            self.metrics[metric_name].append(duration)
            del self.start_times[metric_name]

    def get_statistics(self) -> Dict[str, Dict[str, float]]:
        """Get statistics for all metrics"""
        stats = {}
        for metric, values in self.metrics.items():
            if values:
                stats[metric] = {
                    'mean': statistics.mean(values),
                    'median': statistics.median(values),
                    'min': min(values),
                    'max': max(values),
                    'std': statistics.stdev(values) if len(values) > 1 else 0
                }
        return stats

    def reset(self):
        """Reset all metrics"""
        self.metrics = {k: [] for k in self.metrics}
        self.start_times = {} 