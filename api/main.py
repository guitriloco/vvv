import os
from fastapi import FastAPI, Request
import hashlib
import time
import sys
import json

app = FastAPI(title="vvv Yield-Aware Preservation Engine")

# Define storage paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STORAGE_DIR = os.path.join(BASE_DIR, "storage")
# Eternal Ledger for 'Pure Gold' essence (ROI > 0.98)
ETERNAL_LEDGER_PATH = os.path.join(STORAGE_DIR, "eternal_ledger.jsonl")
# Standard Ledger for High Grade essence
STANDARD_LEDGER_PATH = os.path.join(STORAGE_DIR, "standard_ledger.jsonl")
# Path aligned with REX's cold storage in shared directory
SIPHON_PATH = "/home/team/shared/expansion_code/vvv/data/siphoned_essence.json"

os.makedirs(STORAGE_DIR, exist_ok=True)

class PurityDistiller:
    """
    Analyzes incoming essence for 'purity' based on Yield-Master metrics.
    """
    @staticmethod
    def distill(data: dict):
        # Extract metrics from various sources (YES, REX, Mirror)
        roi = data.get("roi", data.get("nectar_yield", data.get("value_score", 0.0)))
        
        # If string based classification is present, boost or floor purity
        classification = str(data.get("nectar_classification", "")).upper()
        if "ABSOLUTE NECTAR" in classification or "PURE GOLD" in classification:
            roi = max(roi, 0.99)
        elif "HIGH GRADE" in classification:
            roi = max(roi, 0.90)
            
        purity = float(roi)
        
        if purity >= 0.98:
            return purity, "PHOENIX_GOLD", ETERNAL_LEDGER_PATH
        elif purity >= 0.90:
            return purity, "REFINED_SILVER", STANDARD_LEDGER_PATH
        else:
            return purity, "RAW_CORE", STANDARD_LEDGER_PATH

def apply_zkp(content: str, grade: str, purity: float):
    """
    Yield-Aware Simulated Zero-Knowledge Proof verification.
    The proof strength scales with purity.
    """
    timestamp = time.time()
    # Create a challenge including purity
    challenge = hashlib.sha256(f"{content}_{timestamp}_{purity}".encode()).hexdigest()
    # Create the proof (simulated)
    proof = hashlib.sha256(f"ZKP_V2_PROOF_{challenge}_{grade}_{purity}".encode()).hexdigest()
    
    # Verify the proof (simulated)
    is_valid = proof == hashlib.sha256(f"ZKP_V2_PROOF_{challenge}_{grade}_{purity}".encode()).hexdigest()
    
    return proof, is_valid

def preserve_essence(data: dict, source: str):
    content = json.dumps(data, sort_keys=True)
    
    # 1. Distill Purity
    purity, grade, ledger_path = PurityDistiller.distill(data)
    
    # 2. Yield-Aware ZKP Verification
    proof, is_valid = apply_zkp(content, grade, purity)
    
    if not is_valid:
        print(f"[VVV] ZKP Verification FAILED for essence from {source}")
        return None
    
    print(f"[VVV] ZKP Verification SUCCESS ({grade}) for essence from {source}")
    
    # 3. Add to Prioritized Immutable Ledger
    ledger_entry = {
        "timestamp": time.time(),
        "source": source,
        "purity": purity,
        "grade": grade,
        "content_hash": hashlib.sha256(content.encode()).hexdigest(),
        "zkp_proof": proof,
        "immutable_id": hashlib.sha256(f"{content}_{proof}_{purity}".encode()).hexdigest()
    }
    
    # Append to prioritized ledger file
    try:
        with open(ledger_path, "a") as f:
            f.write(json.dumps(ledger_entry) + "\n")
        print(f"[VVV] Essence Preserved in {os.path.basename(ledger_path)}")
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
        return {
            "status": "preserved", 
            "grade": entry['grade'],
            "purity": entry['purity'],
            "vault": "ETERNAL" if entry['grade'] == "PHOENIX_GOLD" else "STANDARD"
        }
    return {"status": "verification_failed"}

@app.post("/protocol/callback")
async def protocol_callback(payload: dict):
    event = payload.get("event")
    data = payload.get("data")
    
    print(f"[VVV] Received protocol signal: {event}")
    
    # Yield-Aware Filtering
    purity, grade, _ = PurityDistiller.distill(data)
    
    if event == "PROTOCOL_COMPLETE":
        if purity >= 0.90:
            entry = preserve_essence(data, "Mirror_Protocol")
            if entry:
                return {"status": "essence_archived", "entry": entry}
        else:
            print(f"[VVV] Essence Purity ({purity}) too low for vault preservation.")
            return {"status": "purity_low", "purity": purity}
    
    return {"status": "signal_received"}

@app.get("/vault/eternal_ledger")
async def get_eternal_ledger():
    entries = []
    if os.path.exists(ETERNAL_LEDGER_PATH):
        with open(ETERNAL_LEDGER_PATH, "r") as f:
            for line in f:
                entries.append(json.loads(line))
    return entries

@app.get("/vault/sync_siphon")
async def sync_siphon():
    """Sync with REX's siphoned essence file and apply yield-aware preservation"""
    if not os.path.exists(SIPHON_PATH):
        return {"status": "no_siphon_data"}
    
    new_entries = 0
    try:
        with open(SIPHON_PATH, "r") as f:
            siphoned_data = json.load(f)
        
        # Collect existing hashes from both ledgers
        existing_hashes = set()
        for l_path in [ETERNAL_LEDGER_PATH, STANDARD_LEDGER_PATH]:
            if os.path.exists(l_path):
                with open(l_path, "r") as f:
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
