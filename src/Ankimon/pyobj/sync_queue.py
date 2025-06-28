import time
import threading
from ..utils import is_online
from aqt.utils import tooltip

class SyncQueueManager:
    def __init__(self, sync_callback, logger=None, retry_interval=10):
        self.sync_callback = sync_callback
        self.logger = logger
        self.retry_interval = retry_interval
        self.pending = False
        self._stop = False
        self._thread = None

    def mark_for_sync(self):
        if self.logger:
            self.logger.log("info", "Marked sync as pending — will retry when online.")
        self.pending = True
        self.start_retry_loop()

    def start_retry_loop(self):
        if self._thread and self._thread.is_alive():
            return
        self._thread = threading.Thread(target=self._retry_loop, daemon=True)
        self._thread.start()

    def _retry_loop(self):
        while not self._stop and self.pending:
            if is_online():
                if self.logger:
                    self.logger.log("info", "Device is online. Syncing now.")
                try:
                    self.sync_callback()
                    tooltip("Pending sync resumed.")
                    self.pending = False
                    if self.logger:
                        self.logger.log("info", "Sync completed successfully.")
                except Exception as e:
                    if self.logger:
                        self.logger.log("error", f"Failed to resume sync: {e}")
            time.sleep(self.retry_interval)

    def stop(self, wait=False):
        self._stop = True
        if wait and self._thread and self._thread.is_alive():
            self._thread.join()

    def is_pending(self):
        return self.pending
    
    def is_running(self):
        return self._thread is not None and self._thread.is_alive()
    
    def reset(self):
        self.stop()
        self.pending = False
        if self._thread:
            if self.logger:
                self.logger.log("info", "Sync queue reset.")
        self._thread = None

    def __del__(self):
        self.stop(wait = True)
        if self.logger:
            self.logger.log("info", "SyncQueueManager instance deleted.")
        self._thread = None
        self.sync_callback = None
        self.logger = None
        self._stop = True
        self.pending = False
        
# Ensure the thread is stopped and cleaned up
def cleanup_sync_queue(sync_queue_manager):
    if sync_queue_manager and sync_queue_manager.is_running():
        sync_queue_manager.stop(wait = True)
        if sync_queue_manager.logger:
            sync_queue_manager.logger.log("info", "SyncQueueManager cleaned up.")
    else:
        if sync_queue_manager and sync_queue_manager.logger:
            sync_queue_manager.logger.log("info", "SyncQueueManager was not running, no cleanup needed.")
    sync_queue_manager.reset()
    return sync_queue_manager

# Ensure the sync queue manager is cleaned up when the application exits
def ensure_sync_queue_cleanup(sync_queue_manager):
    if sync_queue_manager:
        cleanup_sync_queue(sync_queue_manager)
    else:
        if sync_queue_manager and sync_queue_manager.logger:
            sync_queue_manager.logger.log("info", "No SyncQueueManager instance to clean up.")
    return None

