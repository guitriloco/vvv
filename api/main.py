import os
from fastapi import FastAPI, Request
import hashlib
import time
import sys
import json

app = FastAPI(title="vvv Vault Preservation Engine")

# Define storage paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STORAGE_DIR = os.path.join(BASE_DIR, "storage")
LEDGER_PATH = os.path.join(STORAGE_DIR, "immutable_ledger.jsonl")
# Path aligned with REX's cold storage
SIPHON_PATH = os.path.join(BASE_DIR, "data", "siphoned_essence.json")

os.makedirs(STORAGE_DIR, exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, "data"), exist_ok=True)

def apply_zkp(content: str, grade: str):
    """
    Simulated Zero-Knowledge Proof verification.
    In a real system, this would involve a cryptographic proof 
    that the content meets the 'Pure Gold' criteria without revealing the logic.
    """
    timestamp = time.time()
    # Create a challenge
    challenge = hashlib.sha256(f"{content}_{timestamp}".encode()).hexdigest()
    # Create the proof (simulated)
    proof = hashlib.sha256(f"ZKP_PROOF_{challenge}_{grade}".encode()).hexdigest()
    
    # Verify the proof (simulated)
    is_valid = proof == hashlib.sha256(f"ZKP_PROOF_{challenge}_{grade}".encode()).hexdigest()
    
    return proof, is_valid

def preserve_essence(data: dict, source: str):
    content = json.dumps(data, sort_keys=True)
    grade = str(data.get("Pure_Gold", data.get("nectar_classification", "Standard")))
    
    # 1. ZKP Verification
    proof, is_valid = apply_zkp(content, grade)
    
    if not is_valid:
        print(f"[VVV] ZKP Verification FAILED for essence from {source}")
        return None
    
    print(f"[VVV] ZKP Verification SUCCESS for essence from {source}")
    
    # 2. Add to Immutable Ledger
    ledger_entry = {
        "timestamp": time.time(),
        "source": source,
        "grade": grade,
        "content_hash": hashlib.sha256(content.encode()).hexdigest(),
        "zkp_proof": proof,
        "immutable_id": hashlib.sha256(f"{content}_{proof}".encode()).hexdigest()
    }
    
    # Append to local ledger file
    try:
        with open(LEDGER_PATH, "a") as f:
            f.write(json.dumps(ledger_entry) + "\n")
    except Exception as e:
        print(f"[VVV] Ledger Write Error: {e}")

    return ledger_entry

@app.post("/vault/ingest")
async def ingest_wealth(payload: dict):
    """General endpoint for incoming technical wealth (REX, YES, etc.)"""
    source = payload.get("source", "Unknown")
    data = payload.get("data", {})
    
    print(f"[VVV] Ingesting technical wealth from {source}")
    entry = preserve_essence(data, source)
    
    if entry:
        return {"status": "preserved", "immutable_id": entry['immutable_id']}
    return {"status": "verification_failed"}

@app.post("/protocol/callback")
async def protocol_callback(payload: dict):
    event = payload.get("event")
    data = payload.get("data")
    
    print(f"[VVV] Received protocol signal: {event}")
    
    # Handle Pure Gold or Absolute Nectar
    is_valuable = (
        "Pure_Gold" in data or 
        data.get("is_absolute_nectar") == True or 
        "Absolute Nectar" in str(data.get("nectar_classification", ""))
    )
    
    if event == "PROTOCOL_COMPLETE" and is_valuable:
        source = "Mirror_Protocol"
        entry = preserve_essence(data, source)
        if entry:
            return {"status": "essence_archived", "entry": entry}
    
    return {"status": "signal_received"}

@app.get("/vault/ledger")
async def get_ledger():
    entries = []
    if os.path.exists(LEDGER_PATH):
        with open(LEDGER_PATH, "r") as f:
            for line in f:
                entries.append(json.loads(line))
    return entries

@app.get("/vault/sync_siphon")
async def sync_siphon():
    """Sync with REX's siphoned essence file and apply ZKP to all entries"""
    if not os.path.exists(SIPHON_PATH):
        return {"status": "no_siphon_data"}
    
    new_entries = 0
    try:
        with open(SIPHON_PATH, "r") as f:
            siphoned_data = json.load(f)
        
        # Check existing ledger for already archived hashes
        existing_hashes = set()
        if os.path.exists(LEDGER_PATH):
            with open(LEDGER_PATH, "r") as f:
                for line in f:
                    existing_hashes.add(json.loads(line).get("content_hash"))
        
        for entry in siphoned_data:
            content_hash = hashlib.sha256(json.dumps(entry, sort_keys=True).encode()).hexdigest()
            if content_hash not in existing_hashes:
                preserve_essence(entry, "REX_SIPHON")
                new_entries += 1
                
        return {"status": "synced", "new_entries": new_entries}
    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
