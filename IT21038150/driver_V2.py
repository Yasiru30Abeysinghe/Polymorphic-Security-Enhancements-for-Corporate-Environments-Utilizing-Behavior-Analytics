import json
import numpy as np
import pandas as pd
from subprocess import Popen, PIPE
from keras.models import load_model
from sklearn.preprocessing import StandardScaler

def hexToInt(hex):
    return int(hex[2:], 16)

model = load_model('models/ID_ANN_V6.h5')
data = pd.read_csv('../dataProcessing/processedData/testDataProcessed.csv')

# dummyPacket = {
#     "frame_len": 0,
#     "frame_cap_len": 0,
#     "frame_protocols": 0,
#     "ip_dsfield_dscp": 0,
#     "ip_flags_df": 0,
#     "ip_proto": 0,
#     "ip_checksum": 0,
#     "ip_flags": 0,
#     "ip_ttl": 0,
#     "tcp_stream": 0,
#     "tcp_len": 0,
#     "tcp_flags_push": 0,
#     "tcp_window_size": 0,
#     "tcp_window_size_scalefactor": 0,
#     "udp_length": 0,
#     "udp_checksum": 0,
#     "udp_checksum_status": 0,
#     "udp_stream": 0,
#     "dns_count_add_rr": 0,
#     "dns_qry_name_len": 0,
#     "dns_count_labels": 0
# }

dummyPacket = {
    "frame_frame_time_relative": "0",
    "frame_frame_protocols": "0",
    "eth_eth_type": "0",
    "ip_ip_flags": "0",
    "ip_ip_ttl": "0",
    "ip_ip_proto": "0",
    "tcp_tcp_completeness": "0",
    "tcp_tcp_completeness_data": "0",
    "tcp_tcp_completeness_ack": "0",
    "tcp_tcp_completeness_syn-ack": "0",
    "tcp_tcp_completeness_syn": "0",
    "tcp_tcp_window_size_value": "0",
    "tcp_tcp_window_size": "0",
    "tcp_tcp_analysis_push_bytes_sent": "0",
    "dtls_dtls_record_content_type": "0",
    "dtls_dtls_record_version": "0",
    "dtls_dtls_record_length": "0",
    "dtls_dtls_handshake_type": "0",
    "udp_udp_time_relative": "0",
    "udp_udp_checksum": "0",
    "udp_udp_stream": "0",
    "dns_dns_count_add_rr": "0",
    "dns_dns_qry_name_len": "0",
    "dns_dns_count_labels": "0",
    "quic_quic_fixed_bit": "0",
    "quic_quic_long_packet_type": "0",
    "quic_quic_version": "0",
    "quic_quic_length": "0",
    "stun_stun_type": "0",
    "stun_stun_type_class": "0",
    "stun_stun_type_method": "0",
    "stun_stun_length": "0",
    "stun_stun_network_version": "0",
    "stun_stun_attribute": "0",
    "stun_stun_att_type": "0",
    "stun_stun_att_length": "0",
    "stun_stun_att_crc32": "0",
    "stun_stun_att_crc32_status": "0"
}

fields = list(dummyPacket.keys())

captureCmd = [
   "sudo", "tshark",
   "-i", "wlo1",
   "-T", "ek",
   "-Y", "not (ip.src == 192.168.1.28)",
#    "-c", "1"
]

process = Popen(
    captureCmd,
    stdout=PIPE,
    stderr=PIPE,
    text=True
)

