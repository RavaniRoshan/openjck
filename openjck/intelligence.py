import json
import re
from typing import Optional
from dataclasses import dataclass, field


@dataclass
class IntelligenceResult:
    trace_id: str
    root_cause_step: Optional[int] = None
    root_cause_reason: Optional[str] = None
    recovery_point_step: Optional[int] = None
    dependency_chain: list = field(default_factory=list)
    anomalies: list = field(default_factory=list)
    patterns: list = field(default_factory=list)


class DependencyChainTracer:
    """Finds the earliest step whose output fed into the failure chain."""

    # Patterns that look like file paths, variable names, IDs, URLs
    VALUE_PATTERNS = [
        r'[\w/\\.-]+\.(?:csv|txt|json|md|py|pdf|xlsx|png|jpg)',  # file paths
        r'https?://\S+',  # URLs
        r'[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}',  # UUIDs
        r'\b[A-Z][A-Z0-9_]{3,}\b',  # CONSTANT_NAMES
    ]

    def extract_values(self, text: str) -> set:
        """Extract values from text that could be referenced by later steps."""
        if not text:
            return set()
        values = set()
        for pattern in self.VALUE_PATTERNS:
            matches = re.findall(pattern, str(text))
            values.update(matches)
        return values

    def trace(self, steps: list) -> tuple[Optional[int], Optional[str], list]:
        """
        Returns (root_cause_step_id, reason, dependency_chain)
        """
        if not steps:
            return None, None, []

        # Find the first failed step
        failed_steps = [s for s in steps if s.get('error')]
        if not failed_steps:
            return None, None, []

        first_failure = failed_steps[0]
        failure_step_id = first_failure.get('step_id', 0)

        # Build output value map: what each step produced
        output_values = {}
        for step in steps:
            sid = step.get('step_id', 0)
            if sid >= failure_step_id:
                break
            output_str = json.dumps(step.get('output', {})) + json.dumps(step.get('input', {}))
            vals = self.extract_values(output_str)
            if vals:
                output_values[sid] = vals

        # Check if values from earlier steps appear in the failure context
        failure_context = json.dumps(first_failure.get('input', {})) + (first_failure.get('error') or '')
        dependency_chain = []
        root_cause_step = None
        root_cause_reason = None

        for step_id, values in sorted(output_values.items()):
            for val in values:
                if val in failure_context and len(val) > 4:
                    dependency_chain.append({
                        'step_id': step_id,
                        'value': val,
                        'used_in_step': failure_step_id
                    })
                    if root_cause_step is None or step_id < root_cause_step:
                        root_cause_step = step_id
                        step_name = next((s.get('name', f'step {step_id}') for s in steps if s.get('step_id') == step_id), f'step {step_id}')
                        root_cause_reason = (
                            f"Output from step {step_id} ({step_name}) contained \"{val}\" "
                            f"which was referenced by the failing step {failure_step_id} "
                            f"({first_failure.get('name', '')}). "
                            f"Error: {str(first_failure.get('error', ''))[:120]}"
                        )

        # If no dependency found, the failure itself is the root cause
        if root_cause_step is None:
            root_cause_step = failure_step_id
            root_cause_reason = (
                f"Step {failure_step_id} ({first_failure.get('name', '')}) "
                f"failed directly. Error: {str(first_failure.get('error', ''))[:200]}"
            )

        return root_cause_step, root_cause_reason, dependency_chain


class RecoveryPointDetector:
    """Finds the last step with valid output before the failure chain."""

    def detect(self, steps: list) -> Optional[int]:
        if not steps:
            return None
        recovery_point = None
        for step in steps:
            if step.get('error'):
                break
            if step.get('output') and step['output'] != {}:
                recovery_point = step.get('step_id')
        return recovery_point


class AnomalyDetector:
    """Compares current run steps against historical baseline."""

    def detect(self, current_steps: list, historical_runs: list) -> list:
        if not historical_runs or not current_steps:
            return []

        # Build baseline: mean duration and tokens per step name
        baseline = {}
        for run in historical_runs:
            for step in (run.get('steps') or []):
                name = step.get('name', '')
                if name not in baseline:
                    baseline[name] = {'durations': [], 'tokens': []}
                if step.get('duration_ms'):
                    baseline[name]['durations'].append(step['duration_ms'])
                total_tokens = (step.get('tokens_in') or 0) + (step.get('tokens_out') or 0)
                if total_tokens:
                    baseline[name]['tokens'].append(total_tokens)

        anomalies = []
        for step in current_steps:
            name = step.get('name', '')
            if name not in baseline:
                continue
            b = baseline[name]
            if len(b['durations']) >= 3:
                mean_dur = sum(b['durations']) / len(b['durations'])
                if step.get('duration_ms') and step['duration_ms'] > mean_dur * 3:
                    anomalies.append({
                        'step_id': step.get('step_id'),
                        'step_name': name,
                        'type': 'slow_step',
                        'message': f"Step '{name}' took {step['duration_ms']}ms — average is {int(mean_dur)}ms"
                    })
            if len(b['tokens']) >= 3:
                mean_tok = sum(b['tokens']) / len(b['tokens'])
                current_tokens = (step.get('tokens_in') or 0) + (step.get('tokens_out') or 0)
                if current_tokens and current_tokens > mean_tok * 4:
                    anomalies.append({
                        'step_id': step.get('step_id'),
                        'step_name': name,
                        'type': 'token_spike',
                        'message': f"Step '{name}' used {current_tokens} tokens — average is {int(mean_tok)}"
                    })

        return anomalies


class PatternAggregator:
    """Finds recurring failure patterns across multiple runs of the same agent."""

    def aggregate(self, agent_name: str, recent_runs: list) -> list:
        if not recent_runs:
            return []

        failed_runs = [r for r in recent_runs if r.get('status') == 'failed']
        if len(failed_runs) < 2:
            return []

        # Count which steps fail most often
        failure_counts = {}
        for run in failed_runs:
            for step in (run.get('steps') or []):
                if step.get('error'):
                    name = step.get('name', f"step_{step.get('step_id')}")
                    failure_counts[name] = failure_counts.get(name, 0) + 1

        patterns = []
        total_runs = len(recent_runs)
        for step_name, count in failure_counts.items():
            if count >= 2:
                pct = int((count / total_runs) * 100)
                patterns.append({
                    'step_name': step_name,
                    'failure_count': count,
                    'total_runs': total_runs,
                    'failure_rate_pct': pct,
                    'message': f"'{step_name}' fails in {count}/{total_runs} runs ({pct}%)"
                })

        return sorted(patterns, key=lambda x: x['failure_count'], reverse=True)


def analyse_trace(trace: dict, historical_runs: list = None) -> IntelligenceResult:
    """
    Main entry point. Takes a full trace dict and optional historical runs.
    Returns IntelligenceResult.
    """
    trace_id = trace.get('trace_id', '')
    steps = trace.get('steps', [])

    result = IntelligenceResult(trace_id=trace_id)

    if trace.get('status') != 'failed':
        return result  # Only analyse failed runs

    tracer = DependencyChainTracer()
    result.root_cause_step, result.root_cause_reason, result.dependency_chain = tracer.trace(steps)

    detector = RecoveryPointDetector()
    result.recovery_point_step = detector.detect(steps)

    if historical_runs:
        anomaly_detector = AnomalyDetector()
        result.anomalies = anomaly_detector.detect(steps, historical_runs)

        aggregator = PatternAggregator()
        result.patterns = aggregator.aggregate(trace.get('run_name', ''), historical_runs)

    return result
