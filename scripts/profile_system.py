import time
import subprocess
import json
import os
try:
    import psutil
except ImportError:
    psutil = None
from typing import Optional

# Setup database fallback path before imports
os.environ["DATABASE_URL"] = "sqlite:///./vaultrag.db"

from backend.api.chat import _get_or_create_query_engine
from llama_index.core.schema import NodeWithScore

def get_vram_usage() -> Optional[int]:
    """Get the current VRAM usage in MiB using nvidia-smi."""
    try:
        output = subprocess.check_output(
            ["nvidia-smi", "--query-gpu=memory.used", "--format=csv,noheader,nounits"],
            encoding="utf-8"
        )
        return int(output.strip())
    except Exception:
        return None

def get_ram_usage() -> Optional[float]:
    """Get system RAM usage percent."""
    if psutil is not None:
        return psutil.virtual_memory().percent
    return None

def run_profiling():
    print("=" * 60)
    print("VaultRAG System Profiler - Latency & Resource Utilization")
    print("=" * 60)
    
    # 1. Warm-up and engine loading
    print("\n[1/3] Initialising Query Engine (and triggering first model load)...")
    vram_before_init = get_vram_usage()
    ram_before_init = get_ram_usage()
    init_start = time.time()
    
    qe = _get_or_create_query_engine()
    
    init_time = time.time() - init_start
    vram_after_init = get_vram_usage()
    ram_after_init = get_ram_usage()
    
    print(f"Engine initialised in {init_time:.2f} seconds.")
    if vram_before_init is not None and vram_after_init is not None:
         print(f"VRAM change: {vram_before_init} MiB -> {vram_after_init} MiB (Delta: {vram_after_init - vram_before_init} MiB)")
    print(f"RAM change: {ram_before_init}% -> {ram_after_init}%")
    
    # Predefined queries to run
    queries = [
        "What does The Rundown use Granola for?",
        "How did Rowan grow his Instagram account?",
        "Granola",
        "List the top 3 ways The Rundown uses AI.",
        "What is the capital of France?" # Out of context test case
    ]
    
    results = []
    
    print("\n[2/3] Executing Profiling Queries...")
    for idx, query in enumerate(queries, 1):
        is_cold = (idx == 1)
        query_type = "Cold Load" if is_cold else "Warm Model"
        print(f"\nQuery #{idx} ({query_type}): '{query}'")
        
        vram_start = get_vram_usage()
        ram_start = get_ram_usage()
        
        # A. Retrieval Step
        t0 = time.time()
        nodes = qe.retriever.retrieve(query)
        t_retrieval = time.time() - t0
        
        # B. Combined query execution (Retrieval + Synthesis)
        t1 = time.time()
        response = qe.query(query)
        t_query_total = time.time() - t1
        
        # Approximate synthesis time
        t_synthesis = max(0.0, t_query_total - t_retrieval)
        
        vram_end = get_vram_usage()
        ram_end = get_ram_usage()
        
        t_total = t_query_total
        
        # Node details
        node_ids = [n.node.node_id for n in nodes]
        pages = [n.node.metadata.get("page_label", "N/A") for n in nodes]
        files = [n.node.metadata.get("file_name", "unknown") for n in nodes]
        
        print(f"  - Retrieval latency: {t_retrieval:.3f}s (Fetched {len(nodes)} chunks)")
        print(f"  - Synthesis latency: {t_synthesis:.3f}s")
        print(f"  - Total latency:     {t_total:.3f}s")
        if vram_start is not None and vram_end is not None:
            print(f"  - VRAM usage:        {vram_start} MiB -> {vram_end} MiB")
        print(f"  - RAM usage:         {ram_start}% -> {ram_end}%")
        print(f"  - Answer snippet:    {str(response)[:120]}...")
        
        results.append({
            "query_number": idx,
            "query": query,
            "type": query_type,
            "retrieval_latency_sec": t_retrieval,
            "synthesis_latency_sec": t_synthesis,
            "total_latency_sec": t_total,
            "vram_start_mib": vram_start,
            "vram_end_mib": vram_end,
            "ram_start_pct": ram_start,
            "ram_end_pct": ram_end,
            "chunks_retrieved": len(nodes),
            "pages_cited": pages,
            "files_cited": files,
            "answer_snippet": str(response)[:250]
        })
        
    # Write output to JSON
    output_path = os.path.join("data", "profiling_results.json")
    os.makedirs("data", exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(results, f, indent=4)
        
    print("\n" + "=" * 60)
    print(f"[3/3] Profiling Complete. Results saved to {output_path}")
    print("=" * 60)
    
    # Print overall summary table
    print("\nSummary Table:")
    print(f"{'No.':<4}{'Query':<45}{'Type':<12}{'Retr(s)':<8}{'Synth(s)':<9}{'Total(s)':<9}{'VRAM(MiB)':<10}")
    print("-" * 100)
    for r in results:
        vram_str = f"{r['vram_end_mib']}" if r['vram_end_mib'] is not None else "N/A"
        q_short = r['query'] if len(r['query']) <= 42 else r['query'][:39] + "..."
        print(f"{r['query_number']:<4}{q_short:<45}{r['type']:<12}{r['retrieval_latency_sec']:<8.2f}{r['synthesis_latency_sec']:<9.2f}{r['total_latency_sec']:<9.2f}{vram_str:<10}")
    print("=" * 60)

if __name__ == "__main__":
    run_profiling()
