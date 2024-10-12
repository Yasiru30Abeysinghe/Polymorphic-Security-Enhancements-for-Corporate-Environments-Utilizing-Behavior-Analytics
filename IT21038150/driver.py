import json
import numpy as np
import pandas as pd
from subprocess import Popen, PIPE
from keras.models import load_model
from sklearn.preprocessing import StandardScaler

def hexToInt(hex):
    return int(hex[2:], 16)

model = load_model('models/ID_ANN_V7.h5')

dummyPacket = {
    "frame_len": 0,
    "frame_cap_len": 0,
    "frame_protocols": 0,
    "ip_dsfield_dscp": 0,
    "ip_flags_df": 0,
    "ip_proto": 0,
    "ip_checksum": 0,
    "ip_flags": 0,
    "ip_ttl": 0,
    "tcp_len": 0,
    "tcp_flags_push": 0,
    "tcp_window_size": 0,
    "tcp_window_size_scalefactor": 0,
    "udp_length": 0,
    "udp_checksum": 0,
    "udp_checksum_status": 0,
    "udp_stream": 0,
    "dns_count_add_rr": 0,
    "dns_qry_name_len": 0,
    "dns_count_labels": 0
}

fields = list(dummyPacket.keys())

captureCmd = [
   "sudo", "tshark",
   "-i", "wlo1",
   "-T", "ek",
   "-Y", "not (ip.src == 192.168.1.28)",
   "-Y", "not (ip.src == 192.168.238.235)",
   "-Y", "not (ip.src == 192.168.238.8)",
#    "-c", "1"
]

process = Popen(
    captureCmd,
    stdout=PIPE,
    stderr=PIPE,
    text=True
)

for line in process.stdout:
    excludes = ["tls", "ipv6", "ssdp"]
    if "index" not in str(line):
        packet = json.loads(line)
        tmpPacket = dummyPacket
        if 'frame' in packet['layers']:
            if 'frame_frame_len' in packet['layers']['frame']:
                tmpPacket['frame_len'] = packet['layers']['frame']['frame_frame_len']
            if 'frame_frame_cap_len' in packet['layers']['frame']:
                tmpPacket['frame_cap_len'] = packet['layers']['frame']['frame_frame_cap_len']
            if 'frame_frame_protocols' in packet['layers']['frame']:
                if "tcp" in str(packet['layers']['frame']['frame_frame_protocols']):
                    tmpPacket['frame_protocols'] = 0
                elif "udp" in str(packet['layers']['frame']['frame_frame_protocols']):
                    tmpPacket['frame_protocols'] = 1
        if "ip" in packet['layers']:
            if 'ip_ip_dsfield_dscp' in packet['layers']['ip']:
                tmpPacket['ip_dsfield_dscp'] = packet['layers']['ip']['ip_ip_dsfield_dscp']
            if 'ip_ip_flags_df' in packet['layers']['ip']:
                if packet['layers']['ip']['ip_ip_flags_df'] == 'true':
                    tmpPacket['ip_flags_df'] = 1
                if packet['layers']['ip']['ip_ip_flags_df'] == 'false':
                    tmpPacket['ip_flags_df'] = 0    
            if 'ip_ip_proto' in packet['layers']['ip']:
                tmpPacket['ip_proto'] = packet['layers']['ip']['ip_ip_proto']
            if 'ip_ip_checksum' in packet['layers']['ip']:
                tmpPacket['ip_checksum'] = hexToInt(packet['layers']['ip']['ip_ip_checksum'])
            if 'ip_ip_flags' in packet['layers']['ip']:
                tmpPacket['ip_flags'] = hexToInt(packet['layers']['ip']['ip_ip_flags'])
            if 'ip_ip_ttl' in packet['layers']['ip']:
                tmpPacket['ip_ttl'] = packet['layers']['ip']['ip_ip_ttl']
        if "tcp" in packet['layers']:
            if 'tcp_tcp_len' in packet['layers']['tcp']:
                tmpPacket['tcp_len'] = packet['layers']['tcp']['tcp_tcp_len']
            if 'tcp_tcp_flags_push' in packet['layers']['tcp']:
                if packet['layers']['tcp']['tcp_tcp_flags_push'] == 'true':
                    tmpPacket['tcp_flags_push'] = 1
                if packet['layers']['tcp']['tcp_tcp_flags_push'] == 'false':
                    tmpPacket['tcp_flags_push'] = 0
            if 'tcp_tcp_window_size' in packet['layers']['tcp']:
                tmpPacket['tcp_window_size'] = packet['layers']['tcp']['tcp_tcp_window_size']
            if 'tcp_tcp_window_size_scalefactor' in packet['layers']['tcp']:
                tmpPacket['tcp_window_size_scalefactor'] = packet['layers']['tcp']['tcp_tcp_window_size_scalefactor']
        if "udp" in packet['layers']:
            if 'udp_udp_length' in packet['layers']['udp']:
                tmpPacket['udp_length'] = packet['layers']['udp']['udp_udp_length']
            if 'udp_udp_checksum' in packet['layers']['udp']:
                tmpPacket['udp_checksum'] = hexToInt(packet['layers']['udp']['udp_udp_checksum'])
            if 'udp_udp_checksum_status' in packet['layers']['udp']:
                tmpPacket['udp_checksum_status'] = packet['layers']['udp']['udp_udp_checksum_status']
            if 'udp_udp_stream' in packet['layers']['udp']:
                tmpPacket['udp_stream'] = packet['layers']['udp']['udp_udp_stream']
        if "dns" in packet['layers']:
            if 'dns_dns_count_add_rr' in packet['layers']['dns']:
                tmpPacket['dns_count_add_rr'] = packet['layers']['dns']['dns_dns_count_add_rr']
            if 'dns_dns_qry_name_len' in packet['layers']['dns']:
                tmpPacket['dns_qry_name_len'] = packet['layers']['dns']['dns_dns_qry_name_len']
            if 'dns_dns_count_labels' in packet['layers']['dns']:
                tmpPacket['dns_count_labels'] = packet['layers']['dns']['dns_dns_count_labels']
        if 'arp' in packet['layers']:
            continue
        if 'data' in packet['layers']:
            continue
        if 'mdns' in packet['layers']:
            continue
        if 'tls' in packet['layers']:
            continue
        if 'ssdp' in packet['layers']:
            continue
        if 'ipv6' in packet['layers']:
            continue
        if 'quic' in packet['layers']:
            continue

        df = pd.json_normalize(tmpPacket)
        df1 = np.asarray(df).astype(np.int32)
        predictions = model.predict(df1)
        predictions = (predictions > 0.5)*1

        if predictions.flatten() == 1:
           print("Alert")
           print(packet['layers'].keys())
           

process.kill()
    
