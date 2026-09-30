"""Optional Web Push transport. No messages are sent without configured keys."""
import os,json,logging

def send_push(subscription,payload):
    key=os.environ.get('VAPID_PRIVATE_KEY');subject=os.environ.get('VAPID_SUBJECT')
    if not key or not subject: return False
    try:
        from pywebpush import webpush
        webpush(subscription_info=subscription,data=json.dumps(payload),vapid_private_key=key,vapid_claims={'sub':subject},ttl=3600,timeout=5)
        return True
    except Exception:
        # Do not log endpoints or credentials.
        logging.getLogger(__name__).warning('Push delivery failed; order changes remain saved.')
        return False
