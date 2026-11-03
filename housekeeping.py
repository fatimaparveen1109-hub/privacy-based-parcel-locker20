from db import execute
def expire_pickups(): execute("UPDATE qr_tokens SET expired_at=NOW() WHERE used_at IS NULL AND expires_at<NOW() AND expired_at IS NULL")
