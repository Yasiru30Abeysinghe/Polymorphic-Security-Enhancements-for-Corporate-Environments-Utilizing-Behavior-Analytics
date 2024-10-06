from netfilterqueue import NetfilterQueue as nfq
from scapy.all import IP, TCP, UDP, ICMP
from keras.models import load_model
import json
import numpy as np
import pandas as pd
from csv import reader
from os import system

enableIPTables = "iptables -I INPUT -j NFQUEUE --queue-num 0"
disableIPTables = "iptables -D INPUT -j NFQUEUE --queue-num 0"

model = load_model('models/ID_ANN_V10.h5')

suspicious_ips = []

def hexToInt(hex):
    strHex = "0x"+ str(hex)
    return int(strHex, 16)

def analyzePacket(packet):
    dummyPacket = {
        "ip_flags_df": 0,
        "ip_proto": 0,
        "ip_checksum": 0,
        "ip_flags": 0,
        "ip_ttl": 0,
        "tcp_checksum": 0,
        "tcp_window_size": 0,
        "tcp_urgent_pointer": 0,
        "udp_length": 0,
        "udp_checksum": 0
    }
    
    if IP in packet:
        ipLayer = packet[IP]
        dummyPacket['ip_proto'] = ipLayer.proto
        dummyPacket["ip_checksum"] = ipLayer.chksum
        dummyPacket['ip_flags'] = hexToInt(ipLayer.flags)
        dummyPacket['ip_ttl'] = ipLayer.ttl
        if ipLayer.flags == "DF":
            dummyPacket['ip_flags_df'] = 1

    if TCP in packet:
        tcpLayer = packet[TCP]
        dummyPacket['tcp_window_size'] = tcpLayer.window
        dummyPacket['tcp_checksum'] = tcpLayer.chksum
        dummyPacket['tcp_urgent_pointer'] = tcpLayer.urgptr
        
    if UDP in packet:
        udpLayer = packet[UDP]
        dummyPacket['udp_length'] = udpLayer.len
        dummyPacket['udp_checksum'] = udpLayer.chksum   
        
    df = pd.json_normalize(dummyPacket)
    df1 = np.asarray(df).astype(np.int32)
    predictions = model.predict(df1)
    predictions = (predictions > 0.5)*1

    if predictions.flatten() == 1:
        print("Alert")
    
    #print(dummyPacket)

def getSusIPs(file_path):
    ip_addresses = []
    with open(file_path, mode='r') as file:
        csv_reader = reader(file)
        for row in csv_reader:
            ip_addresses.append(row[1])
    return ip_addresses

def process_packet(packet):
    scapy_packet = IP(packet.get_payload()) 
    
    # Check whether the IP is in the blacklist
    if scapy_packet.src in suspicious_ips:
        print(f"[+] ALERT!!! Dropping packet from Blacklisted IP: {scapy_packet.src}")
        packet.drop()
        return
    
    # Implement the ANN based prediction
    analyzePacket(scapy_packet)
    
    packet.accept()

file_path = './IPFeed/ipFeed.csv'
suspicious_ips = getSusIPs(file_path)

# Add IPTables Rule
system(enableIPTables)

# Bind the queue
nfqueue = nfq()
nfqueue.bind(0, process_packet)

try:
    print("[+] IDS Initialized...")
    nfqueue.run()
except KeyboardInterrupt:
    print("[+] Stopping IDS...")

nfqueue.unbind()
system(disableIPTables)
