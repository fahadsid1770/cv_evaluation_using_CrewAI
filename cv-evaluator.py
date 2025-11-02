import os
import json
from fastapi import FastAPI, HTTPException
from pymongo import MongoClient
from bson import ObjectId
import uvicorn
from typing import Dict, Any, List
import json
from datetime import datetime
from typing import Dict, Any


import warnings
warnings.filterwarnings('ignore')


from crewai import Agent, Crew, Process, Task

class CVEvaluatorCrewExecutor:
    def __init__(self, mongo_uri: str, db_name: str, input_collection: str, output_collection: str):
        try:
            self.client = MongoClient(mongo_uri)
            self.db = self.client[db_name]
            self.input_collection = self.db[input_collection]
            self.output_collection = self.db[output_collection]
            print("Successfully connected to MongoDB.")
        except Exception as e:
            raise ConnectionError(f"Failed to connect to MongoDB: {e}")

        #Initializing agents and tasks
        self._initialize_crew()

    def _initialize_crew(self):
        self.credentials_analyst = Agent(
            role='Expert Academic & Professional Credentials Analyst',
            goal="""To meticulously evaluate a candidate's CV based on their academic degrees, publications, 
                  citation record, and awards. Provide a score from 1-10 for their credentials.""",
            backstory="""You are a seasoned evaluator for prestigious grant committees and top-tier university 
                       admissions. You have a keen eye for quantifying a person's track record and professional standing.""",
            verbose=True,
            allow_delegation=False
        )
        self.national_importance_analyst = Agent(
            role='U.S. Strategic Interest & Policy Analyst',
            goal="""To analyze a candidate's field of work and determine its alignment with the current national 
                  interests of the United States. Provide a 'National Importance Score' from 1-10.""",
            backstory="""You are a policy advisor who constantly monitors governmental reports and strategic initiatives 
                       from the White House, NSF, DOE, and DHS to identify critical fields like AI, semiconductors, 
                       clean energy, and national security.""",
            verbose=True,
            allow_delegation=False
        )
        
        self.lead_adjudicator = Agent(
            role='Chief Immigration Adjudicator for NIW Cases',
            goal="""To oversee the evaluation of an NIW candidate, synthesize analyses on credentials and national 
                  importance, calculate a final score, and write a concise final recommendation.""",
            backstory="""You are a senior officer responsible for making final decisions on National Interest Waiver 
                       petitions. You delegate detailed analysis to your specialist team and then integrate their 
                       findings to form a holistic, evidence-based judgment.""",
            verbose=True,
            allow_delegation=True # This agent can delegate/manage the others
        )

        self.credentials_analysis_task = Task(
            description="""
            Analyze the provided CV text and score the candidate's credentials on a 1-10 scale.
            Use the following scoring model:
            - High Score (8-10): PhD from a reputable university, numerous publications in top-tier journals, high citation count (top 5-10%), major awards, or significant grant funding.
            - Medium Score (5-7): Master's or PhD, solid publication record, moderate citations, some minor awards.
            - Low Score (1-4): Basic advanced degree, minimal publications, low citations, no significant awards.
            
            Provide ONLY the score and a 1-sentence justification.

            Candidate CV:
            ---
            {cv_text}
            ---
            """,
            expected_output="A score (e.g., 'Credentials Score: 8/10') and a single-sentence justification for the rating.",
            agent=self.credentials_analyst
        )

        self.importance_analysis_task = Task(
            description="""
            Analyze the candidate's field of endeavor described in the CV and score its national importance to the U.S. on a 1-10 scale. 
            Consider the current date is July 2025.
            Use the following scoring model:
            - High Score (8-10): Work directly addresses critical U.S. priorities like AI development, semiconductor manufacturing, national security, specific cancer research, or clean energy.
            - Medium Score (5-7): Work contributes to an important field like general healthcare, economic growth, or education, but the impact is less immediate.
            - Low Score (1-4): The benefit to the U.S. is abstract, indirect, or not clearly articulated.

            Provide ONLY the score and a 1-sentence justification.

            Candidate CV:
            ---
            {cv_text}
            ---
            """,
            expected_output="A score (e.g., 'National Importance Score: 9/10') and a single-sentence justification for the rating.",
            agent=self.national_importance_analyst
        )

        self.final_evaluation_task = Task(
            description="""
            Synthesize the reports from the Credentials Analyst and the National Importance Analyst to produce a final evaluation.
            1. Extract the two scores from the context provided.
            2. Calculate the final weighted score using the formula: Final Score = (Credentials Score × 0.6) + (National Importance Score × 0.4).
            3. Based on the final score (e.g., >7 is Strong, 5-7 is Moderate, <5 is Weak), write a one-line overall rating.
            4. Write a 1-3 line paragraph explaining the reasons for this rating, summarizing the key strengths and weaknesses from the analysts' reports.
            """,
            expected_output="""
            A final report containing two parts:
            1. A single line with the overall rating (e.g., "Overall Rating: Strong Candidate for NIW").
            2. A 1-3 line paragraph detailing the justification for the rating.
            """,
            agent=self.lead_adjudicator,
            context=[self.credentials_analysis_task, self.importance_analysis_task]
        )

    def _load_and_process_inputs_as_paragraph(self, document_id: str) -> Dict[str, str]:
        print(f"Fetching document with ID: {document_id}")
        data = self.input_collection.find_one({"_id": ObjectId(document_id)})
        
        if not data:
            raise ValueError(f"No document found with ID {document_id}")
        
        cv_info = data.get('cv_info', {})
        cv_parts: List[str] = []
        cv_parts.append("Curriculum Vitae for Mohammad Sajib Al Seraj")
        
        if summary := cv_info.get('summary'):
            cv_parts.append(f"\n## Professional Summary\n{summary}")

        # Process work experience
        if work_experience := cv_info.get('work_experience'):
            cv_parts.append("\n## Work Experience")
            for job in work_experience:
                title = job.get('title', 'N/A')
                company = job.get('company', 'N/A')
                dates = job.get('dates', 'N/A')
                description = job.get('description', '')
                cv_parts.append(f"- **{title}** at {company} ({dates})\n  {description}")

        # Process education
        if education := cv_info.get('education'):
            cv_parts.append("\n## Education")
            for edu in education:
                degree = edu.get('degree', 'N/A')
                institution = edu.get('institution', 'N/A')
                dates = edu.get('year', 'N/A')
                cv_parts.append(f"- {degree}, {institution} ({dates})")

        # Process publications
        if publications := cv_info.get('publications'):
            cv_parts.append("\n## Publications")
            for pub in publications:
                title = pub.get('title', 'N/A')
                journal = pub.get('journal', 'N/A')
                cv_parts.append(f"- {title} - *{journal}*")

        # Process simple list-based fields (e.g., skills)
        if skills := cv_info.get('skills'):
            cv_parts.append(f"\n## Skills\n{', '.join(skills)}")

        # Join all parts into a single string
        full_cv_text = "\n".join(cv_parts)
        
        print("Inputs loaded and processed successfully as a single paragraph.")
        
        # Return in the format CrewAI expects for inputs
        return {'cv_text': full_cv_text}


    def execute(self, document_id: str) -> Dict[str, Any]:
        try:
            inputs = self._load_and_process_inputs_as_paragraph(document_id)
            crew = Crew(
                agents=[self.credentials_analyst, self.national_importance_analyst, self.lead_adjudicator],
                tasks=[self.credentials_analysis_task, self.importance_analysis_task, self.final_evaluation_task],
                process=Process.sequential,
                verbose=True
            )
            print("Kicking off the crew...")
            final_result = crew.kickoff(inputs=inputs)
            print("Crew execution finished.")
            task_outputs = {}
            for i, task in enumerate(crew.tasks):
                task_name = f"task_{i+1}"
                task_outputs[task_name] = task.output.raw

            #Saving outputs to MongoDB
            print("Saving outputs to MongoDB...")
            output_document = {
                "source_document_id": ObjectId(document_id),
                "status": "completed",
                "results": task_outputs
            }
            
            result = self.output_collection.update_one(
                {"source_document_id": ObjectId(document_id)},
                {"$set": output_document},
                upsert=True
            )
            
            # Fetch the saved document to return its ID
            saved_doc = self.output_collection.find_one({"source_document_id": ObjectId(document_id)})

            print("All tasks completed and results saved.")
            
            # 5. Return the result, ensuring ObjectIds are strings for JSON serialization
            if saved_doc:
                saved_doc['_id'] = str(saved_doc['_id'])
                saved_doc['source_document_id'] = str(saved_doc['source_document_id'])
                return saved_doc
            else:
                 raise Exception("Failed to save or retrieve the output document.")


        except ValueError as ve:
            raise HTTPException(status_code=404, detail=str(ve))
        except Exception as e:
            # Save error status to MongoDB
            self.output_collection.update_one(
                {"source_document_id": ObjectId(document_id)},
                {"$set": {"status": "failed", "error": str(e)}},
                upsert=True
            )
            raise HTTPException(status_code=500, detail=f"An error occurred during crew execution: {e}")