for line in process.stdout:
    if "index" not in str(line):
        packet = json.loads(line)
        tmpPacket = dummyPacket
        if 'frame' in packet['layers']:
            if 'frame_frame_time_relative' in packet['layers']['frame']:
                tmpPacket['frame_time_relative'] = packet['layers']['frame']['frame_frame_time_relative']
            if 'frame_frame_protocols' in packet['layers']['frame']:
                if "tcp" in str(packet['layers']['frame']['frame_frame_protocols']):
                    tmpPacket['frame_protocols'] = 0
                elif "udp" in str(packet['layers']['frame']['frame_frame_protocols']):
                    tmpPacket['frame_protocols'] = 1
        if 'eth' in packet['layers']:
            if 'eth_eth_type' in packet['layers']['eth']:
                tmpPacket['eth_type'] = hexToInt(packet['layers']['eth']['eth_eth_type'])
        if "ip" in packet['layers']:
            if 'ip_ip_flags' in packet['layers']['ip']:
                tmpPacket['ip_flags'] = hexToInt(packet['layers']['ip']['ip_ip_flags'])
            if 'ip_ip_ttl' in packet['layers']['ip']:
                tmpPacket['ip_ttl']  = packet['layers']['ip']['ip_ip_ttl']
            if 'ip_ip_proto' in packet['layers']['ip']:
                tmpPacket['ip_proto'] = packet['layers']['ip']['ip_ip_proto']
        if "udp" in packet['layers']:
            if 'udp_udp_length' in packet['layers']['udp']:
                tmpPacket['udp_length'] = packet['layers']['udp']['udp_udp_length']
            if 'udp_udp_checksum' in packet['layers']['udp']:
                tmpPacket['udp_checksum'] = hexToInt(packet['layers']['udp']['udp_udp_checksum'])
            if 'udp_udp_stream' in packet['layers']['udp']:
                tmpPacket['udp_stream'] = packet['layers']['udp']['udp_udp_stream']
        if "dns" in packet['layers']:
            if 'dns_dns_count_add_rr' in packet['layers']['dns']:
                tmpPacket['dns_count_add_rr'] = packet['layers']['dns']['dns_dns_count_add_rr']
            if 'dns_dns_qry_name_len' in packet['layers']['dns']:
                tmpPacket['dns_qry_name_len'] = packet['layers']['dns']['dns_dns_qry_name_len']
            if 'dns_dns_count_labels' in packet['layers']['dns']:
                tmpPacket['dns_count_labels'] = packet['layers']['dns']['dns_dns_count_labels']
        if 'tcp' in packet['layers']:
            if 'tcp_tcp_completeness' in packet['layers']['tcp']:
                tmpPacket['tcp_completeness'] = packet['layers']['tcp']['tcp_tcp_completeness']
            if 'tcp_tcp_completeness_data' in packet['layers']['tcp']:
                tmpPacket['tcp_tcp_completeness_data'] = packet['layers']['tcp']['tcp_tcp_completeness_data']
            if 'tcp_tcp_completeness_ack' in packet['layers']['tcp']:
                tmpPacket['tcp_completeness_ack'] = packet['layers']['tcp']['tcp_tcp_completeness_ack']
            if 'tcp_tcp_completeness_syn-ack' in packet['layers']['tcp']:
                tmpPacket['tcp_completeness_syn-ack'] = packet['layers']['tcp']['tcp_tcp_completeness_syn-ack']
            if 'tcp_tcp_completeness_syn' in packet['layers']['tcp']:
                tmpPacket['tcp_completeness_syn'] = packet['layers']['tcp']['tcp_tcp_completeness_syn']
            if 'tcp_tcp_window_size_value' in packet['layers']['tcp']:
                tmpPacket['tcp_window_size_value'] = packet['layers']['tcp']['tcp_tcp_window_size_value']
            if 'tcp_tcp_window_size' in packet['layers']['tcp']:
                tmpPacket['tcp_window_size'] = packet['layers']['tcp']['tcp_tcp_window_size']
            if 'tcp_tcp_analysis_push_bytes_sent' in packet['layers']['tcp']:
                tmpPacket['tcp_analysis_push_bytes_sent'] = packet['layers']['tcp']['tcp_tcp_analysis_push_bytes_sent']
        # if 'dtls' in packet['layers']:
        #     if 'dtls_dtls_record_content_type' in packet['layers']['dtls']:
        #         tmpPacket['dtls_record_content_type'] = packet['layers']['dtls']['dtls_dtls_record_content_type']
        #     if 'dtls_dtls_record_version' in packet['layers']['dtls']:
        #         tmpPacket['dtls_record_version'] = packet['layers']['dtls']['dtls_dtls_record_version']
        #     if 'dtls_dtls_record_length' in packet['layers']['dtls']:
        #         tmpPacket['dtls_record_length'] = packet['layers']['dtls']['dtls_dtls_record_length']
        #     if 'dtls_dtls_handshake_type' in packet['layers']['dtls']:
        #         tmpPacket['dtls_handshake_type'] = packet['layers']['dtls']['dtls_dtls_handshake_type']
        # if 'quic' in packet['layers']:
            if 'quic_quic_fixed_bit' in packet['layers']['quic']:
                tmpPacket['quic_fixed_bit'] = packet['layers']['quic']['quic_quic_fixed_bit']
            if 'dtls_dtls_record_version' in packet['layers']['quic']:
                tmpPacket['dtls_record_version'] = packet['layers']['quic']['dtls_dtls_record_version']
            if 'quic_quic_version' in packet['layers']['quic']:
                tmpPacket['quic_version'] = hexToInt(packet['layers']['quic']['quic_quic_version'])
            if 'quic_quic_length' in packet['layers']['quic']:
                tmpPacket['quic_length'] = packet['layers']['quic']['quic_quic_length']
        # if 'stun' in packet['layers']:
        #     if 'stun_stun_type' in packet['layers']['stun']:
        #         tmpPacket['stun_type'] = hexToInt(packet['layers']['stun']['stun_stun_type'])
                
        #     if 'stun_stun_type_class' in packet['layers']['stun']:
        #         tmpPacket['stun_type_class'] = hexToInt(packet['layers']['stun']['stun_stun_type_class'])
                
        #     if 'stun_stun_type_method' in packet['layers']['stun']:
        #         tmpPacket['stun_type_method'] = hexToInt(packet['layers']['stun']['stun_stun_type_method'])
                
        #     if 'stun_stun_length' in packet['layers']['stun']:
        #         tmpPacket['stun_length'] = packet['layers']['stun']['stun_stun_length']
                
        #     if 'stun_stun_network_version' in packet['layers']['stun']:
        #         tmpPacket['stun_network_version'] = packet['layers']['stun']['stun_stun_network_version']
                
                
                
        #     if 'stun_stun_attributes_stun_attribute' in packet['layers']['stun']:
        #         tmpPacket['stun_attribute'] = packet['layers']['stun']['stun_stun_attributes_stun_attribute']
                
        #     if 'stun_stun_attributes_stun_attribute_tree' in packet['layers']['stun']:
        #         tmpPacket['stun_att_type'] = packet['layers']['stun']['stun_stun_att_type']
                
        #     if 'stun_stun_att_length' in packet['layers']['stun']:
        #         tmpPacket['stun_att_length'] = packet['layers']['stun']['stun_stun_att_length']
                
        #     if 'stun_stun_att_crc32' in packet['layers']['stun']:
        #         tmpPacket['stun_att_crc32'] = packet['layers']['stun']['stun_stun_att_crc32']
                
        #     if 'stun_stun_att_crc32_status' in packet['layers']['stun']:
        #         tmpPacket['stun_att_crc32_status'] = packet['layers']['stun']['stun_stun_att_crc32_status']

        df = pd.json_normalize(tmpPacket)
        df1 = np.asarray(df).astype(np.int32)
        predictions = model.predict(df1)
        predictions = (predictions > 0.5)*1

        if predictions.flatten() == 1:
           print("Alert")
           print(packet['layers'].keys())

