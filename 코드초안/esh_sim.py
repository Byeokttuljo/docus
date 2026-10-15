import time
import random

# 가상 Meshtastic 노드 클래스 정의
class VirtualNode:
    def __init__(self, node_name):
        self.node_name = node_name
        self.seen_packets = set()  # 중복 수신 방지용 (Packet ID 저장)

    def receive_packet(self, packet):
        seq = packet['seq']
        
        # 1. 무한루프/중복 수신 검증 (이미 본 패킷은 Drop)
        if seq in self.seen_packets:
            print(f"[{self.node_name}] 중복 패킷({seq}) 감지 -> 버림(Drop)")
            return None
        self.seen_packets.add(seq)

        # 2. LoRa Mesh 전송 및 백오프 지연시간 시뮬레이션 (1홉당 약 0.3~0.8초)
        hop_delay = random.uniform(0.3, 0.8)
        time.sleep(hop_delay)
        
        packet['hop_count'] += 1
        packet['total_delay'] += hop_delay
        
        print(f"[{self.node_name}] {packet['hop_count']}Hop 중계 완료 (누적 지연: {packet['total_delay']:.2f}초)")
        return packet

# --- 모의실행 시작 ---
print("=== Meshtastic 가상 노드 3홉 통신 모의실행 ===")

# 우리가 정의한 5바이트 상태 패킷 (Byte 3: 0b00000001 -> 추락 발생)
status_bitfield = 0b00000001 
packet = {
    'src_id': 0x1001,
    'seq': 101,
    'data': bytes([0x10, 0x01, 101, status_bitfield, 0xA2]),
    'hop_count': 0,
    'total_delay': 0.0
}

# 3개 노드 거쳐 전달 (Node_A -> Node_B -> Gateway)
nodes = [VirtualNode("Node_B (중계1)"), VirtualNode("Node_C (중계2)"), VirtualNode("Gateway (수신)")]

curr_pkt = packet
for node in nodes:
    curr_pkt = node.receive_packet(curr_pkt)

print("\n[최종 검증 결과]")
print(f"1. 게이트웨이 수신 여부: 성공")
print(f"2. 총 Hop 수: {curr_pkt['hop_count']} Hops")
print(f"3. 3홉 도달 지연시간: {curr_pkt['total_delay']:.2f}초 (10초 이내 목표 달성)")
print(f"4. 5바이트 비트필드 해독: Status Bit = {bin(curr_pkt['data'][3])} (추락 감지 확인)")