import subprocess
import time
from diagnostic_snapshot import save_snapshot
from prometheus_client import Counter, Gauge, start_http_server

destination = "1.1.1.1"
interface_name = "eth0"

network_reachable = Gauge(
    "network_reachable",
    "Whether the destination replied to at least one ping",
)
network_packet_loss = Gauge(
    "network_packet_loss_percent",
    "Percentage of pings that received no reply",
)
network_latency = Gauge(
    "network_latency_ms",
    "Average ping reply time in milliseconds",
)
network_interface_up = Gauge(
    "network_interface_up",
    "Whether the monitored network interface is up",
)
route_changes = Counter(
    "network_route_changes_total",
    "Number of routing table changes detected",
)

start_http_server(8000)
print("Metrics are at http://localhost:8000/metrics")

previous_routes = None
previously_unreachable = False

while True:
    ping_result = subprocess.run(
        ["ping", "-c", "5", "-W", "2", destination],
        capture_output=True,
        text=True,
    )

    is_reachable = ping_result.returncode == 0
    network_reachable.set(1 if is_reachable else 0)

    if not is_reachable and not previously_unreachable:
        save_snapshot("destination unreachable")
    previously_unreachable = not is_reachable

    average_latency_ms = None

    for line in ping_result.stdout.splitlines():
        if "packet loss" in line:
            packet_loss = float(line.split(",")[2].strip().split("%")[0])
            network_packet_loss.set(packet_loss)

        if "rtt min/avg/max" in line:
            values = line.split("=")[1].strip().split("/")
            average_latency_ms = float(values[1])

    if average_latency_ms is not None:
        network_latency.set(average_latency_ms)
    else:
        network_latency.set(float("nan"))

    interface_result = subprocess.run(
        ["ip", "-br", "link", "show", interface_name],
        capture_output=True,
        text=True,
    )
    interface_fields = interface_result.stdout.split()
    interface_is_up = (
        interface_result.returncode == 0
        and len(interface_fields) > 1
        and interface_fields[1] == "UP"
    )
    network_interface_up.set(1 if interface_is_up else 0)

    route_result = subprocess.run(
        ["ip", "route"],
        capture_output=True,
        text=True,
    )
    current_routes = route_result.stdout

    if previous_routes is None:
        previous_routes = current_routes
    elif current_routes != previous_routes:
        route_changes.inc()
        previous_routes = current_routes
        print("Route change detected")

    print(f"Latest check complete for {destination} and {interface_name}")
    time.sleep(10)