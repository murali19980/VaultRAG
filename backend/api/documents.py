from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.retrieval.vector_store import get_chroma_collection
from backend.retrieval.bm25_index import delete_document_from_bm25
import os

class RenameRequest(BaseModel):
    old_name: str
    new_name: str

class FolderUpdateRequest(BaseModel):
    folder: str

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

@router.get("/{file_name:path}/metadata")
def get_document_metadata(file_name: str):
    """
    Get file size, upload time (creation time) from the filesystem, and folder info from Chroma.
    """
    raw_path = os.path.join("data", "uploads", file_name)
    if not os.path.exists(raw_path):
        raise HTTPException(status_code=404, detail="File not found on disk")
    
    stat_info = os.stat(raw_path)
    size_bytes = stat_info.st_size
    creation_time = os.path.getctime(raw_path)
    
    from datetime import datetime
    creation_date = datetime.fromtimestamp(creation_time).isoformat()
    
    # Get folder from Chroma
    folder = "Default"
    try:
        collection = get_chroma_collection()
        result = collection.get(where={"file_name": file_name}, limit=1, include=["metadatas"])
        if result and "metadatas" in result and result["metadatas"]:
            folder = result["metadatas"][0].get("folder", "Default")
    except Exception:
        pass
    
    return {
        "file_name": file_name,
        "size_bytes": size_bytes,
        "upload_date": creation_date,
        "folder": folder
    }

@router.post("/rename")
def rename_document(req: RenameRequest):
    old_name = req.old_name
    new_name = req.new_name
    
    if not old_name or not new_name:
        raise HTTPException(status_code=400, detail="old_name and new_name are required")
        
    # 1. Rename physical file
    old_path = os.path.join("data", "uploads", old_name)
    new_path = os.path.join("data", "uploads", new_name)
    if os.path.exists(old_path):
        try:
            os.rename(old_path, new_path)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to rename file on disk: {str(e)}")
            
    # 2. Update ChromaDB
    try:
        collection = get_chroma_collection()
        result = collection.get(where={"file_name": old_name}, include=["metadatas", "documents"])
        ids = result.get("ids", [])
        metadatas = result.get("metadatas", [])
        documents = result.get("documents", [])
        
        if ids:
            for meta in metadatas:
                meta["file_name"] = new_name
                if "file_path" in meta:
                    meta["file_path"] = os.path.join("data", "uploads", new_name)
            collection.update(ids=ids, metadatas=metadatas)
            
            # 3. Update BM25 Whoosh
            from backend.retrieval.bm25_index import BM25Index
            bm25 = BM25Index()
            bm25_docs = []
            for i in range(len(ids)):
                bm25_docs.append({
                    "doc_id": ids[i],
                    "text": documents[i],
                    "metadata": metadatas[i]
                })
            bm25.add_documents(bm25_docs)
            
            # Clear cache
            try:
                from backend.api.chat import _get_or_create_query_engine
                engine = _get_or_create_query_engine()
                if hasattr(engine.retriever, "_retrieve_cached"):
                    engine.retriever._retrieve_cached.cache_clear()
            except Exception:
                pass
                
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database update failed: {str(e)}")
        
    return {"message": f"Successfully renamed {old_name} to {new_name}"}

@router.patch("/{file_name:path}/folder")
def update_document_folder(file_name: str, req: FolderUpdateRequest):
    try:
        collection = get_chroma_collection()
        result = collection.get(where={"file_name": file_name}, include=["metadatas", "documents"])
        ids = result.get("ids", [])
        metadatas = result.get("metadatas", [])
        documents = result.get("documents", [])
        
        if not ids:
            raise HTTPException(status_code=404, detail="Document not found")
            
        for meta in metadatas:
            meta["folder"] = req.folder
            
        collection.update(ids=ids, metadatas=metadatas)
        
        # Update Whoosh BM25
        from backend.retrieval.bm25_index import BM25Index
        bm25 = BM25Index()
        bm25_docs = []
        for i in range(len(ids)):
            bm25_docs.append({
                "doc_id": ids[i],
                "text": documents[i],
                "metadata": metadatas[i]
            })
        bm25.add_documents(bm25_docs)
        
        # Clear cache
        try:
            from backend.api.chat import _get_or_create_query_engine
            engine = _get_or_create_query_engine()
            if hasattr(engine.retriever, "_retrieve_cached"):
                engine.retriever._retrieve_cached.cache_clear()
        except Exception:
            pass
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database update failed: {str(e)}")
        
    return {"message": f"Moved {file_name} to folder '{req.folder}'"}