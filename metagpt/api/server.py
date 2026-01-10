from fastapi import FastAPI
from metagpt.api.routes import company, config, roles, files, stream, conversation, project, agents, bugs, versions

app = FastAPI(
    title="MetaGPT-Pro Enterprise API",
    description="Autonomous Software Development Virtual Company API",
    version="1.0.0"
)

# Include Routers
app.include_router(company.router, prefix="/v1/company", tags=["Company"])
app.include_router(config.router, prefix="/v1/config", tags=["Configuration"])
app.include_router(roles.router, prefix="/v1/roles", tags=["Roles"])
app.include_router(files.router, prefix="/v1/files", tags=["Files"])
app.include_router(stream.router, prefix="/v1/stream", tags=["Streaming"])
app.include_router(conversation.router, prefix="/v1/conversation", tags=["Conversation"])
app.include_router(project.router, prefix="/v1/project", tags=["Project"])
app.include_router(agents.router, prefix="/v1/agents", tags=["Agent Collaboration"])
app.include_router(bugs.router, prefix="/v1/project", tags=["Bug Tracking"])
app.include_router(versions.router, prefix="/v1/project", tags=["Versioning"])

@app.get("/")
async def root():
    return {"message": "Welcome to MetaGPT-Pro Enterprise API", "docs_url": "/docs"}

def main():
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()
