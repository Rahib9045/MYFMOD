import json
import os

def generate_mock_data():
    os.makedirs('data', exist_ok=True)
    
    resumes = [
        {
            "id": "res_001",
            "name": "Alice Johnson",
            "skills": "Python, Machine Learning, PyTorch, SQL, Scikit-learn",
            "experience": "3 years as a Data Scientist at TechCorp. Built recommendation engines.",
            "education": "MS in Computer Science, Stanford University"
        },
        {
            "id": "res_002",
            "name": "Bob Smith",
            "skills": "JavaScript, React, Node.js, CSS, HTML5",
            "experience": "5 years Frontend Developer. Lead UI/UX designer for various web apps.",
            "education": "BS in Informatics, Berkeley"
        },
        {
            "id": "res_003",
            "name": "Charlie Brown",
            "skills": "Project Management, Agile, Scrum, Jira, Communication",
            "experience": "7 years Project Manager. Managed cross-functional teams in finance.",
            "education": "MBA, Harvard Business School"
        }
    ]
    
    job_descriptions = [
        {
            "id": "job_001",
            "title": "Machine Learning Engineer",
            "description": "We are looking for a Machine Learning Engineer to build and optimize models using PyTorch and Scikit-learn. Proficiency in Python and data processing is required."
        },
        {
            "id": "job_002",
            "title": "Full Stack Developer",
            "description": "Seeking a Full Stack Developer experienced in React and Node.js. Must be comfortable with frontend and backend development."
        }
    ]
    
    with open('data/resumes.json', 'w') as f:
        json.dump(resumes, f, indent=4)
    
    with open('data/job_descriptions.json', 'w') as f:
        json.dump(job_descriptions, f, indent=4)
        
    print("Mock data generated in data/ directory.")

if __name__ == "__main__":
    generate_mock_data()
