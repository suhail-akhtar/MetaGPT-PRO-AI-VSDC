from fastapi import APIRouter, HTTPException
from metagpt.config2 import config
from metagpt.api.schemas import ConfigUpdate

router = APIRouter()

@router.get("/")
async def get_config():
    """Get the current running configuration"""
    # Return a simplified view or full view?
    # Full config might contain keys, so be careful.
    # Exposing public parts only.
    mask_keys = ["api_key", "secret_key", "access_key"]
    dump = config.model_dump()
    if 'llm' in dump:
        for k in dump['llm']:
            if any(mask in k for mask in mask_keys):
                dump['llm'][k] = "***"
    return dump

@router.put("/")
async def update_config(update: ConfigUpdate):
    """Update configuration values"""
    if update.llm:
        # Pydantic update or manual merge
        # This is complex because config is a Pydantic model.
        # Simple implementation: update extra dict or specific fields
        for k, v in update.llm.items():
            setattr(config.llm, k, v)
    
    # Reload functionality if needed, or just apply in-memory
    return {"status": "updated", "config": await get_config()}
