import functools
from layer_0.main import main
from layer_0.normalizer import normalize
from layer_0.crm import CustomerInfoService  

def build_layer0(container):
    container.layer0_normalizer = normalize
    
    container.customer_info_service = CustomerInfoService(
        profile_repo=container.triage_customer_repository,
        ticket_repo=container.triage_ticket_repository  
    )
  
    container.layer0_main = functools.partial(
        main,
        normalizer=container.layer0_normalizer,
        language_detector=container.language_detector,              
        crm_repository=container.customer_info_service    
    )