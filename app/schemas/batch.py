from pydantic import BaseModel
from datetime import datetime

class BatchBase(BaseModel):
    batch_year:int

class BatchCreate(BatchBase):
    pass

class BatchUpdate(BatchBase):
    pass

class BatchResponse(BatchBase):
    id:int
    created_at:datetime
    updated_at:datetime
    model_config = {"from_attributes":True}
