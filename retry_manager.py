class RetryManager:
    def __init__(self, max_retries=2):
        self.retry_counts = {}  # {(pipeline_name, runId): retry_count}
        self.max_retries = max_retries
        self.blocked_runs = set()

    def _key(self, pipeline_name, run_id):
        return (pipeline_name, run_id)

    def can_retry(self, pipeline_name, run_id):
        key = self._key(pipeline_name, run_id)
        if key in self.blocked_runs:
            return False
        return self.retry_counts.get(key, 0) < self.max_retries

    def record_retry(self, pipeline_name, run_id):
        key = self._key(pipeline_name, run_id)
        count = self.retry_counts.get(key, 0) + 1
        self.retry_counts[key] = count
        if count >= self.max_retries:
            self.blocked_runs.add(key)

    def reset_retry(self, pipeline_name, run_id):
        key = self._key(pipeline_name, run_id)
        self.retry_counts.pop(key, None)
        self.blocked_runs.discard(key)
