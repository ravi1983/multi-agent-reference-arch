#!/bin/bash

cd agent
source .venv/bin/activate
cd ..

uvicorn agent.main:app --port 8080