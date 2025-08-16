'''
Ein Programm, welches eine beliebige Datei aus dem World Wide Web 
via unverschlüsselten HTTP in Blöcken herunterladen kann.
'''


import json
import sys
import socket
import os
import time

# ----------------------------
# Hilfsfunktionen
# ----------------------------

def parse_uri(uri):
    if uri.startswith("http://"):
        uri = uri[7:]

    parts = uri.split("/", 1)
    host = parts[0]
    path = "/" + parts[1] if len(parts) > 1 else "/"

    return host, path

def parse_block_size(size_str):
    size_str = size_str.strip().upper()
    if size_str.endswith("K"):
        return int(size_str[:-1]) * 1024
    elif size_str.endswith("M"):
        return int(size_str[:-1]) * 1024 * 1024
    elif size_str.endswith("G"):
        return int(size_str[:-1]) * 1024 * 1024 * 1024
    else:
        return int(size_str)

def send_http_head(host, path):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, 80))

    request = (
        f"HEAD {path} HTTP/1.1\r\n"
        f"Host: {host}\r\n"
        f"Connection: close\r\n\r\n"
    )
    s.sendall(request.encode())

    response = b""
    while True:
        data = s.recv(4096)
        if not data:
            break
        response += data

    s.close()
    return response.decode()

def parse_headers(response_text):
    content_length = None
    accepts_ranges = False

    for line in response_text.split("\r\n"):
        line = line.lower()
        if line.startswith("content-length:"):
            content_length = int(line.split(":")[1].strip())
            
        elif line.startswith("accept-ranges:") and "bytes" in line:
            accepts_ranges = True

    return content_length, accepts_ranges

def download_block(host, path, start_byte, end_byte):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, 80))

    request = (
        f"GET {path} HTTP/1.1\r\n"
        f"Host: {host}\r\n"
        f"Range: bytes={start_byte}-{end_byte}\r\n"
        f"Connection: close\r\n\r\n"
    )
    s.sendall(request.encode())

    response = b""
    while True:
        data = s.recv(4096)
        if not data:
            break
        response += data

    s.close()

    header_end = response.find(b"\r\n\r\n")
    body = response[header_end + 4:] if header_end != -1 else b""

    return body

def load_status():
    if os.path.exists("downloader_status.json"):
        with open("downloader_status.json", "r") as file:
            return json.load(file)
    return {}

def save_status(status):
    with open("downloader_status.json", "w") as file:
        json.dump(status, file, indent=2)

def finalize_download(num_blocks, output_filename):
    print("Alle Blöcke vorhanden. Füge zusammen...")

    with open(output_filename, "wb") as outfile:
        for i in range(num_blocks):
            with open(f"block_{i}.tmp", "rb") as infile:
                outfile.write(infile.read())

    print(f"Gespeichert als: {output_filename}")

    for i in range(num_blocks):
        os.remove(f"block_{i}.tmp")
    os.remove("downloader_status.json")

def get_filename_from_path(path):
    if path.endswith("/"):
        return f"file_{int(time.time())}.bin"
    return path.split("/")[-1]

# ----------------------------
# Hauptprogramm
# ----------------------------

def main():
    if len(sys.argv) < 3:
        print("Nutze: python downloader.py <BLOCKSIZE> <LINK>")
        exit(1)

    block_size = parse_block_size(sys.argv[1])
    uri = sys.argv[2]

    host, path = parse_uri(uri)
    response = send_http_head(host, path)
    content_length, supports_ranges = parse_headers(response)

    print("Dateigröße:", content_length, "Bytes")
    print("Range Requests unterstützt:", supports_ranges)

    if not supports_ranges:
        print("Server unterstützt keine Range-Requests. Abbruch.")
        exit(1)

    num_blocks = (content_length + block_size - 1) // block_size
    print(f"Download in {num_blocks} Blöcken à {block_size} Bytes\n")

    status = load_status()
    if (not status or status.get("uri") != uri or
        status.get("block_size") != block_size or
        status.get("content_length") != content_length):
        status = {
            "uri": uri,
            "block_size": block_size,
            "content_length": content_length,
            "downloaded_blocks": []
        }

    output_filename = get_filename_from_path(path)

    for i in range(num_blocks):
        if i in status["downloaded_blocks"]:
            print(f"[{i+1}/{num_blocks}] Block {i} vorhanden, überspringe.")
            continue

        start = i * block_size
        end = min(start + block_size - 1, content_length - 1)
        filename = f"block_{i}.tmp"

        print(f"[{i+1}/{num_blocks}] Lade {start}-{end} : {filename}")
        try:
            block_data = download_block(host, path, start, end)
            with open(filename, "wb") as f:
                f.write(block_data)
            print(f"Block {i} gespeichert.\n")

            status["downloaded_blocks"].append(i)
            save_status(status)

        except Exception as e:
            print(f"Fehler beim Download von Block {i}: {e}")
            print("Wird beim nächsten Durchlauf erneut versucht.")
            break

    if len(status["downloaded_blocks"]) == num_blocks:
        finalize_download(num_blocks, output_filename)

if __name__ == "__main__":
    main()
