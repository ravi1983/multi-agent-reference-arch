#!/bin/bash

cd remote_agent
source .venv/bin/activate
cd ..

uvicorn remote_agent.main_agent:root_agent --port 9095