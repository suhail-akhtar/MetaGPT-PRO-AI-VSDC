from fastapi import APIRouter, HTTPException
from metagpt.api.orchestrator import orchestrator
from metagpt.schema import UserMessage

router = APIRouter()

@router.get("/")
async def list_roles():
    """List all agents in the team"""
    if not orchestrator.team:
        raise HTTPException(status_code=404, detail="Team not hired yet.")
    
    roles = {}
    for name, role in orchestrator.team.env.get_roles().items():
        roles[name] = {
            "profile": role.profile,
            "goal": role.goal,
            "is_idle": role.is_idle,
            "todo": str(role.rc.todo) if role.rc.todo else None
        }
    return roles

@router.get("/{name}/memory")
async def get_role_memory(name: str):
    """Get the memory of a specific agent"""
    if not orchestrator.team:
        raise HTTPException(status_code=404, detail="Team not hired yet.")
    
    role = orchestrator.team.env.get_role(name)
    if not role:
        raise HTTPException(status_code=404, detail=f"Role {name} not found.")
    
    # Return last 20 messages
    memories = role.get_memories(k=20)
    return [
        {
            "role": m.role,
            "content": m.content,
            "cause_by": m.cause_by
        } 
        for m in memories
    ]

@router.post("/{name}/message")
async def message_agent(name: str, content: str):
    """Send a direct message/instruction to an agent"""
    if not orchestrator.team:
        raise HTTPException(status_code=404, detail="Team not hired yet.")
    
    role = orchestrator.team.env.get_role(name)
    if not role:
        raise HTTPException(status_code=404, detail=f"Role {name} not found.")
    
    msg = UserMessage(content=content)
    role.put_message(msg)
    return {"message": f"Message delivered to {name}."}
