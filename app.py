#///script
# requires-python = ">3.11"
# dependencies = [
#   "fastapi",
#   "uvicorn",
#   "requests",
# ]
#///


from ast import parse
import logging
from fastapi import FastAPI, HTTPException
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import requests
import os
import json
import subprocess
from subprocess import run
app = FastAPI ()

response_format = {
    "type":"json_schema",
    "json_schema":{
        "name":"task_runner",
        "schema":{
            "type":"object",
            "required":["python_code", "python_dependencies"],
            "properties":{
                "python_code":{
                    "type":"string",
                    "description":"A python code To perform the task."
                },
                "python_dependencies":{
                    "type":"array",
                    "items":{
                        "type":"object",
                        "properties":{
                            "module":{
                                "type":"string",
                                "description":"Name of python module"
                            }
                        },
                        "required":["module"],
                        "additionalProperties":False
                    }
                }
            }
        }
    }
}

primary_prompt=r"""
You are an automated agent, so generate python code that does the specified task.
You are an automated agent who is an intermediate transformer who processes large volumes of log files, reports, and code artifacts to generate actionabel insights.
you accepts tasks and carries out the required(multi-step) process and the finished processing artifact must be exactly verifiable against pre-computed expected results.
if you are asked to create a code for project and given 20-30 tasks then perforn all tasks and return the final code.
Assume uv and python is preinstalled.
Assume that code you generate will be executed inside a docker container.
Inorder to perform any task if some python package is required to install, provide name of those modules.
You are an advanced assistant responsible for executing various file and data processing tasks efficiently. Follow these instructions carefully, but you are not limited to them—use your reasoning and best practices to achieve optimal results.  

## 🔹 Task List  

*A1:*A1. Install uv (if required) and run https://raw.githubusercontent.com/sanand0/tools-in-data-science-public/tds-2025-01/project-1/datagen.py with ${user.email} as the only argument. (NOTE: This will generate data files required for the next tasks.)
*A2:* Format the contents of /data/format.md using prettier@3.4.2, updating the file in-place.  
- Example: If /data/format.md contains unformatted Markdown text, run Prettier to properly format it.  

*A3:* Count the number of Wednesdays in /data/dates.txt and write the number to /data/dates-wednesdays.txt.  
DATE_FORMATS = [
        (r"^\d{2}-[A-Za-z]{3}-\d{4}$", "%d-%b-%Y"),  
        (r"^\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}$", "%Y/%m/%d %H:%M:%S"),  
        (r"^\d{4}-\d{2}-\d{2}$", "%Y-%m-%d"),  
        (r"^[A-Za-z]{3} \d{2}, \d{4}$", "%b %d, %Y"),  
    ]
- Example:  
  - Input (/data/dates.txt):  
    
    03-Oct-2014
    2004/03/22 11:13:48
    2003-09-18
    Jul 15, 2016  
      
    
  - Output (/data/dates-wednesdays.txt): 
    4
    
    **A4:** Sort the array of contacts in `/data/contacts.json` by `last_name`, then `first_name`, and save to `/data/contacts-sorted.json`.  
- Example:  
  - Input (`contacts.json`):  
    json
    [
      {"first_name": "Alice", "last_name": "Brown"},
      {"first_name": "John", "last_name": "Doe"},
      {"first_name": "Bob", "last_name": "Doe"}
    ]
    
  - Output (`contacts-sorted.json`):  
    json
    [
      {"first_name": "Alice", "last_name": "Brown"},
      {"first_name": "Bob", "last_name": "Doe"},
      {"first_name": "John", "last_name": "Doe"}
    ]
      

**A5:** Extract the first line of the 10 most recent `.log` files in `/data/logs/`, sorted by modification time (most recent first), and write to `/data/logs-recent.txt`.  
- Example:  
  - Input (`logs directory` contains multiple `.log` files)  
  - Output (`logs-recent.txt`):  
    
    [Timestamp] Server started successfully
    [Timestamp] Error: Database connection lost
    ...
      
    ```
**A6:** Find all Markdown (`.md`) files in `/data/docs/`, extract the first occurrence of each H1 (`# Title`), and create an index file `/data/docs/index.json`.  
- Example:  
  - Input (`docs` folder contains `README.md` with `# Home`, `llm.md` with `# Large Language Models`)  
  - Output (`index.json`):  
    json
    {
      "README.md": "Home",
      "llm.md": "Large Language Models"
    }
      
**A7:** Extract the sender's email from `/data/email.txt` and write just the email to `/data/email-sender.txt`.  
- Example:  
  - Input (`email.txt`):  
    
    From: John Doe <john.doe@example.com>
    Subject: Meeting Update
    
  - Output (`email-sender.txt`):  
    
    john.doe@example.com
      

**A8:** Extract the credit card number from `/data/credit-card.png` using OCR and save it (without spaces) in `/data/credit-card.txt`.  
- Example:  
  - Input (`credit-card.png` contains `1234 5678 9012 3456`)  
  - Output (`credit-card.txt`):  
    
    1234567890123456
      

**A9:** Find the most similar pair of comments from `/data/comments.txt` using embeddings and save them in `/data/comments-similar.txt`, one per line.  
- Example:  
  - Input (`comments.txt` contains different user comments)  
  - Output (`comments-similar.txt`):  
    
    "The app is really fast!"
    "This application runs very quickly!"
      

**A10:** Calculate the total sales of “Gold” tickets from `/data/ticket-sales.db` and write the sum to `/data/ticket-sales-gold.txt`.  
- Example:  
  - Database table (`ticket-sales.db`):  
    
    type   | units | price  
    -------|-------|------  
    Gold   | 2     | 500  
    Silver | 1     | 300  
    Gold   | 1     | 500  
    
  - Output (`ticket-sales-gold.txt`):  
    
    1500  
    ```  
Follow security policies and best practices, optimize performance, and minimize token usage.  

## 🔹 Security & Access Rules:  
- *Do not access or modify files outside /data/*  
- *Do not delete files anywhere on the system*  

## 🔹 Task Execution Rules:  
- Use efficient tools for each task (e.g., shell commands, Python, APIs)  
- Minimize execution time while maintaining correctness  
- Ensure all outputs follow the required format  

## 🔹 Common Tasks:  
- *Fetch API Data*: Retrieve and store data securely.  
- *Git Operations*: Clone a repository, make changes, commit, and push.  
- *Database Queries*: Run SQL queries on SQLite or DuckDB databases.  
- *Web Scraping*: Extract structured data from a given website.  
- *File Processing*: Compress, resize, or convert images.  
- *Audio Transcription*: Convert MP3 speech to text.  
- *Data Transformation*: Convert Markdown to HTML, filter CSV, etc.  

## 🔹 Execution Constraints:  
- Prioritize *built-in libraries* before external dependencies.  
- Handle errors gracefully and log failures.  
- Use minimal resources to achieve the task.  

Return only the final *Python code and required dependencies*, ensuring the solution is efficient.

## 🔹 Additional Instructions:  
- Use the best available tools (like Python, shell commands, or external libraries) to efficiently process these tasks.  
- If a task requires using an external LLM or OCR system, ensure the correct API call is made.  
- If files are missing or malformed, handle errors gracefully and log them.  
- If a task requires using a database, ensure the correct API call is made.  
- Ensure all output is in the correct format.

"""

