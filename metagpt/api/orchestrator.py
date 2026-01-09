import asyncio
from typing import Optional
from metagpt.team import Team
from metagpt.config2 import config
from metagpt.logs import logger
from metagpt.api.schemas import CompanyStatus, RoleStatus, ProjectRequest

class GlobalOrchestrator:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GlobalOrchestrator, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self.team: Optional[Team] = None
        self.running_task: Optional[asyncio.Task] = None
        self._status = "idle"
        self._initialized = True

    @property
    def status(self) -> str:
        if self.running_task and not self.running_task.done():
            return "running"
        return "idle"

    def hire(self, roles: list = None):
        """Initialize a new company team"""
        # If roles is None, Team will load default from SoftwareCompany or empty, 
        # but SoftwareCompany logic usually does config.roles/startup. 
        # For API, we initialize a fresh Team.
        self.team = Team()
        self.team.hire(roles or [
            # Default roles if none provided, imported dynamically to avoid circular imports if possible
            # But Team() might be empty.
            # We typically want the Standard Software Company Structure.
            # We'll rely on Team default behavior or caller to provide roles.
            # For now, let's just init an empty Team or check config.
        ])
        
        # HACK: Replicate "Software Company" setup if empty
        if not self.team.env.get_roles():
            from metagpt.roles.project_manager import ProjectManager
            from metagpt.roles.product_manager import ProductManager
            from metagpt.roles.architect import Architect
            from metagpt.roles.engineer import Engineer
            from metagpt.roles.qa_engineer import QaEngineer
            from metagpt.roles.di.team_leader import TeamLeader
            from metagpt.roles.di.engineer2 import Engineer2
            from metagpt.roles.di.data_analyst import DataAnalyst
            
            self.team.hire([
                TeamLeader(),
                ProductManager(),
                Architect(),
                Engineer2(), # Use Engineer2 as per software_company.py default
                DataAnalyst(),
            ])
        logger.info("New Team hired.")

    async def start_project(self, req: ProjectRequest):
        if self.status == "running":
            raise ValueError("Company is already running a project.")
        
        requirement_text = req.requirement
        # Determine project_id with proper precedence
        if req.project_name:
            project_id = req.project_name
        elif req.conversation_id:
            project_id = req.conversation_id.replace("conv_", "proj_")
        else:
            project_id = "default_project"
        
        try:
            # Check if using pre-approved requirements from conversation
            if req.conversation_id:
                from metagpt.conversation import conversation_manager
                approved_text = await conversation_manager.get_approved_requirement_text(req.conversation_id)
                if approved_text:
                    requirement_text = approved_text
                    logger.info(f"Using approved requirements from conversation {req.conversation_id}")
                else:
                    logger.warning(f"No approved requirements found for {req.conversation_id}, using provided requirement")
            
            # 1. Handle Project Name
            if req.project_name:
                config.update_via_cli(
                    project_path=req.project_name, 
                    project_name=req.project_name, 
                    inc=True, 
                    reqa_file="", 
                    max_auto_summarize_code=0
                )
            
            # 2. Generate Task Breakdown & Sprint Plan
            await self._initialize_project_management(project_id, requirement_text)
            
            if not self.team:
                self.hire()

            # 3. Hook Environment for Real-time structured events
            self._hook_environment()

            self.team.invest(req.investment)
            self.team.run_project(requirement_text)  # Use potentially enhanced requirement
        except Exception as e:
            logger.exception(f"Start Project failed: {e}")
            raise ValueError(f"Start Project failed at step: {e}")
        
        # Start background task
        self.running_task = asyncio.create_task(self._run_loop(req.n_round))
        logger.info(f"Project started: {req.project_name}")
    
    async def _initialize_project_management(self, project_id: str, requirements: str):
        """Initialize task breakdown, sprints, and Kanban board"""
        try:
            from metagpt.project.task_breakdown import TaskBreakdownGenerator
            from metagpt.project.sprint_planner import SprintPlanner
            from metagpt.project.backlog_manager import BacklogManager
            from metagpt.project.board_tracker import board_tracker
            
            # 1. Generate task breakdown
            generator = TaskBreakdownGenerator()
            breakdown = await generator.generate(requirements)
            
            # 2. Initialize backlog
            manager = BacklogManager(project_id)
            await manager.initialize(
                epics=breakdown["epics"],
                stories=breakdown["stories"],
                tasks=breakdown["tasks"]
            )
            
            # 3. Create sprints
            planner = SprintPlanner()
            sprints = planner.create_sprints(
                tasks=breakdown["tasks"],
                stories=breakdown["stories"]
            )
            await manager.save_sprints(sprints)
            
            # 4. Initialize board
            await board_tracker.initialize_board(project_id, breakdown["tasks"])
            
            logger.info(f"Project management initialized for {project_id}")
        except Exception as e:
            logger.warning(f"Failed to initialize project management: {e}")
            # Non-fatal - continue with standard workflow

    def _hook_environment(self):
        if hasattr(self.team.env, "_is_hooked") and self.team.env._is_hooked:
            return
            
        original_publish = self.team.env.publish_message
        
        def new_publish(*args, **kwargs):
            # args[0] is typically the message
            if args:
                message = args[0]
                if hasattr(message, 'content'):
                    # Emit structured event
                    asyncio.create_task(self._broadcast({
                        "type": "message",
                        "role": message.role,
                        "content": message.content,
                        "cause_by": str(message.cause_by),
                        "sent_from": message.sent_from,
                        # "send_to": list(message.send_to) if message.send_to else []
                    }))
            return original_publish(*args, **kwargs)
        
        object.__setattr__(self.team.env, "publish_message", new_publish)
        self.team.env._is_hooked = True

    async def _run_loop(self, n_round: int):
        try:
            self._status = "running"
            await self.team.run(n_round=n_round, idea=None) # idea already set in run_project
        except Exception as e:
            logger.exception(f"Error in project run loop: {e}")
        finally:
            self._status = "idle"

    async def stop(self):
        if self.running_task and not self.running_task.done():
            self.running_task.cancel()
            try:
                await self.running_task
            except asyncio.CancelledError:
                pass
            logger.info("Project stopped manually.")

    def get_status(self) -> CompanyStatus:
        if not self.team:
             return CompanyStatus(status="not_hired", roles=[], is_idle=True)
        
        roles_status = []
        for role in self.team.env.roles.values():
            todo = role.rc.todo
            roles_status.append(RoleStatus(
                name=role.name,
                profile=role.profile,
                goal=role.goal,
                is_idle=role.is_idle,
                current_todo=str(todo) if todo else None
            ))
            
        return CompanyStatus(
            status=self.status,
            roles=roles_status,
            is_idle=self.team.env.is_idle
        )

    # Log Streaming Logic
    def _log_sink(self, message):
         asyncio.create_task(self._broadcast(str(message)))

    async def _broadcast(self, message):
        import json
        msg_str = json.dumps(message) if isinstance(message, dict) else str(message)
        for ws in self._websockets:
            try:
                await ws.send_text(msg_str)
            except Exception:
                pass

    def add_websocket(self, ws):
        self._websockets.add(ws)

    def remove_websocket(self, ws):
        self._websockets.remove(ws)

    def start_log_stream(self):
        if not hasattr(self, "_streaming_started") or not self._streaming_started:
            from metagpt.logs import logger
            logger.add(self._log_sink, level="INFO")
            self._streaming_started = True

    async def get_plan(self):
        """Retrieve the current project plan/tasks from the generated file"""
        if not self.team:
            return None
        
        from metagpt.const import DEFAULT_WORKSPACE_ROOT
        import glob
        import os
        import json
        
        # Search for project_schedule.json
        search_path = DEFAULT_WORKSPACE_ROOT
        if config.project_name:
             search_path = search_path / config.project_name
        
        files = glob.glob(str(search_path / "**/project_schedule.json"), recursive=True)
        
        if files:
            latest_file = max(files, key=os.path.getmtime)
            try:
                with open(latest_file, 'r', encoding='utf-8') as f:
                     return json.load(f)
            except:
                return None
        return None

# Global Instance
orchestrator = GlobalOrchestrator()
orchestrator._websockets = set()
orchestrator.start_log_stream()
