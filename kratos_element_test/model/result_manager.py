class ResultManager:
    def __init__(self, current_test_getter):
        self._results = {}
        self._current_test_getter = current_test_getter

    def get_results(self):
        return self._results.get(self._current_test_getter(), {})

    def set_results(self, expected_results):
        self._results[self._current_test_getter()] = expected_results
