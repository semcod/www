"""Script to scan sample projects and populate the database."""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from routers.audit import _run_sandbox_analysis
from db_module.scans import save_scan
from sample_projects import get_sample_projects


async def scan_sample_projects():
    """Scan all sample projects and save to database."""
    projects = get_sample_projects()
    
    print(f"Scanning {len(projects)} sample projects...")
    print("=" * 60)
    
    results = []
    
    for i, project in enumerate(projects, 1):
        print(f"\n[{i}/{len(projects)}] Scanning: {project['name']}")
        print(f"Platform: {project['platform']}")
        print(f"URL: {project['url']}")
        
        try:
            # Create a fake audit_id for the scan
            import hashlib
            from datetime import datetime, timezone
            audit_id = hashlib.sha256(
                f"{project['name']}-{datetime.now(timezone.utc).isoformat()}".encode()
            ).hexdigest()[:12]
            
            # Run the sandbox analysis
            await _run_sandbox_analysis(
                audit_id,
                project['url'],
                project['name']
            )
            
            # The scan will be saved to database by the pipeline
            print(f"✓ Scan completed for {project['name']}")
            results.append({
                "project": project['name'],
                "status": "success",
            })
            
            # Small delay to avoid overwhelming servers
            await asyncio.sleep(2)
            
        except Exception as e:
            print(f"✗ Scan failed for {project['name']}: {e}")
            results.append({
                "project": project['name'],
                "status": "failed",
                "error": str(e),
            })
    
    print("\n" + "=" * 60)
    print("Scan Summary:")
    print("=" * 60)
    success_count = sum(1 for r in results if r['status'] == 'success')
    print(f"Total: {len(results)}")
    print(f"Success: {success_count}")
    print(f"Failed: {len(results) - success_count}")
    
    return results


if __name__ == "__main__":
    asyncio.run(scan_sample_projects())
