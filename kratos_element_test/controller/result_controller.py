from typing import Dict, List, Optional

from kratos_element_test.model.result_manager import ResultManager


class ResultController:
    def __init__(self, result_manager: ResultManager):
        self._result_manager = result_manager

    def get_latest_results(self) -> Optional[Dict[str, List[float]]]:
        return self._result_manager.get_results_of_active_test_type()

    def get_current_test(self) -> str:
        return self._result_manager.get_current_test()

    def get_experimental_results(self) -> Dict[str, List[float]]:
        return self._result_manager.get_experimental_results()

    def clear_experimental_results(self) -> None:
        self._result_manager.clear_experimental_results()
