"""
Timeout management system for algorithm execution.

This module provides configurable timeout mechanisms for algorithm execution
with graceful handling of timeout scenarios and proper cleanup.
"""

import signal
import time
import threading
from typing import Any, Callable, Optional, TypeVar
from contextlib import contextmanager

T = TypeVar('T')


class TimeoutError(Exception):
    """Raised when an operation times out."""
    pass


class TimeoutManager:
    """
    Manages timeout functionality for algorithm execution.
    
    Provides both signal-based and thread-based timeout mechanisms
    depending on the platform and use case.
    """
    
    def __init__(self, default_timeout: float = 30.0):
        """
        Initialize the timeout manager.
        
        Args:
            default_timeout: Default timeout in seconds
        """
        self.default_timeout = default_timeout
        self._original_handler = None
        
    @contextmanager
    def timeout(self, seconds: Optional[float] = None):
        """
        Context manager for timeout functionality.
        
        Args:
            seconds: Timeout duration in seconds. Uses default if None.
            
        Yields:
            None
            
        Raises:
            TimeoutError: If the operation times out
        """
        timeout_duration = seconds if seconds is not None else self.default_timeout
        
        if timeout_duration <= 0:
            # No timeout requested
            yield
            return
            
        # Use signal-based timeout on Unix-like systems
        if hasattr(signal, 'SIGALRM'):
            yield from self._signal_timeout(timeout_duration)
        else:
            # Fallback to thread-based timeout on Windows
            yield from self._thread_timeout(timeout_duration)
    
    @contextmanager
    def _signal_timeout(self, seconds: float):
        """Signal-based timeout implementation (Unix/Linux/Mac)."""
        def timeout_handler(signum, frame):
            raise TimeoutError(f"Operation timed out after {seconds} seconds")
        
        # Save original handler
        self._original_handler = signal.signal(signal.SIGALRM, timeout_handler)
        
        try:
            # Set alarm
            signal.alarm(int(seconds))
            yield
        except TimeoutError:
            raise
        finally:
            # Clean up: cancel alarm and restore original handler
            signal.alarm(0)
            if self._original_handler is not None:
                signal.signal(signal.SIGALRM, self._original_handler)
                self._original_handler = None
    
    @contextmanager
    def _thread_timeout(self, seconds: float):
        """Thread-based timeout implementation (Windows compatible)."""
        result = [None]
        exception = [None]
        finished = threading.Event()
        
        def target():
            try:
                # This is a placeholder - the actual work happens in the context
                finished.wait()
            except Exception as e:
                exception[0] = e
        
        thread = threading.Thread(target=target)
        thread.daemon = True
        thread.start()
        
        try:
            yield
            finished.set()
        except Exception as e:
            finished.set()
            raise
        
        # Check if we timed out
        thread.join(timeout=seconds)
        if thread.is_alive():
            finished.set()
            raise TimeoutError(f"Operation timed out after {seconds} seconds")
        
        if exception[0]:
            raise exception[0]
    
    def execute_with_timeout(self, func: Callable[[], T], 
                           timeout_seconds: Optional[float] = None) -> T:
        """
        Execute a function with timeout protection.
        
        Args:
            func: Function to execute
            timeout_seconds: Timeout duration in seconds
            
        Returns:
            Result of the function execution
            
        Raises:
            TimeoutError: If the function times out
        """
        with self.timeout(timeout_seconds):
            return func()
    
    def safe_execute(self, func: Callable[[], T], 
                    timeout_seconds: Optional[float] = None,
                    default_value: Optional[T] = None) -> tuple[T, bool]:
        """
        Safely execute a function with timeout, returning success status.
        
        Args:
            func: Function to execute
            timeout_seconds: Timeout duration in seconds
            default_value: Value to return if timeout occurs
            
        Returns:
            Tuple of (result, success_flag)
        """
        try:
            result = self.execute_with_timeout(func, timeout_seconds)
            return result, True
        except TimeoutError:
            return default_value, False
        except Exception:
            # Re-raise non-timeout exceptions
            raise


# Global timeout manager instance
default_timeout_manager = TimeoutManager()


@contextmanager
def timeout(seconds: float):
    """
    Convenience function for timeout context manager.
    
    Args:
        seconds: Timeout duration in seconds
        
    Yields:
        None
        
    Raises:
        TimeoutError: If the operation times out
    """
    with default_timeout_manager.timeout(seconds):
        yield


def execute_with_timeout(func: Callable[[], T], timeout_seconds: float) -> T:
    """
    Convenience function to execute a function with timeout.
    
    Args:
        func: Function to execute
        timeout_seconds: Timeout duration in seconds
        
    Returns:
        Result of the function execution
        
    Raises:
        TimeoutError: If the function times out
    """
    return default_timeout_manager.execute_with_timeout(func, timeout_seconds)