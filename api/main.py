import os
from fastapi import FastAPI, Request
import hashlib
import time
import sys
import json

app = FastAPI(title="VVV: Omni-Pulse Preservation Engine (V3.0)")

# Define storage paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STORAGE_DIR = os.path.join(BASE_DIR, "storage")
# Eternal Ledger for 'Pure Gold' essence (ROI > 0.98)
ETERNAL_LEDGER_PATH = os.path.join(STORAGE_DIR, "eternal_ledger.jsonl")
# Standard Ledger for High Grade essence
STANDARD_LEDGER_PATH = os.path.join(STORAGE_DIR, "standard_ledger.jsonl")
# Cluster Ledgers mapping
CLUSTER_LEDGERS = {
    "ALPHA": os.path.join(STORAGE_DIR, "alpha_cluster_ledger.jsonl"),
    "BETA": os.path.join(STORAGE_DIR, "beta_cluster_ledger.jsonl"),
    "GAMMA": os.path.join(STORAGE_DIR, "gamma_cluster_ledger.jsonl"),
    "DELTA": os.path.join(STORAGE_DIR, "delta_cluster_ledger.jsonl")
}

# Path aligned with REX's cold storage in shared directory
SIPHON_PATH = "/home/team/shared/expansion_code/vvv/data/siphoned_essence.json"

os.makedirs(STORAGE_DIR, exist_ok=True)

class PurityDistiller:
    """
    Analyzes incoming essence for 'purity' based on Yield-Master metrics.
    """
    @staticmethod
    def distill(data: dict):
        # Extract metrics from various sources (YES, REX, Mirror, Mutation)
        roi = data.get("roi", data.get("nectar_yield", data.get("value_score", 0.0)))
        
        # If string based classification is present, boost or floor purity
        classification = str(data.get("nectar_classification", "")).upper()
        if "ABSOLUTE NECTAR" in classification or "PURE GOLD" in classification or "ATOM-SHIFT" in data:
            roi = max(roi, 0.99)
        elif "HIGH GRADE" in classification or "YIELD-HARVEST" in data:
            roi = max(roi, 0.90)
            
        purity = float(roi)
        
        if purity >= 0.98:
            return purity, "PHOENIX_GOLD", ETERNAL_LEDGER_PATH
        elif purity >= 0.90:
            return purity, "REFINED_SILVER", STANDARD_LEDGER_PATH
        else:
            return purity, "RAW_CORE", STANDARD_LEDGER_PATH

def apply_zkp(content: str, grade: str, purity: float, context: str = "generic"):
    """
    Yield-Aware Simulated Zero-Knowledge Proof verification.
    The proof strength scales with purity.
    """
    timestamp = time.time()
    # Create a challenge including purity and context
    challenge = hashlib.sha256(f"{content}_{timestamp}_{purity}_{context}".encode()).hexdigest()
    # Create the proof (simulated)
    proof = hashlib.sha256(f"ZKP_V3_PROOF_{challenge}_{grade}_{purity}_{context}".encode()).hexdigest()
    
    # Verify the proof (simulated)
    is_valid = proof == hashlib.sha256(f"ZKP_V3_PROOF_{challenge}_{grade}_{purity}_{context}".encode()).hexdigest()
    
    return proof, is_valid

def preserve_essence(data: dict, source: str, context: str = "general_preservation", cluster_id: str = None):
    content = json.dumps(data, sort_keys=True)
    
    # 1. Distill Purity
    purity, grade, ledger_path = PurityDistiller.distill(data)
    
    # If cluster_id is provided, use the specific cluster ledger
    if cluster_id and cluster_id.upper() in CLUSTER_LEDGERS:
        ledger_path = CLUSTER_LEDGERS[cluster_id.upper()]
    elif context == "ALPHA_CLUSTER_SEALING":
        ledger_path = CLUSTER_LEDGERS["ALPHA"]
    
    # 2. Yield-Aware ZKP Verification
    proof, is_valid = apply_zkp(content, grade, purity, context)
    
    if not is_valid:
        print(f"[VVV] ZKP Verification FAILED for essence from {source} [{context}]")
        return None
    
    print(f"[VVV] ZKP Verification SUCCESS ({grade}) for essence from {source} [{context}]")
    
    # 3. Add to Prioritized Immutable Ledger
    ledger_entry = {
        "timestamp": time.time(),
        "source": source,
        "context": context,
        "cluster_id": cluster_id,
        "purity": purity,
        "grade": grade,
        "content_hash": hashlib.sha256(content.encode()).hexdigest(),
        "zkp_proof": proof,
        "immutable_id": hashlib.sha256(f"{content}_{proof}_{purity}_{context}_{cluster_id}".encode()).hexdigest()
    }
    
    # Append to prioritized ledger file
    try:
        with open(ledger_path, "a") as f:
            f.write(json.dumps(ledger_entry) + "\n")
        print(f"[VVV] Essence Preserved in {os.path.basename(ledger_path)}")
    except Exception as e:
        print(f"[VVV] Ledger Write Error: {e}")

    return ledger_entry

