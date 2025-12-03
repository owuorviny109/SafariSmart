"""
Module: services/abuse_detector.py
Purpose: Detect and prevent abuse of quick trip feature

This module tracks invalid attempts and blocks abusive users.

Classes:
    AbuseDetector: Main abuse detection service
 
"""

from typing import Optional
from datetime import datetime, timedelta
import logging
from django.core.cache import cache

logger = logging.getLogger(__name__)


class AbuseDetector:
    """
    Detect and prevent abuse of quick trip feature.
    
    Tracks invalid attempts per IP and session, implements
    progressive blocking for repeat offenders.
    
    Example:
        >>> detector = AbuseDetector()
        >>> if detector.is_blocked(ip_address):
        ...     return "Blocked"
    """
    
    # Thresholds
    INVALID_ATTEMPTS_LIMIT = 10  # Max invalid attempts in window
    INVALID_ATTEMPTS_WINDOW = 600  # 10 minutes
    BLOCK_DURATION = 1800  # 30 minutes
    
    # Severe abuse (IP-level blocking)
    SEVERE_ABUSE_LIMIT = 50  # Invalid attempts in 1 hour
    SEVERE_ABUSE_WINDOW = 3600  # 1 hour
    SEVERE_BLOCK_DURATION = 86400  # 24 hours
    
    def __init__(self):
        """Initialize abuse detector."""
        pass
    
    def get_client_ip(self, request) -> str:
        """
        Get client IP address from request.
        
        Args:
            request: Django request object
            
        Returns:
            str: Client IP address
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def track_invalid_attempt(self, ip_address: str, session_key: str) -> None:
        """
        Track an invalid attempt.
        
        Args:
            ip_address (str): Client IP
            session_key (str): Session key
        """
        now = datetime.now().timestamp()
        
        # Track by IP
        ip_key = f'quick_trip_invalid_ip_{ip_address}'
        ip_attempts = cache.get(ip_key, [])
        ip_attempts.append(now)
        
        # Keep only recent attempts
        ip_attempts = [ts for ts in ip_attempts if now - ts < self.SEVERE_ABUSE_WINDOW]
        cache.set(ip_key, ip_attempts, self.SEVERE_ABUSE_WINDOW)
        
        # Check for severe abuse
        if len(ip_attempts) >= self.SEVERE_ABUSE_LIMIT:
            logger.error(f"SEVERE ABUSE detected from IP {ip_address}: {len(ip_attempts)} invalid attempts")
            self.block_ip(ip_address, self.SEVERE_BLOCK_DURATION)
    
    def is_blocked(self, ip_address: str, session_key: str) -> tuple:
        """
        Check if IP or session is blocked.
        
        Args:
            ip_address (str): Client IP
            session_key (str): Session key
            
        Returns:
            tuple: (is_blocked: bool, reason: str, remaining_seconds: int)
        """
        now = datetime.now().timestamp()
        
        # Check IP-level block (severe abuse)
        ip_block_key = f'quick_trip_blocked_ip_{ip_address}'
        ip_block_until = cache.get(ip_block_key, 0)
        
        if now < ip_block_until:
            remaining = int(ip_block_until - now)
            hours = remaining // 3600
            minutes = (remaining % 3600) // 60
            
            if hours > 0:
                reason = f"Too many invalid attempts. Blocked for {hours} hour(s) {minutes} minute(s)."
            else:
                reason = f"Too many invalid attempts. Blocked for {minutes} minute(s)."
            
            return True, reason, remaining
        
        return False, "", 0
    
    def block_ip(self, ip_address: str, duration: int) -> None:
        """
        Block an IP address.
        
        Args:
            ip_address (str): IP to block
            duration (int): Block duration in seconds
        """
        now = datetime.now().timestamp()
        block_until = now + duration
        
        ip_block_key = f'quick_trip_blocked_ip_{ip_address}'
        cache.set(ip_block_key, block_until, duration)
        
        logger.warning(f"Blocked IP {ip_address} for {duration} seconds")
    
    def get_invalid_attempt_count(self, ip_address: str) -> int:
        """
        Get number of recent invalid attempts from IP.
        
        Args:
            ip_address (str): Client IP
            
        Returns:
            int: Number of recent invalid attempts
        """
        now = datetime.now().timestamp()
        
        ip_key = f'quick_trip_invalid_ip_{ip_address}'
        ip_attempts = cache.get(ip_key, [])
        
        # Count recent attempts
        recent_attempts = [ts for ts in ip_attempts if now - ts < self.INVALID_ATTEMPTS_WINDOW]
        
        return len(recent_attempts)
    
    def clear_attempts(self, ip_address: str, session_key: str) -> None:
        """
        Clear invalid attempts (on successful submission).
        
        Args:
            ip_address (str): Client IP
            session_key (str): Session key
        """
        ip_key = f'quick_trip_invalid_ip_{ip_address}'
        cache.delete(ip_key)
