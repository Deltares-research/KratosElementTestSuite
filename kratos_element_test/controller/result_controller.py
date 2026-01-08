class ResultController:
    def __init__(self,result_manager):
        self._result_manager=result_manager

    def get_latest_results(self):
        return self._result_manager.get_results()

    def get_current_test(self):
    	return self._result_manager.get_current_test()
