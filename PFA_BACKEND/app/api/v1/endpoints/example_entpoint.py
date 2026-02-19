from fastapi import APIRouter

router = APIRouter(
    prefix="/examples",
    tags=["Examples"]   # tag dla swaggera
)

@router.get("/")
def get_examples():
    return [{"id":1, "name": "Jan"}]

@router.get("/{example_id}")
def get_example(example_id: int):
    return {"id": example_id, "name": "jon"}