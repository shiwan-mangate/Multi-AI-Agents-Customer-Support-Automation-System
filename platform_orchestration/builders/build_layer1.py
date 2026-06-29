import functools
from layer_1.app.nodes.supervisor_node import supervisor_node

def build_layer1(container):
   
    container.supervisor_node = functools.partial(
        supervisor_node,
        llm=container.llm
    )