import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from openjck.intelligence import analyse_trace, DependencyChainTracer, RecoveryPointDetector


def test_root_cause_detection():
    trace = {
        'trace_id': 'test_001',
        'status': 'failed',
        'run_name': 'test_agent',
        'steps': [
            {'step_id': 1, 'name': 'call_llm', 'type': 'llm_call', 'output': {'content': 'Use file data/report_2026.csv'}, 'error': None},
            {'step_id': 2, 'name': 'process', 'type': 'agent_step', 'output': {'result': 'ok'}, 'error': None},
            {'step_id': 3, 'name': 'read_file', 'type': 'tool_call', 'input': {'path': 'data/report_2026.csv'}, 'output': {}, 'error': 'FileNotFoundError: data/report_2026.csv not found'},
        ]
    }

    result = analyse_trace(trace)
    assert result.root_cause_step is not None, 'Should detect root cause'
    assert result.recovery_point_step == 2, 'Recovery point should be step 2'
    print('test_root_cause_detection PASSED')


def test_no_false_positive_on_success():
    trace = {
        'trace_id': 'test_002',
        'status': 'completed',
        'steps': [{'step_id': 1, 'name': 'call_llm', 'output': {'content': 'ok'}, 'error': None}]
    }

    result = analyse_trace(trace)
    assert result.root_cause_step is None, 'Should not flag successful runs'
    print('test_no_false_positive_on_success PASSED')


test_root_cause_detection()
test_no_false_positive_on_success()
print('ALL INTELLIGENCE TESTS PASSED')
