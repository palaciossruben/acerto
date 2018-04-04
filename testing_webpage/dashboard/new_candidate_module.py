from datetime import datetime
import common


def update_candidate(candidate, candidate_params):
    """
    Args:
        candidate: Obj
        candidate_params: dict with fields of a candidate obj
    Returns: None
    """

    common.update_object(candidate, candidate_params)
    candidate.updated_at = datetime.utcnow()
    candidate.save()

    return candidate
