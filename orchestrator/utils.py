def save_orchestrator_ip(ip: str):
    with open("orchestrator_ip.txt", "w") as f:
        f.write(ip)
        
def get_orchestator_ip():
    with open("orchestrator_ip.txt", "r") as f:
        return f.read()