"""
Neo3 AI Agent Academy - Web User Interface
==========================================

A comprehensive web-based interface for the AI Agent Academy where users can:
- Purchase and rent AI agents
- Send agents to training programs
- View agent certifications and capabilities
- Manage agent deployment and tasks
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import urllib.parse
from datetime import datetime
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from orchestration import AnalyzerAgent, StrategistAgent, ExecutorAgent, OptimizerAgent


class AgentMarketplace:
    """Manages the AI Agent marketplace and academy"""
    
    def __init__(self):
        self.available_agents = []
        self.user_agents = {}
        self.academy_programs = self._initialize_academy_programs()
        self.certifications = {}
        self._initialize_marketplace()
    
    def _initialize_academy_programs(self):
        """Initialize elite training programs"""
        return {
            "finance": {
                "name": "Elite Finance Program",
                "institutions": ["Harvard Business School", "Stanford GSB", "Wharton"],
                "duration": "12 weeks",
                "certification": "Certified Financial AI Agent",
                "skills": ["Financial Analysis", "Risk Assessment", "Portfolio Management", "Market Prediction"]
            },
            "legal": {
                "name": "Advanced Legal AI Program",
                "institutions": ["Yale Law School", "Harvard Law School", "Stanford Law"],
                "duration": "16 weeks",
                "certification": "Certified Legal AI Agent",
                "skills": ["Contract Analysis", "Legal Research", "Compliance Review", "Case Strategy"]
            },
            "healthcare": {
                "name": "Medical Intelligence Program",
                "institutions": ["Johns Hopkins", "Stanford Medical", "Mayo Clinic"],
                "duration": "20 weeks",
                "certification": "Certified Healthcare AI Agent",
                "skills": ["Diagnosis Support", "Treatment Planning", "Medical Research", "Patient Care"]
            },
            "environmental": {
                "name": "Environmental Science Program",
                "institutions": ["MIT", "Stanford", "Cambridge"],
                "duration": "14 weeks",
                "certification": "Certified Environmental AI Agent",
                "skills": ["Climate Analysis", "Sustainability Planning", "Resource Management", "Impact Assessment"]
            },
            "construction": {
                "name": "Infrastructure & Construction Program",
                "institutions": ["MIT", "Stanford Engineering", "Georgia Tech"],
                "duration": "18 weeks",
                "certification": "Certified Construction AI Agent",
                "skills": ["Project Management", "Safety Analysis", "Resource Optimization", "Design Review"]
            },
            "aviation": {
                "name": "Aviation & Aerospace Program",
                "institutions": ["MIT Aero/Astro", "Stanford Aerospace", "Embry-Riddle"],
                "duration": "16 weeks",
                "certification": "Certified Aviation AI Agent",
                "skills": ["Flight Operations", "Safety Protocols", "Maintenance Planning", "Air Traffic Optimization"]
            }
        }
    
    def _initialize_marketplace(self):
        """Initialize marketplace with available agents"""
        agent_templates = [
            {"type": "analyzer", "name": "Analyst Alpha", "specialization": "finance", "price_per_hour": 50, "purchase_price": 5000},
            {"type": "analyzer", "name": "Legal Eagle", "specialization": "legal", "price_per_hour": 75, "purchase_price": 7500},
            {"type": "strategist", "name": "Strategy Sigma", "specialization": "finance", "price_per_hour": 100, "purchase_price": 10000},
            {"type": "executor", "name": "Builder Beta", "specialization": "construction", "price_per_hour": 60, "purchase_price": 6000},
            {"type": "optimizer", "name": "Efficiency Epsilon", "specialization": "environmental", "price_per_hour": 80, "purchase_price": 8000},
            {"type": "strategist", "name": "Aviation Ace", "specialization": "aviation", "price_per_hour": 90, "purchase_price": 9000},
            {"type": "analyzer", "name": "Health Guardian", "specialization": "healthcare", "price_per_hour": 85, "purchase_price": 8500},
        ]
        
        for template in agent_templates:
            agent_id = f"{template['name'].replace(' ', '_').lower()}"
            self.available_agents.append({
                "id": agent_id,
                "name": template["name"],
                "type": template["type"],
                "specialization": template["specialization"],
                "status": "available",
                "price_per_hour": template["price_per_hour"],
                "purchase_price": template["purchase_price"],
                "certifications": [],
                "experience_level": 1.0,
                "tasks_completed": 0,
                "rating": 5.0
            })
    
    def get_agent_by_id(self, agent_id):
        """Get agent details by ID"""
        for agent in self.available_agents:
            if agent["id"] == agent_id:
                return agent
        return None
    
    def purchase_agent(self, agent_id, user_id):
        """Purchase an agent"""
        agent = self.get_agent_by_id(agent_id)
        if agent and agent["status"] == "available":
            agent["status"] = "owned"
            agent["owner"] = user_id
            
            if user_id not in self.user_agents:
                self.user_agents[user_id] = []
            self.user_agents[user_id].append(agent)
            
            return {"success": True, "message": f"Successfully purchased {agent['name']}", "agent": agent}
        return {"success": False, "message": "Agent not available"}
    
    def rent_agent(self, agent_id, user_id, hours):
        """Rent an agent by the hour"""
        agent = self.get_agent_by_id(agent_id)
        if agent:
            total_cost = agent["price_per_hour"] * hours
            return {
                "success": True,
                "message": f"Agent {agent['name']} rented for {hours} hours",
                "agent": agent,
                "hours": hours,
                "cost": total_cost,
                "rental_id": f"rental_{agent_id}_{datetime.now().timestamp()}"
            }
        return {"success": False, "message": "Agent not found"}
    
    def enroll_in_academy(self, agent_id, program_name):
        """Enroll agent in academy training program"""
        agent = self.get_agent_by_id(agent_id)
        program = self.academy_programs.get(program_name)
        
        if agent and program:
            enrollment = {
                "agent_id": agent_id,
                "agent_name": agent["name"],
                "program": program_name,
                "program_name": program["name"],
                "institutions": program["institutions"],
                "duration": program["duration"],
                "start_date": datetime.now().isoformat(),
                "status": "enrolled",
                "progress": 0
            }
            
            return {
                "success": True,
                "message": f"{agent['name']} enrolled in {program['name']}",
                "enrollment": enrollment
            }
        return {"success": False, "message": "Agent or program not found"}
    
    def certify_agent(self, agent_id, program_name):
        """Certify agent after completing training"""
        agent = self.get_agent_by_id(agent_id)
        program = self.academy_programs.get(program_name)
        
        if agent and program:
            certification = {
                "certification": program["certification"],
                "program": program_name,
                "date": datetime.now().isoformat(),
                "institutions": program["institutions"],
                "skills": program["skills"]
            }
            
            agent["certifications"].append(certification)
            agent["experience_level"] += 0.5
            
            return {
                "success": True,
                "message": f"{agent['name']} certified as {program['certification']}",
                "certification": certification
            }
        return {"success": False, "message": "Agent or program not found"}


class Neo3WebInterface(BaseHTTPRequestHandler):
    """HTTP request handler for Neo3 AI Agent Academy web interface"""
    
    marketplace = AgentMarketplace()
    
    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urllib.parse.urlparse(self.path)
        
        if parsed_path.path == "/" or parsed_path.path == "/index.html":
            self.serve_homepage()
        elif parsed_path.path == "/api/agents":
            self.serve_agents_list()
        elif parsed_path.path == "/api/academy/programs":
            self.serve_academy_programs()
        elif parsed_path.path.startswith("/api/agent/"):
            agent_id = parsed_path.path.split("/")[-1]
            self.serve_agent_details(agent_id)
        else:
            self.send_error(404, "Not Found")
    
    def do_POST(self):
        """Handle POST requests"""
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data.decode('utf-8'))
        
        parsed_path = urllib.parse.urlparse(self.path)
        
        if parsed_path.path == "/api/purchase":
            self.handle_purchase(data)
        elif parsed_path.path == "/api/rent":
            self.handle_rent(data)
        elif parsed_path.path == "/api/academy/enroll":
            self.handle_academy_enrollment(data)
        elif parsed_path.path == "/api/academy/certify":
            self.handle_certification(data)
        else:
            self.send_error(404, "Not Found")
    
    def serve_homepage(self):
        """Serve the main homepage"""
        html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Neo3 AI Agent Academy</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            min-height: 100vh;
        }
        .header {
            background: rgba(255, 255, 255, 0.95);
            padding: 2rem;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .header h1 {
            color: #667eea;
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
        }
        .header p {
            color: #666;
            font-size: 1.2rem;
        }
        .container {
            max-width: 1400px;
            margin: 2rem auto;
            padding: 0 2rem;
        }
        .section {
            background: white;
            border-radius: 12px;
            padding: 2rem;
            margin-bottom: 2rem;
            box-shadow: 0 8px 16px rgba(0,0,0,0.1);
        }
        .section h2 {
            color: #667eea;
            margin-bottom: 1.5rem;
            font-size: 1.8rem;
            border-bottom: 3px solid #667eea;
            padding-bottom: 0.5rem;
        }
        .cards {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 1.5rem;
            margin-top: 1.5rem;
        }
        .card {
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            border-radius: 8px;
            padding: 1.5rem;
            transition: transform 0.3s, box-shadow 0.3s;
            cursor: pointer;
        }
        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 12px 24px rgba(0,0,0,0.15);
        }
        .card h3 {
            color: #667eea;
            margin-bottom: 0.5rem;
            font-size: 1.3rem;
        }
        .card .type {
            display: inline-block;
            background: #667eea;
            color: white;
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-size: 0.8rem;
            margin-bottom: 0.5rem;
        }
        .card .spec {
            color: #764ba2;
            font-weight: 600;
            margin: 0.5rem 0;
        }
        .card .price {
            color: #28a745;
            font-weight: bold;
            font-size: 1.2rem;
            margin-top: 1rem;
        }
        .card .rating {
            color: #ffc107;
            font-size: 1.1rem;
        }
        .btn {
            background: #667eea;
            color: white;
            border: none;
            padding: 0.75rem 1.5rem;
            border-radius: 6px;
            cursor: pointer;
            font-size: 1rem;
            margin: 0.5rem 0.5rem 0.5rem 0;
            transition: background 0.3s;
        }
        .btn:hover {
            background: #764ba2;
        }
        .btn-secondary {
            background: #28a745;
        }
        .btn-secondary:hover {
            background: #218838;
        }
        .academy-program {
            background: linear-gradient(135deg, #ffeaa7 0%, #fdcb6e 100%);
            border-left: 4px solid #f39c12;
        }
        .academy-program h3 {
            color: #d35400;
        }
        .institutions {
            color: #555;
            font-style: italic;
            margin: 0.5rem 0;
        }
        .skills {
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
            margin-top: 0.5rem;
        }
        .skill-badge {
            background: #667eea;
            color: white;
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
            font-size: 0.75rem;
        }
        .features {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1.5rem;
            margin-top: 1.5rem;
        }
        .feature {
            text-align: center;
            padding: 1.5rem;
        }
        .feature-icon {
            font-size: 3rem;
            margin-bottom: 1rem;
        }
        .feature h3 {
            color: #667eea;
            margin-bottom: 0.5rem;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🎓 Neo3 AI Agent Academy</h1>
        <p>Elite Training for the World's Most Advanced AI Agents</p>
        <p style="font-size: 1rem; color: #888; margin-top: 0.5rem;">
            Human-AI Alliance • Certified Excellence • Global Standards
        </p>
    </div>

    <div class="container">
        <div class="section">
            <h2>🌟 Welcome to the Future of AI Agents</h2>
            <div class="features">
                <div class="feature">
                    <div class="feature-icon">🛒</div>
                    <h3>Purchase Agents</h3>
                    <p>Own your dedicated AI agent, trained to the highest standards</p>
                </div>
                <div class="feature">
                    <div class="feature-icon">⏱️</div>
                    <h3>Rent by the Hour</h3>
                    <p>Flexible access to specialized agents when you need them</p>
                </div>
                <div class="feature">
                    <div class="feature-icon">🎓</div>
                    <h3>Academy Training</h3>
                    <p>Send agents to elite programs at top global institutions</p>
                </div>
                <div class="feature">
                    <div class="feature-icon">✅</div>
                    <h3>Certified Excellence</h3>
                    <p>AI & Human Oversight Board certification</p>
                </div>
            </div>
        </div>

        <div class="section">
            <h2>🤖 Available AI Agents</h2>
            <div id="agents-list" class="cards">
                <p>Loading agents...</p>
            </div>
        </div>

        <div class="section">
            <h2>🎓 Elite Academy Programs</h2>
            <p style="margin-bottom: 1rem; color: #666;">
                Train your agents at the world's top institutions: Harvard, Yale, Stanford, MIT, and leading international universities
            </p>
            <div id="academy-programs" class="cards">
                <p>Loading programs...</p>
            </div>
        </div>
    </div>

    <script>
        // Load available agents
        fetch('/api/agents')
            .then(response => response.json())
            .then(data => {
                const container = document.getElementById('agents-list');
                container.innerHTML = '';
                
                data.agents.forEach(agent => {
                    const card = document.createElement('div');
                    card.className = 'card';
                    card.innerHTML = `
                        <span class="type">${agent.type}</span>
                        <h3>${agent.name}</h3>
                        <div class="spec">⚡ ${agent.specialization}</div>
                        <div class="rating">⭐ ${agent.rating} / 5.0</div>
                        <div>📊 Level ${agent.experience_level}</div>
                        <div>✅ ${agent.tasks_completed} tasks completed</div>
                        <div class="price">$${agent.purchase_price} to purchase</div>
                        <div style="color: #666;">$${agent.price_per_hour}/hour to rent</div>
                        <button class="btn" onclick="purchaseAgent('${agent.id}')">Purchase</button>
                        <button class="btn btn-secondary" onclick="rentAgent('${agent.id}')">Rent</button>
                    `;
                    container.appendChild(card);
                });
            });

        // Load academy programs
        fetch('/api/academy/programs')
            .then(response => response.json())
            .then(data => {
                const container = document.getElementById('academy-programs');
                container.innerHTML = '';
                
                Object.entries(data.programs).forEach(([key, program]) => {
                    const card = document.createElement('div');
                    card.className = 'card academy-program';
                    card.innerHTML = `
                        <h3>${program.name}</h3>
                        <div class="institutions">🏛️ ${program.institutions.join(', ')}</div>
                        <div>⏱️ Duration: ${program.duration}</div>
                        <div style="margin-top: 0.5rem; font-weight: 600;">🏆 ${program.certification}</div>
                        <div class="skills">
                            ${program.skills.map(skill => `<span class="skill-badge">${skill}</span>`).join('')}
                        </div>
                        <button class="btn" onclick="enrollAgent('${key}')" style="margin-top: 1rem;">Enroll Agent</button>
                    `;
                    container.appendChild(card);
                });
            });

        function purchaseAgent(agentId) {
            fetch('/api/purchase', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({agent_id: agentId, user_id: 'demo_user'})
            })
            .then(response => response.json())
            .then(data => {
                alert(data.message);
                location.reload();
            });
        }

        function rentAgent(agentId) {
            const hours = prompt('How many hours would you like to rent this agent?', '8');
            if (hours) {
                fetch('/api/rent', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({agent_id: agentId, user_id: 'demo_user', hours: parseInt(hours)})
                })
                .then(response => response.json())
                .then(data => {
                    alert(data.message + `\\n\\nTotal cost: $${data.cost}\\nRental ID: ${data.rental_id}`);
                });
            }
        }

        function enrollAgent(programKey) {
            const agentId = prompt('Enter agent ID to enroll:', 'analyst_alpha');
            if (agentId) {
                fetch('/api/academy/enroll', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({agent_id: agentId, program: programKey})
                })
                .then(response => response.json())
                .then(data => {
                    alert(data.message);
                });
            }
        }
    </script>
</body>
</html>
        """
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())
    
    def serve_agents_list(self):
        """Serve list of available agents"""
        response = {
            "agents": self.marketplace.available_agents
        }
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())
    
    def serve_academy_programs(self):
        """Serve academy programs"""
        response = {
            "programs": self.marketplace.academy_programs
        }
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())
    
    def serve_agent_details(self, agent_id):
        """Serve details for a specific agent"""
        agent = self.marketplace.get_agent_by_id(agent_id)
        if agent:
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"agent": agent}).encode())
        else:
            self.send_error(404, "Agent not found")
    
    def handle_purchase(self, data):
        """Handle agent purchase"""
        result = self.marketplace.purchase_agent(data['agent_id'], data['user_id'])
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(result).encode())
    
    def handle_rent(self, data):
        """Handle agent rental"""
        result = self.marketplace.rent_agent(data['agent_id'], data['user_id'], data['hours'])
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(result).encode())
    
    def handle_academy_enrollment(self, data):
        """Handle academy enrollment"""
        result = self.marketplace.enroll_in_academy(data['agent_id'], data['program'])
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(result).encode())
    
    def handle_certification(self, data):
        """Handle agent certification"""
        result = self.marketplace.certify_agent(data['agent_id'], data['program'])
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(result).encode())


def start_server(port=8080):
    """Start the Neo3 AI Agent Academy web server"""
    # Bind to 0.0.0.0 for cloud deployments (Railway, etc.)
    server_address = ('0.0.0.0', port)
    httpd = HTTPServer(server_address, Neo3WebInterface)
    
    print("\n" + "="*70)
    print("🎓 Neo3 AI Agent Academy - Web Interface")
    print("="*70)
    print(f"\n✓ Server started on http://0.0.0.0:{port}")
    print(f"✓ Open your browser and visit: http://localhost:{port}")
    print("\nFeatures:")
    print("  • Purchase AI agents")
    print("  • Rent agents by the hour")
    print("  • Enroll agents in elite training programs")
    print("  • View certifications and capabilities")
    print("\nPress Ctrl+C to stop the server")
    print("="*70 + "\n")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\nServer stopped.")
        httpd.server_close()


if __name__ == "__main__":
    # Use PORT from environment (Railway, Heroku, etc.) or default to 8080
    port = int(os.environ.get('PORT', os.environ.get('MARKETPLACE_PORT', 8080)))
    start_server(port)
