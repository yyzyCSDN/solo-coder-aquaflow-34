from dataclasses import dataclass
@dataclass(frozen=True)
class Revision:
    revision:int;sequence:int;open_pipes:frozenset[str]
def at(sequence:int,rows:list[Revision]):
    # Historical reads may only see revisions effective at or before the
    # queried sequence; future revisions must never leak into the answer.
    xs=[r for r in rows if r.sequence<=sequence]
    if not xs:raise ValueError("no revision")
    # Deterministic tie-break: within the same effective sequence the
    # highest revision id wins, regardless of input ordering.
    return max(xs,key=lambda r:(r.sequence,r.revision))
