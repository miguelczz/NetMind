from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
import ipaddress
import requests
import socket
from typing import List, Optional, Dict, Any
import ipaddress

router = APIRouter(prefix="/tools", tags=["Quick Tools"])

# --- Quick Tools Endpoints Removed by User Request ---
# (Subnet, DNS, MAC Lookup deleted)

# --- Dashboard Endpoints ---

class ServiceStatus(BaseModel):
    name: str
    status: str  # "operational", "degraded", "down"
    latency_ms: float
    uptime_percentage: float

class DashboardStats(BaseModel):
    active_incidents: int
    avg_latency: float
    services: List[ServiceStatus]

@router.get("/dashboard/status", response_model=DashboardStats)
async def get_dashboard_status():
    # In a real app, this would query a background monitoring service or DB
    # For now, we perform real-time check on key targets
    
    targets = [
        {"name": "Internet (Google DNS)", "host": "8.8.8.8"},
        {"name": "Gateway", "host": "1.1.1.1"}, # Cloudflare as proxy for external connectivity
        {"name": "Internal Auth", "host": "localhost"} # Dummy internal
    ]
    
    services = []
    total_latency = 0
    count_up = 0
    
    import platform
    import subprocess
    import re
    
    # Simple ping helper with TCP fallback for Heroku/Cloud
    def simple_ping(host):
        # 1. Try system ping first (works in local)
        import time
        param = '-n' if platform.system().lower()=='windows' else '-c'
        command = ['ping', param, '1', host]
        try:
            start_time = time.time()
            output = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=2)
            if output.returncode == 0:
                match = re.search(r"time[=<](\d+)", output.stdout)
                if match:
                    return float(match.group(1))
                return 1.0
        except:
            pass
            
        # 2. Fallback: TCP Head/Connect (Works on Heroku)
        # We try to connect to port 80/443 to measure "app targets" or 8.8.8.8:53
        port = 80
        if "google" in host or "8.8.8.8" in host: port = 53 # DNS port is often open
        if host == "localhost": port = 8000 # Typical dev port
        
        try:
            start = time.time()
            # Try to resolve and connect
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1.5)
            result = sock.connect_ex((host, port))
            end = time.time()
            sock.close()
            
            if result == 0 or result == 111: # 0=success, 111=Connection refused (but host is alive)
                return max(1.0, round((end - start) * 1000, 2))
            return None
        except:
            return None

    for t in targets:
        latency = simple_ping(t["host"])
        status = "down"
        
        # Si hay latencia real, usarla. Si no (timeout), usar penalización de 999ms
        # para que impacte el gráfico y el promedio visualmente.
        metric_value = latency if latency is not None else 999.0
        
        if latency is not None:
            status = "operational" if latency < 100 else "degraded"
        
        total_latency += metric_value
        count_up += 1 # Contamos todos los objetivos para el promedio, incluso los caídos
            
        services.append(ServiceStatus(
            name=t["name"],
            status=status,
            latency_ms=metric_value,
            uptime_percentage=99.9 if status != "down" else 0.0
        ))
        
    avg = total_latency / len(targets) if targets else 0
    
    return DashboardStats(
        active_incidents=len(targets) - count_up,
        avg_latency=round(avg, 2),
        services=services
    )

# --- GeoTrace Endpoints ---

class GeoPoint(BaseModel):
    hop: int
    ip: str
    lat: float
    lon: float
    city: str
    country: str
    rtt: str

@router.get("/geo-trace", response_model=List[GeoPoint])
async def geo_trace(host: str = Query(..., description="Host to trace")):
    # 1. Run Traceroute
    # Implementation depends on OS. We'll reuse ip_tool logic or simple subprocess here for simplicity
    # Ideally import IPTool instance
    import subprocess
    import platform
    import re
    
    hops_ips = []
    
    def is_public_ip(ip: str) -> bool:
        try:
            ip_obj = ipaddress.ip_address(ip)
            return not (ip_obj.is_private or ip_obj.is_loopback or ip_obj.is_link_local or ip_obj.is_multicast)
        except:
            return False

    # 0. Get Source IP (Server/Local)
    try:
        source_ip = requests.get("https://api.ipify.org", timeout=5).text
        if is_public_ip(source_ip):
            hops_ips.append(source_ip)
    except:
        pass

    # 1. Run Traceroute (Optimized)
    # Windows: -d (no DNS), -h 20 (max hops), -w 200 (wait 200ms)
    # Linux: -n (no DNS), -m 20 (max hops), -q 1 (1 query), -w 1 (wait 1s)
    cmd = ['tracert', '-d', '-h', '20', '-w', '200', host] if platform.system().lower() == 'windows' else ['traceroute', '-n', '-m', '20', '-q', '1', '-w', '1', host]
    
    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        out, err = proc.communicate(timeout=45) 
        
        lines = out.split('\n')
        for line in lines:
            ip_match = re.search(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', line)
            if ip_match:
                ip = ip_match.group(1)
                if ip not in hops_ips and is_public_ip(ip):
                    hops_ips.append(ip)
                
    except Exception:
        # Fallback to External MTR API if local fails
        try:
            external_resp = requests.get(f"https://api.hackertarget.com/mtr/?q={host}", timeout=15)
            if external_resp.status_code == 200:
                lines = external_resp.text.split('\n')
                for line in lines:
                    ip_match = re.search(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', line)
                    if ip_match:
                        ip = ip_match.group(1)
                        if ip not in hops_ips and is_public_ip(ip):
                            hops_ips.append(ip)
        except:
            pass
        
    # Ensure target IP is at the end if we resolved it
    try:
        target_ip = socket.gethostbyname(host)
        if target_ip not in hops_ips and is_public_ip(target_ip):
            hops_ips.append(target_ip)
        elif target_ip in hops_ips:
            # Move target to the end
            hops_ips.remove(target_ip)
            hops_ips.append(target_ip)
    except:
        pass

    if len(hops_ips) < 2:
         raise HTTPException(status_code=400, detail="Could not trace host or find public nodes")

    # 2. Geolocation (Batch query to ip-api.com)
    # Max 100 IPs per batch. We have max 15 hops.
    # Docs: https://ip-api.com/docs/api:batch
    
    geo_points = []
    
    try:
        resp = requests.post("http://ip-api.com/batch", json=hops_ips, timeout=10)
        start_lat = None
        start_lon = None
        
        if resp.status_code == 200:
            data = resp.json()
            for idx, item in enumerate(data):
                if item.get("status") == "success":
                    lat = item.get("lat")
                    lon = item.get("lon")
                    
                    # Filter out local IPs or invalid coords
                    if lat == 0 and lon == 0: continue
                    
                    # Store current user location approximately from first public hop
                    # (Private IPs will fail status or have 0,0 usually but ip-api handles private IPs by failing)
                    
                    geo_points.append(GeoPoint(
                        hop=idx + 1,
                        ip=item.get("query"),
                        lat=lat,
                        lon=lon,
                        city=item.get("city", "Unknown"),
                        country=item.get("country", "Unknown"),
                        rtt="-" # Parsing RTT is complex, skipping for MVP
                    ))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"GeoIP Error: {str(e)}")
        
    return geo_points
