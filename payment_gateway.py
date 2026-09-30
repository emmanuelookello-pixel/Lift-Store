"""Contract for the future hosted payment-provider adapter; disabled by default."""
from dataclasses import dataclass
from typing import Protocol

@dataclass(frozen=True)
class PaymentRequest:
    order_id:int
    amount_ugx:int
    method:str
    idempotency_key:str

@dataclass(frozen=True)
class VerifiedPayment:
    provider_reference:str
    order_id:int
    amount_ugx:int
    currency:str
    status:str

class HostedPaymentGateway(Protocol):
    def create_checkout(self,request:PaymentRequest)->str:
        """Return a provider-hosted HTTPS checkout URL."""
        ...
    def verify_notification(self,raw_body:bytes,headers:dict)->VerifiedPayment:
        """Verify signature and recheck transaction with the provider."""
        ...

class UnconfiguredGateway:
    def create_checkout(self,request):
        raise RuntimeError('Online payments are not configured.')
    def verify_notification(self,raw_body,headers):
        raise RuntimeError('Online payments are not configured.')