#MongoDB Connection Details
MONGO_URI = "mongodb+srv://fahad1770:asdf1234@cluster0.gdqu6ee.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
DB_NAME = "applicant_information"
INPUT_COLLECTION = "applicant_information"
OUTPUT_COLLECTION = "cv-evaluation-result"

# Initialize FastAPI app
app = FastAPI(
    title="CrewAI Service",
    description="An API to trigger a  crew that reads from and writes to MongoDB."
)

# Instantiate the executor once when the application starts
crew_executor = None
try:
    crew_executor = CVEvaluatorCrewExecutor(
        mongo_uri=MONGO_URI,
        db_name=DB_NAME,
        input_collection=INPUT_COLLECTION,
        output_collection=OUTPUT_COLLECTION
    )
except ConnectionError as e:
    print(e)

@app.on_event("startup")
async def startup_event():
    if crew_executor is None:
        raise RuntimeError("Could not connect to MongoDB. Application startup failed.")
    print("FastAPI application started.")

@app.post("/run-cv-evaluation/{document_id}", tags=["Crew Execution"])
async def run_drafting_crew(document_id: str):
    if not ObjectId.is_valid(document_id):
        raise HTTPException(status_code=400, detail="Invalid MongoDB ObjectId format.")
    
    result = crew_executor.execute(document_id)
    return {"message": "Crew executed successfully!", "output": result}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

    

