from typing import Callable, Dict, List, Optional


class ResultManager:
    """
    This class manages all results that can be displayed or exported in the GUI.
    """

    def __init__(self, active_test_getter: Callable[[], str]):
        """
        :param active_test_getter: callable which returns the currently active test
        """
        self._simulation_results: Dict[str, Dict[str, List[float]]] = {}
        self._experimental_results: Dict[str, Dict[str, List[float]]] = {}
        self._active_test_getter = active_test_getter

    def get_results_of_active_test_type(self) -> Optional[Dict[str, List[float]]]:
        return self._simulation_results.get(self.get_current_test())

    def set_results_of_active_test_type(self, results: Dict[str, List[float]]):
        self._simulation_results[self._active_test_getter()] = results

    def get_current_test(self) -> str:
        return self._active_test_getter()

    def clear_results(self) -> None:
        self._simulation_results.clear()

    def get_experimental_results(self) -> Dict[str, List[float]]:
        return self._experimental_results.get(self.get_current_test(), {})

    def set_experimental_results_for_test_type(
        self, test_type: str, results: Dict[str, List[float]]
    ) -> None:
        self._experimental_results[test_type] = results

    def clear_experimental_results(self) -> None:
        self._experimental_results.clear()
