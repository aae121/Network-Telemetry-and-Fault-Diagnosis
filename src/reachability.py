import subprocess

destination = "1.1.1.1"
result = subprocess.run(
    ["ping", "-c", "5", "-W", "2", destination],
    capture_output=True,
    text=True,
)

if result.returncode == 0:
    print(f"{destination} replied to at least one ping")
else:
    print(f"{destination} did not reply to any pings")

packet_loss = None
average_latency_ms = None

for line in result.stdout.splitlines():
    if "packet loss" in line:
        packet_loss = float(line.split(",")[2].strip().split("%")[0])

    if "rtt min/avg/max" in line:
        values = line.split("=")[1].strip().split("/")
        average_latency_ms = float(values[1])

if packet_loss is not None:
    print(f"Packet loss: {packet_loss}%")

if average_latency_ms is not None:
    print(f"Average latency: {average_latency_ms} ms")
else:
    print("Average latency: unavailable (no ping replies)")


