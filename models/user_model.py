from datetime import datetime
from typing import List, Dict
from bson import ObjectId

class User:
    def __init__(self, userId: str, email: str, firstName: str, lastName: str, resume: str, applications: List[Dict]):
        self._id = ObjectId()
        self.userId = userId
        self.email = email
        self.firstName = firstName
        self.lastName = lastName
        self.resume = resume
        self.applications = applications  # List of embedded Application objects
        self.createdAt = datetime.utcnow()
        self.updatedAt = datetime.utcnow()

    def to_dict(self):
        return {
            "_id": str(self._id),
            "userId": self.userId,
            "email": self.email,
            "firstName": self.firstName,
            "lastName": self.lastName,
            "resume": self.resume,
            "applications": [app.to_dict() for app in self.applications],
            "createdAt": self.createdAt,
            "updatedAt": self.updatedAt
        }
