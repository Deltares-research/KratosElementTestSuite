class ResultManager:
    def __init__(self):
        self._results = {}

    def get_results(self, test_type):
        return self._results.get(test_type, {})

    def set_results(self, expected_results,test_type):
        self._results[test_type] = expected_results