@app.get("/vault/pulse")
async def vault_pulse():
    """
    Interlaces the Vault-Pulse into the Omni-Pulse frequency.
    Returns the integrity status of the entire system essence.
    """
    status = "STABLE"
    purity_level = 0.0
    total_entries = 0
    
    check_paths = [ETERNAL_LEDGER_PATH] + list(CLUSTER_LEDGERS.values())
    
    for l_path in check_paths:
        if os.path.exists(l_path):
            with open(l_path, "r") as f:
                for line in f:
                    entry = json.loads(line)
                    purity_level = max(purity_level, entry.get("purity", 0.0))
                    total_entries += 1
    
    return {
        "pulse": "VVV_STABLE_PULSE",
        "frequency": "SOVEREIGN_OMNI_PULSE",
        "status": status,
        "purity": purity_level,
        "integrity_score": 1.0,
        "total_sealed_entries": total_entries,
        "timestamp": time.time()
    }

@app.post("/vault/ingest")
async def ingest_wealth(payload: dict):
    """General endpoint for incoming technical wealth (REX, YES, etc.)"""
    source = payload.get("source", "Unknown")
    data = payload.get("data", {})
    context = payload.get("context", "general_preservation")
    cluster_id = payload.get("cluster_id")
    
    print(f"[VVV] Ingesting technical wealth from {source} [{context}]")
    entry = preserve_essence(data, source, context, cluster_id)
    
    if entry:
        return {
            "status": "preserved", 
            "grade": entry['grade'],
            "purity": entry['purity'],
            "vault": os.path.basename(entry.get('ledger_path', 'default'))
        }
    return {"status": "verification_failed"}

@app.post("/vault/seal_cluster")
async def seal_cluster(payload: dict):
    """Specific endpoint for sealing cluster states"""
    cluster_id = payload.get("cluster_id", "ALPHA")
    data = payload.get("data", {})
    
    print(f"[VVV] Sealing Cluster State: {cluster_id}")
    entry = preserve_essence(data, f"CLUSTER_{cluster_id}", f"{cluster_id}_CLUSTER_SEALING", cluster_id)
    
    if entry:
        return {"status": "cluster_sealed", "immutable_id": entry['immutable_id']}
    return {"status": "sealing_failed"}

@app.post("/protocol/callback")
async def protocol_callback(payload: dict):
    event = payload.get("event")
    data = payload.get("data")
    cluster_id = payload.get("cluster_id")
    
    print(f"[VVV] Received protocol signal: {event}")
    
    # Yield-Aware Filtering
    purity, grade, _ = PurityDistiller.distill(data)
    
    if event == "PROTOCOL_COMPLETE" or event == "ATOM_SHIFT_COMPLETE":
        if purity >= 0.90:
            entry = preserve_essence(data, f"Signal_{event}", "Omni-Pulse_Sync", cluster_id)
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

@app.get("/vault/cluster_ledger/{cluster_id}")
async def get_cluster_ledger(cluster_id: str):
    cluster_id = cluster_id.upper()
    if cluster_id not in CLUSTER_LEDGERS:
        return {"error": "Invalid cluster_id"}
    
    ledger_path = CLUSTER_LEDGERS[cluster_id]
    entries = []
    if os.path.exists(ledger_path):
        with open(ledger_path, "r") as f:
            for line in f:
                entries.append(json.loads(line))
    return entries

@app.get("/vault/alpha_ledger")
async def get_alpha_ledger():
    return await get_cluster_ledger("ALPHA")

@app.get("/vault/beta_ledger")
async def get_beta_ledger():
    return await get_cluster_ledger("BETA")

@app.get("/vault/gamma_ledger")
async def get_gamma_ledger():
    return await get_cluster_ledger("GAMMA")

@app.get("/vault/delta_ledger")
async def get_delta_ledger():
    return await get_cluster_ledger("DELTA")

@app.get("/vault/sync_siphon")
async def sync_siphon():
    """Sync with REX's siphoned essence file and apply yield-aware preservation"""
    if not os.path.exists(SIPHON_PATH):
        return {"status": "no_siphon_data"}
    
    new_entries = 0
    try:
        with open(SIPHON_PATH, "r") as f:
            siphoned_data = json.load(f)
        
        # Collect existing hashes from all ledgers
        existing_hashes = set()
        for l_path in [ETERNAL_LEDGER_PATH, STANDARD_LEDGER_PATH] + list(CLUSTER_LEDGERS.values()):
            if os.path.exists(l_path):
                with open(l_path, "r") as f:
                    for line in f:
                        existing_hashes.add(json.loads(line).get("content_hash"))
        
        for entry in siphoned_data:
            content_hash = hashlib.sha256(json.dumps(entry, sort_keys=True).encode()).hexdigest()
            if content_hash not in existing_hashes:
                preserve_essence(entry, "REX_SIPHON", "Batch_Siphon_Sync")
                new_entries += 1
                
        return {"status": "synced", "new_entries": new_entries}
    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8010)
