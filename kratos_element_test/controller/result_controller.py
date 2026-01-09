from typing import Dict, List

from kratos_element_test.model.result_manager import ResultManager


class ResultController:
    def __init__(self, result_manager: ResultManager):
        self._result_manager = result_manager

    def get_latest_results(self) -> Dict[str, List[float]]:
        return self._result_manager.get_results_of_active_test_type()

    def get_current_test(self) -> str:
        return self._result_manager.get_current_test()
