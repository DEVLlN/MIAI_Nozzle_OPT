def get_oldest_mcp_parent(mcp):
    """Recursively looks for the oldest parent of the MCParticle"""
    pars = mcp.getParents()
    if (len(pars) < 1):
        return mcp
    for par in pars:
        if par is mcp:
            continue
        return get_oldest_mcp_parent(par)
