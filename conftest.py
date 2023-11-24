from contextlib import contextmanager
import logging

@contextmanager
def services_context_manager(test_id):
    try:
        logging.info(f"Start the testcase- {test_id}")
        yield True
    except Exception as e:
        logging.error(e)
        raise
    finally:
        logging.info(f"End the testcase- {test_id}")