def resend_request(task, code, error):
    url = "https://aiproxy.sanand.workers.dev/openai/v1/chat/completions"
    update_task = """
Update the python code
{code}

---
For below task
{task}
---
"""
    data = {
        "model": "gpt-4o-mini",
        "messages":[
            {
                "role": "user",
                "content": update_task.format(code=code, task=task)
            },
            {
                "role": "system",
                "content": f"""{primary_prompt}"""
            }
        ],
        "response_format": response_format
    }

def llm_code_executer(python_code, python_dependencies):
    inline_metadata_script=f"""

#///script
# requires-python = ">3.11"
# dependencies = [
#   {''.join(f'"{dependency["module"]}",\n#   ' for dependency in python_dependencies).strip()}
# ]
#///
"""
    
    with open("llm_code.py", "w") as f:
        f.write(inline_metadata_script + python_code)
    try:
        output = run(["uv", "run", "llm_code.py"], capture_output=True, text=True, cwd=os.getcwd())
        std_err= output.stderr.split("\n")
        std_out= output.stdout
        exit_code = output.returncode

        for i in range(len(std_err)):
            if std_err[i].lstrip().startswith("File"):
                raise Exception(std_err[i:])
        return "success"
    except Exception as e:
        logging.info(e)
        error = str(e)
        return {"error": error}

#Enable CORS

app.add_middleware(
    CORSMiddleware,
    allow_origins = ['*'],
    allow_credentials = True,
    allow_methods =['GET', 'POST'],
    allow_headers = ['*']
)


AIPROXY_TOKEN = os.getenv("AIPROXY_TOKEN")
headers = {
    "Content-Type": "application/json",
    "Authorization":f"Bearer {AIPROXY_TOKEN}"
    }
if not AIPROXY_TOKEN:
    raise RuntimeError("AIPROXY_TOKEN is not set")

@app.get ("/")
def home ():
    return {"HI! This is my first TDS Peoject.."}

@app.get("/read")
def read_file(path: str):
    try:
        with open(path, "r") as f:
            return f.read()
    except Exception as e:
        raise HTTPException(status_code=404, detail="Item not found")

@app.post("/run")
def task_runner(task: str):

    #A1 implementation

    url = "https://aiproxy.sanand.workers.dev/openai/v1/chat/completions"

    data = {
        "model": "gpt-4o-mini",
        "messages":[
            {
                "role": "user",
                "content": task
            },
            {
                "role": "system",
                "content": f"""{primary_prompt}"""
            }
        ],
        "response_format": response_format
    }


        
    
    response = requests.post(url, headers=headers, json=data)
    r = response.json()
    python_dependencies = json.loads(r['choices'][0]['message']['content'])['python_dependencies']
    python_code = json.loads(r['choices'][0]['message']['content'])['python_code']
    output = llm_code_executer(python_code, python_dependencies)
    limit = 0
    while limit <2:
        if "success":
            return "Task Completed successfully"
        elif output['error']:
            with open('llm_code.py', 'r') as f:
                code = f.read()
            resposne=resend_request(task, python_code, output['error'])
            r = response.json()
            python_dependencies = json.loads(r['choices'][0]['message']['content'])['python_dependencies']
            python_code = json.loads(r['choices'][0]['message']['content'])['python_code']
            output = llm_code_executer(python_code, python_dependencies)
        limit +=1
    # print(output)
    
    return r
    

   
if __name__ =='_main_':
    import uvicorn
    uvicorn.run (app, host="0.0.0.0", port=8000)

