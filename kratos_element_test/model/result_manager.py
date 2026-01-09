class ResultManager:
    def __init__(self, current_test_getter):
        self._simulation_results = {}
        self._current_test_getter = current_test_getter

    def get_results(self):
        return self._simulation_results.get(self._current_test_getter(), {})

    def set_results(self, expected_results):
        self._simulation_results[self._current_test_getter()] = expected_results

    def get_current_test(self):
        return self._current_test_getter()
