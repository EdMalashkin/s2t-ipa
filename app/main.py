from fastapi import FastAPI, Request, Query, HTTPException
from fastapi.responses import JSONResponse
from .json_ipa import JsonIPA

# Initialize FastAPI app
app = FastAPI(
    title="IPA Transcription API",
    description="API for adding IPA transcription to JSON files",
    version="1.0.0"
)

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "IPA Transcription API", "status": "running"}

@app.get("/health")
async def health_check():
    """Health check endpoint for Docker"""
    return {"status": "healthy", "service": "s2t-ipa"}

@app.post("/ipa")
async def add_ipa(
    request: Request,
    lang: str = Query(...),       # required parameter
    token_field: str = Query("lemma")  # field to process in tokens, default "lemma"
):
    try:
        data_json = await request.json()
        l = JsonIPA(data_json, lang, token_field)
        result = l.process_bulc()
        return JSONResponse(content=result, media_type="application/json")
    except Exception as err:
        raise HTTPException(status_code=500, detail=str(err))

@app.delete("/cache")
async def clean_cache():
    """Clean all cached files to free up disk space"""
    try:
        result = JsonIPA.clean_all_cache()
        
        if result["success"]:
            return {
                "message": result["message"],
                "cleaned": True,
                "files_removed": result["files_removed"],
                "space_freed": result["space_freed_formatted"]
            }
        else:
            raise HTTPException(status_code=500, detail=result["message"])
            
    except Exception as err:
        raise HTTPException(status_code=500, detail=f"Failed to clean cache: {str(err)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
