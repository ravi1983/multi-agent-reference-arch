import logging
from typing import List

from agent.models.llm_models import Plan, PlanType


def find_plan_for_agent(plans: List[Plan], agent: PlanType):
    plans_found = [p.plan for p in plans if p.plan_type == agent]
    logging.info(f"Plans to be used for agent {agent} is {plans_found}")
    return plans_found