# for line in process.stdout:
#     if "index" not in str(line):
#         packet = json.loads(line)
#         tmpPacket = dummyPacket
#         if 'frame' in packet['layers']:
#             if 'frame_frame_len' in packet['layers']['frame']:
#                 tmpPacket['frame_len'] = packet['layers']['frame']['frame_frame_len']
#             if 'frame_frame_cap_len' in packet['layers']['frame']:
#                 tmpPacket['frame_cap_len'] = packet['layers']['frame']['frame_frame_cap_len']
#             if 'frame_frame_protocols' in packet['layers']['frame']:
#                 if "tcp" in str(packet['layers']['frame']['frame_frame_protocols']):
#                     tmpPacket['frame_protocols'] = 0
#                 elif "udp" in str(packet['layers']['frame']['frame_frame_protocols']):
#                     tmpPacket['frame_protocols'] = 1
#         if "ip" in packet['layers']:
#             if 'ip_ip_dsfield_dscp' in packet['layers']['ip']:
#                 tmpPacket['ip_dsfield_dscp'] = packet['layers']['ip']['ip_ip_dsfield_dscp']
#             if 'ip_ip_flags_df' in packet['layers']['ip']:
#                 if packet['layers']['ip']['ip_ip_flags_df'] == 'true':
#                     tmpPacket['ip_flags_df'] = 1
#                 if packet['layers']['ip']['ip_ip_flags_df'] == 'false':
#                     tmpPacket['ip_flags_df'] = 0    
#             if 'ip_ip_proto' in packet['layers']['ip']:
#                 tmpPacket['ip_proto'] = packet['layers']['ip']['ip_ip_proto']
#             if 'ip_ip_checksum' in packet['layers']['ip']:
#                 tmpPacket['ip_checksum'] = hexToInt(packet['layers']['ip']['ip_ip_checksum'])
#             if 'ip_ip_flags' in packet['layers']['ip']:
#                 tmpPacket['ip_flags'] = hexToInt(packet['layers']['ip']['ip_ip_flags'])
#             if 'ip_ip_ttl' in packet['layers']['ip']:
#                 tmpPacket['ip_ttl'] = packet['layers']['ip']['ip_ip_ttl']
#         if "tcp" in packet['layers']:
#             if 'tcp_tcp_stream' in packet['layers']['tcp']:
#                 tmpPacket['tcp_stream'] = packet['layers']['tcp']['tcp_tcp_stream']
#             if 'tcp_tcp_len' in packet['layers']['tcp']:
#                 tmpPacket['tcp_len'] = packet['layers']['tcp']['tcp_tcp_len']
#             if 'tcp_tcp_flags_push' in packet['layers']['tcp']:
#                 if packet['layers']['tcp']['tcp_tcp_flags_push'] == 'true':
#                     tmpPacket['tcp_flags_push'] = 1
#                 if packet['layers']['tcp']['tcp_tcp_flags_push'] == 'false':
#                     tmpPacket['tcp_flags_push'] = 0
#             if 'tcp_tcp_window_size' in packet['layers']['tcp']:
#                 tmpPacket['tcp_window_size'] = packet['layers']['tcp']['tcp_tcp_window_size']
#             if 'tcp_tcp_window_size_scalefactor' in packet['layers']['tcp']:
#                 tmpPacket['tcp_window_size_scalefactor'] = packet['layers']['tcp']['tcp_tcp_window_size_scalefactor']
#         if "udp" in packet['layers']:
#             if 'udp_udp_length' in packet['layers']['udp']:
#                 tmpPacket['udp_length'] = packet['layers']['udp']['udp_udp_length']
#             if 'udp_udp_checksum' in packet['layers']['udp']:
#                 tmpPacket['udp_checksum'] = hexToInt(packet['layers']['udp']['udp_udp_checksum'])
#             if 'udp_udp_checksum_status' in packet['layers']['udp']:
#                 tmpPacket['udp_checksum_status'] = packet['layers']['udp']['udp_udp_checksum_status']
#             if 'udp_udp_stream' in packet['layers']['udp']:
#                 tmpPacket['udp_stream'] = packet['layers']['udp']['udp_udp_stream']
#         if "dns" in packet['layers']:
#             if 'dns_dns_count_add_rr' in packet['layers']['dns']:
#                 tmpPacket['dns_count_add_rr'] = packet['layers']['dns']['dns_dns_count_add_rr']
#             if 'dns_dns_qry_name_len' in packet['layers']['dns']:
#                 tmpPacket['dns_qry_name_len'] = packet['layers']['dns']['dns_dns_qry_name_len']
#             if 'dns_dns_count_labels' in packet['layers']['dns']:
#                 tmpPacket['dns_count_labels'] = packet['layers']['dns']['dns_dns_count_labels']

#         df = pd.json_normalize(tmpPacket)
#         df1 = np.asarray(df).astype(np.int32)
#         predictions = model.predict(df1)
#         predictions = (predictions > 0.5)*1

#         if predictions.flatten() == 1:
#            print("Alert")
#            print(packet['layers'].keys())

process.kill()
    
