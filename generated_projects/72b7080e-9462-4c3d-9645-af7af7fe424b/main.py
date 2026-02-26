#!/usr/bin/env python3
"""
Respectful Motivation App - Encouraging users to "go for it" respectfully
"""

import json
import os
from datetime import datetime
from typing import List, Dict
import random

class MotivationApp:
    def __init__(self):
        self.data_file = "user_goals.json"
        self.goals = self.load_goals()
        self.motivational_messages = [
            "Go for it respectfully! You've got this! 💪",
            "Take that step forward - respectfully and confidently! 🚀",
            "Believe in yourself and go for it with respect and dignity! ✨",
            "Your dreams are valid - pursue them respectfully! 🌟",
            "Go for it! Success comes to those who try respectfully! 🎯",
            "Be brave, be respectful, and go for your goals! 🦋",
            "Respectfully chase your dreams - they're waiting for you! 🌈",
            "Go for it with kindness and determination! 💖",
            "Your potential is limitless - pursue it respectfully! 🔥",
            "Take the leap respectfully - you're stronger than you think! 🦅"
        ]
    
    def load_goals(self) -> List[Dict]:
        """Load goals from JSON file"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                return []
        return []
    
    def save_goals(self):
        """Save goals to JSON file"""
        try:
            with open(self.data_file, 'w') as f:
                json.dump(self.goals, f, indent=2)
        except Exception as e:
            print(f"Error saving goals: {e}")
    
    def add_goal(self, goal: str, category: str = "General"):
        """Add a new goal respectfully"""
        new_goal = {
            "id": len(self.goals) + 1,
            "goal": goal,
            "category": category,
            "created_date": datetime.now().isoformat(),
            "completed": False,
            "completion_date": None
        }
        self.goals.append(new_goal)
        self.save_goals()
        print(f"✅ Goal added respectfully: '{goal}'")
        print(random.choice(self.motivational_messages))
    
    def complete_goal(self, goal_id: int):
        """Mark a goal as completed"""
        for goal in self.goals:
            if goal["id"] == goal_id:
                goal["completed"] = True
                goal["completion_date"] = datetime.now().isoformat()
                self.save_goals()
                print(f"🎉 Congratulations! You respectfully completed: '{goal['goal']}'")
                print("Go for it - you're on a roll! Keep up the great work! 🌟")
                return
        print("Goal not found. Please check the goal ID.")
    
    def list_goals(self):
        """List all goals respectfully"""
        if not self.goals:
            print("No goals yet. Go for it and add your first goal! 🎯")
            return
        
        print("\n📋 Your Goals (Go for it respectfully!):")
        print("-" * 50)
        
        for goal in self.goals:
            status = "✅ Completed" if goal["completed"] else "⏳ In Progress"
            created = datetime.fromisoformat(goal["created_date"]).strftime("%Y-%m-%d")
            
            print(f"ID: {goal['id']}")
            print(f"Goal: {goal['goal']}")
            print(f"Category: {goal['category']}")
            print(f"Status: {status}")
            print(f"Created: {created}")
            
            if goal["completed"] and goal["completion_date"]:
                completed = datetime.fromisoformat(goal["completion_date"]).strftime("%Y-%m-%d")
                print(f"Completed: {completed}")
            
            print("-" * 30)
    
    def get_motivation(self):
        """Get a random motivational message"""
        message = random.choice(self.motivational_messages)
        print(f"\n💬 {message}")
        
        # Add goal-specific motivation if there are incomplete goals
        incomplete_goals = [g for g in self.goals if not g["completed"]]
        if incomplete_goals:
            goal = random.choice(incomplete_goals)
            print(f"Remember: You're working towards '{goal['goal']}' - go for it respectfully! 🎯")
    
    def show_stats(self):
        """Show progress statistics"""
        total = len(self.goals)
        completed = len([g for g in self.goals if g["completed"]])
        
        if total == 0:
            print("No goals tracked yet. Go for it and add some goals! 🚀")
            return
        
        progress = (completed / total) * 100
        
        print("\n📊 Your Respectful Progress:")
        print("-" * 30)
        print(f"Total Goals: {total}")
        print(f"Completed: {completed}")
        print(f"In Progress: {total - completed}")
        print(f"Success Rate: {progress:.1f}%")
        
        if progress >= 75:
            print("🔥 Amazing! You're crushing it respectfully!")
        elif progress >= 50:
            print("💪 Great progress! Keep going respectfully!")
        elif progress >= 25:
            print("🌱 You're on your way! Go for it respectfully!")
        else:
            print("🎯 Just getting started! Go for it - you've got this!")
    
    def run(self):
        """Main application loop"""
        print("🌟 Welcome to the Respectful Motivation App! 🌟")
        print("This is what I'm here for - helping you go for it respectfully!")
        print()
        
        while True:
            print("\n" + "="*50)
            print("RESPECTFUL MOTIVATION MENU")
            print("="*50)
            print("1. Add a Goal (Go for it!)")
            print("2. Complete a Goal")
            print("3. View All Goals")
            print("4. Get Motivation")
            print("5. View Progress Stats")
            print("6. Exit")
            
            try:
                choice = input("\nChoose an option (1-6): ").strip()
                
                if choice == "1":
                    goal = input("What goal would you like to pursue respectfully? ")
                    if goal.strip():
                        category = input("Category (optional, press Enter for 'General'): ").strip() or "General"
                        self.add_goal(goal.strip(), category)
                    else:
                        print("Please enter a valid goal.")
                
                elif choice == "2":
                    self.list_goals()
                    try:
                        goal_id = int(input("Enter goal ID to mark as completed: "))
                        self.complete_goal(goal_id)
                    except ValueError:
                        print("Please enter a valid goal ID number.")
                
                elif choice == "3":
                    self.list_goals()
                
                elif choice == "4":
                    self.get_motivation()
                
                elif choice == "5":
                    self.show_stats()
                
                elif choice == "6":
                    print("Thank you for using the Respectful Motivation App!")
                    print("Remember: Go for it respectfully - you've got this! 🌟")
                    break
                
                else:
                    print("Invalid choice. Please select 1-6.")
            
            except KeyboardInterrupt:
                print("\n\nThank you for using the app! Go for it respectfully! 👋")
                break
            except Exception as e:
                print(f"An error occurred: {e}")
                print("But don't worry - go for it and try again! 💪")

def main():
    """Entry point"""
    app = MotivationApp()
    app.run()

if __name__ == "__main__":
    main()