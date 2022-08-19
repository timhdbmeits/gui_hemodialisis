# Standard library modules.

# Third party modules.

# Local modules
from mosquito.utils import (
    MosquitoError,
    monitor_queue,
    MonitoredQueue,
    DelayQueue,
    MonitoredDelayQueue
)
from mosquito.api import (
    available_attributes,
    register_attributes,
    attribute,
    swarm,
    observer
)
from mosquito.swarm import Swarm
from mosquito.scheduler import Scheduler

# Globals and constants variables.
MOSQUITO = mosquito = r"""
mosquito        \             /
                 \     |     /
                 /   \ | /   \
                 \    \|/    /
                  \,  o^o  ,/
                    \,/"\,/
            ,,,,----,{/X\},----,,,,
   ,,---''''      _-'{\X/}'-_      ''''---,,
 /'            ,-'/   \V/   \'-,            '\
(        ,--''/   |   (_)   |   \''--,        )
 '--,,-''    |    |   /_\   |   |     ''-,,--'
            /'    |  (_-_)  |   '\
           /     /'   \_/   '\    \
          /     /     (_)     \    \
               /       V       \
              /                 \
             /                   \
""".strip()
