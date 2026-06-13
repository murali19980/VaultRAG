from fastapi import APIRouter, HTTPException
from backend.retrieval.vector_store import get_chroma_collection
from backend.retrieval.bm25_index import delete_document_from_bm25
import os

router = APIRouter(prefix="/documents", tags=["documents"])

@router.get("")
def list_documents():
    """Return unique filenames stored in ChromaDB."""
    try:
        collection = get_chroma_collection()  # uses CHROMA_COLLECTION = "vaultrag"
        # Retrieve all metadata to extract filenames
        all_data = collection.get(include=["metadatas"])
        filenames = set()
        if all_data and "metadatas" in all_data and all_data["metadatas"]:
            for meta in all_data["metadatas"]:
                if meta and "file_name" in meta:
                    filenames.add(meta["file_name"])
        return {"documents": sorted(list(filenames))}
    except Exception as e:
        # If collection doesn't exist or is empty, return empty list
        return {"documents": []}

@router.delete("/{file_name:path}")
def delete_document(file_name: str):
    """
    Delete all chunks belonging to a given file from:
    - ChromaDB
    - Whoosh BM25 index
    - Raw file from data/uploads/
    """
    try:
        collection = get_chroma_collection()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to connect to vector database: {str(e)}")

    # Find all IDs where metadata.file_name == file_name
    result = collection.get(where={"file_name": file_name}, include=["metadatas"])
    ids_to_delete = result.get("ids", [])
    if not ids_to_delete:
        raise HTTPException(status_code=404, detail="No document with that name found in the index")
    
    # Delete from Chroma
    collection.delete(ids=ids_to_delete)
    
    # Delete from BM25 (Whoosh) – we need to delete each chunk ID from the index
    for doc_id in ids_to_delete:
        delete_document_from_bm25(doc_id)
    
    # Clear query cache post-deletion
    try:
        from backend.api.chat import _get_or_create_query_engine
        engine = _get_or_create_query_engine()
        if hasattr(engine.retriever, "_retrieve_cached"):
            engine.retriever._retrieve_cached.cache_clear()
    except Exception:
        pass

    # Delete the raw file if it exists
    raw_path = os.path.join("data", "uploads", file_name)
    if os.path.exists(raw_path):
        try:
            os.remove(raw_path)
        except Exception as e:
            # Log error but don't fail, since index cleanup is primary
            pass
    
    return {"message": f"Deleted {file_name} (removed {len(ids_to_delete)} chunks)"}