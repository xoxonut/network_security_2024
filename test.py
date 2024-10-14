import ssl
import socket
import subprocess
def add_iptables_rule():
    rule = (
        "iptables -t nat -A PREROUTING -s 192.168.75.129 "
        "-d 140.113.0.0/16 -p tcp --dport 443 -j REDIRECT --to-ports 443"
    )

    try:
        subprocess.run(rule, shell=True, check=True)
        print("iptables rule added successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error adding iptables rule: {e}")

def remove_iptables_rule():
    rule = (
        "iptables -t nat -D PREROUTING -s 192.168.75.129 "
        "-d 140.113.0.0/16 -p tcp --dport 443 -j REDIRECT --to-ports 443"
    )

    try:
        subprocess.run(rule, shell=True, check=True)
        print("iptables rule removed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error removing iptables rule: {e}")

