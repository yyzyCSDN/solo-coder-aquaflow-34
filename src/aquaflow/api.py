from .treatment.chlorine_ct import compliant
from .network.isolation import isolated
from .network.topology import at as topology_at
from .meters.balance import balance
from .leak.localize import rank
from .workflow_service import WorkflowService
class AquaFlowService:
    def __init__(self):self.workflows=WorkflowService()
    def health(self):return {"service":"aquaflow","status":"ok","runtime_dependencies":0}
    def ct(self,rows,required):return compliant(rows,required)
    def isolate(self,nodes,pipes,closed,sources):return isolated(nodes,pipes,closed,sources)
    def water_balance(self,ins,outs,known_loss):return balance(ins,outs,known_loss)
    def leak_rank(self,rows):return rank(rows)
    def topology(self,sequence,rows):
        revision=topology_at(sequence,rows)
        return {"revision":revision,"open_pipes":revision.open_pipes}
    def run_workflow(self,name,payload,received_at=None):return self.workflows.run(name,payload,received_at)
