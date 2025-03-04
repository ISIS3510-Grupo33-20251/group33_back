from fastapi import APIRouter, HTTPException
from app.database import database
from app.models.flashcard_deck import FlashcardDeck
from bson import ObjectId

router = APIRouter(prefix="/flashcard_decks", tags=["Flashcard Decks"])

flashcard_decks_collection = database["flashcard_decks"]
users_collection = database["users"]  # To verify deck ownership

# Create a new flashcard deck
@router.post("/", response_model=FlashcardDeck)
async def create_flashcard_deck(deck: FlashcardDeck):
    deck_dict = deck.model_dump(by_alias=True, exclude={"deck_id"})
    result = await flashcard_decks_collection.insert_one(deck_dict)
    deck_dict["_id"] = str(result.inserted_id)
    return deck_dict

# Get all flashcard decks
@router.get("/")
async def get_flashcard_decks():
    decks = await flashcard_decks_collection.find().to_list(100)
    for deck in decks:
        deck["_id"] = str(deck["_id"])
    return decks

# Get a single flashcard deck by ID
@router.get("/{deck_id}")
async def get_flashcard_deck(deck_id: str):
    deck = await flashcard_decks_collection.find_one({"_id": ObjectId(deck_id)})
    if deck:
        deck["_id"] = str(deck["_id"])
        return deck
    raise HTTPException(status_code=404, detail="Flashcard deck not found")

# Update a flashcard deck by ID
@router.put("/{deck_id}")
async def update_flashcard_deck(deck_id: str, updated_deck: FlashcardDeck):
    deck_dict = updated_deck.model_dump(exclude_unset=True, by_alias=True)
    result = await flashcard_decks_collection.update_one({"_id": ObjectId(deck_id)}, {"$set": deck_dict})
    if result.matched_count:
        return {"message": "Flashcard deck updated successfully"}
    raise HTTPException(status_code=404, detail="Flashcard deck not found")

# Delete a flashcard deck by ID
@router.delete("/{deck_id}")
async def delete_flashcard_deck(deck_id: str):
    result = await flashcard_decks_collection.delete_one({"_id": ObjectId(deck_id)})
    if result.deleted_count:
        return {"message": "Flashcard deck deleted successfully"}
    raise HTTPException(status_code=404, detail="Flashcard deck not found")
