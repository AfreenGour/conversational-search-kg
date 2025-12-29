import os
import subprocess
import time
import urllib.request
import json
import socket
import subprocess


def wait_for_http(url, timeout=120):
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=5) as r:
                return True
        except Exception:
            time.sleep(1)
    return False


def wait_for_tcp(host, port, timeout=120):
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with socket.create_connection((host, port), timeout=5):
                return True
        except Exception:
            time.sleep(1)
    return False


def run_cmd(cmd, **kwargs):
    print('RUN:', ' '.join(cmd))
    return subprocess.run(cmd, check=False, **kwargs)


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    root = os.path.abspath(os.path.join(here, '..'))

    # Start docker-compose
    rc = run_cmd(['docker', 'compose', 'up', '--build', '-d'], cwd=root)
    if rc.returncode != 0:
        print('Failed to start docker-compose')
        raise SystemExit(1)

    try:
        # Wait for Neo4j bolt port and KG service to be reachable
        if not wait_for_tcp('localhost', 7687, timeout=120):
            print('Neo4j bolt port 7687 not reachable; dumping docker-compose logs')
            subprocess.run(['docker', 'compose', 'logs', 'neo4j'])
            raise SystemExit(1)

        if not wait_for_http('http://localhost:8000/', timeout=120):
            print('KG service not reachable; dumping kg_service logs')
            subprocess.run(['docker', 'compose', 'logs', 'kg_service'])
            raise SystemExit(1)

        # Ingest
        data = json.dumps({}).encode('utf-8')
        req = urllib.request.Request('http://localhost:8000/kg/ingest', data=data, method='POST')
        try:
            with urllib.request.urlopen(req, timeout=10) as r:
                print('ingest response', r.read().decode())
        except Exception as e:
            print('ingest call failed', e)
            subprocess.run(['docker-compose', 'logs', 'kg_service'])
            raise

        # Resolve
        data = json.dumps({'brand': 'Acer'}).encode('utf-8')
        req = urllib.request.Request('http://localhost:8000/kg/resolve', data=data, method='POST', headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req, timeout=10) as r:
            body = r.read().decode()
            print('resolve response', body)
            js = json.loads(body)
            if not js:
                raise SystemExit('resolve returned empty')

        # Neighbors
        with urllib.request.urlopen('http://localhost:8000/kg/products/P1/neighbors', timeout=10) as r:
            print('neighbors', r.read().decode())

        # Explain
        with urllib.request.urlopen('http://localhost:8000/kg/products/P1/explain?to=brand', timeout=10) as r:
            print('explain', r.read().decode())

        print('SMOKE OK')
    finally:
        run_cmd(['docker', 'compose', 'down', '-v'], cwd=root)


if __name__ == '__main__':
    main()
