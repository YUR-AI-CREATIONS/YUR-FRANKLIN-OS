"""
Goal tracking utilities for the Respectful Motivation App
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional
import json

class GoalTracker:
    """Enhanced goal tracking with categories and analytics"""
    
    def __init__(self, data_file: str = "goals_data.json"):
        self.data_file = data_file
        self.categories = {
            "Health & Fitness": "💪",
            "Career": "💼", 
            "Education": "📚",
            "Personal": "🌱",
            "Financial": "💰",
            "Relationships": "❤️",
            "Hobbies": "🎨",
            "Travel": "✈️",
            "General": "🎯"
        }
    
    def analyze_progress(self, goals: List[Dict]) -> Dict:
        """Analyze goal completion patterns"""
        if not goals:
            return {"message": "No goals to analyze yet - go for it and add some!"}
        
        analysis = {
            "total_goals": len(goals),
            "completed_goals": len([g for g in goals if g["completed"]]),
            "categories": {},
            "recent_activity": 0,
            "completion_rate": 0
        }
        
        # Calculate completion rate
        if analysis["total_goals"] > 0:
            analysis["completion_rate"] = (analysis["completed_goals"] / analysis["total_goals"]) * 100
        
        # Analyze by category
        for goal in goals:
            category = goal.get("category", "General")
            if category not in analysis["categories"]:
                analysis["categories"][category] = {"total": 0, "completed": 0}
            
            analysis["categories"][category]["total"] += 1
            if goal["completed"]:
                analysis["categories"][category]["completed"] += 1
        
        # Check recent activity (last 7 days)
        recent_date = datetime.now() - timedelta(days=7)
        for goal in goals:
            goal_date = datetime.fromisoformat(goal["created_date"])
            if goal_date >= recent_date:
                analysis["recent_activity"] += 1
        
        return analysis
    
    def get_category_emoji(self, category: str) -> str:
        """Get emoji for category"""
        return self.categories.get(category, "🎯")
    
    def suggest_next_steps(self, goals: List[Dict]) -> List[str]:
        """Suggest next steps based on goal patterns"""
        suggestions = []
        
        if not goals:
            suggestions.append("Start by adding your first goal - go for it respectfully!")
            return suggestions
        
        incomplete_goals = [g for g in goals if not g["completed"]]
        completed_goals = [g for g in goals if g["completed"]]
        
        if len(incomplete_goals) > 5:
            suggestions.append("You have many active goals. Consider focusing on 2-3 priorities to go for it effectively!")
        
        if len(completed_goals) > 0:
            suggestions.append("Great job on your completed goals! Use that momentum to go for it with new challenges!")
        
        # Check for old incomplete goals
        old_goals = []
        thirty_days_ago = datetime.now() - timedelta(days=30)
        
        for goal in incomplete_goals:
            goal_date = datetime.fromisoformat(goal["created_date"])
            if goal_date < thirty_days_ago:
                old_goals.append(goal)
        
        if old_goals:
            suggestions.append("Some goals are over 30 days old. Review them respectfully - update or complete them!")
        
        return suggestions

def format_goal_display(goal: Dict, tracker: GoalTracker) -> str:
    """Format a goal for display"""
    emoji = tracker.get_category_emoji(goal["category"])
    status = "✅" if goal["completed"] else "⏳"
    
    created = datetime.fromisoformat(goal["created_date"]).strftime("%m/%d/%Y")
    
    display = f"{status} {emoji} {goal['goal']}\n"
    display += f"   Category: {goal['category']} | Created: {created}"
    
    if goal["completed"] and goal.get("completion_date"):
        completed = datetime.fromisoformat(goal["completion_date"]).strftime("%m/%d/%Y")
        display += f" | Completed: {completed}"
    
    return display