from datetime import datetime
from typing import Dict, List
from bson import ObjectId


class Application:
    def __init__(self, companyName: str, position: str, location: str, jobDescription: str,
                 resumeFeedback: Dict, coverLetter: Dict, interviewQuestions: List[Dict], status: str):
        self.id = str(ObjectId())
        self.companyName = companyName
        self.position = position
        self.location = location
        self.jobDescription = jobDescription
        self.resumeFeedback = resumeFeedback 
        self.coverLetter = coverLetter
        self.interviewQuestions = interviewQuestions
        self.status = status
        self.dateCreated = datetime.utcnow()

    def to_dict(self):
        return {
            "id": self.id,
            "companyName": self.companyName,
            "position": self.position,
            "location": self.location,
            "jobDescription": self.jobDescription,
            "resumeFeedback": self.resumeFeedback,
            "coverLetter": self.coverLetter,
            "interviewQuestions": self.interviewQuestions,
            "status": self.status,
            "dateCreated": self.dateCreated
        }
