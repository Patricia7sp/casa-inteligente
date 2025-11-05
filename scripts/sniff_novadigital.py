#!/usr/bin/env python3
"""
Sniffer de pacotes para capturar tráfego da NovaDigital
Requer permissões de root: sudo python scripts/sniff_novadigital.py
"""

import socket
import struct
import re
from datetime import datetime


class TuyaSniffer:
    """Sniffer para protocolo Tuya"""

    def __init__(self, target_ip="192.168.68.100"):
        self.target_ip = target_ip
        self.captured_packets = []

    def sniff(self, duration_seconds=60):
        """Capturar pacotes por X segundos"""
        print(f"📡 SNIFFING NOVADIGITAL")
        print(f"=" * 60)
        print(f"🎯 IP alvo: {self.target_ip}")
        print(f"⏱️ Duração: {duration_seconds}s")
        print(f"⚠️ Requer sudo/root")
        print()
        print(f"💡 Enquanto captura, use o app Tuya Smart ou execute:")
        print(f"   python scripts/localtuya_client.py")
        print()
        print(f"Pressione Ctrl+C para parar antes")
        print("-" * 60)

        try:
            # Criar raw socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

            start_time = datetime.now()
            packet_count = 0

            while (datetime.now() - start_time).seconds < duration_seconds:
                try:
                    # Receber pacote
                    packet, addr = sock.recvfrom(65535)

                    # Parsear IP header
                    ip_header = packet[0:20]
                    iph = struct.unpack("!BBHHHBBH4s4s", ip_header)

                    src_ip = socket.inet_ntoa(iph[8])
                    dst_ip = socket.inet_ntoa(iph[9])

                    # Filtrar apenas tráfego da NovaDigital
                    if src_ip == self.target_ip or dst_ip == self.target_ip:
                        packet_count += 1

                        # Parsear TCP header
                        tcp_header = packet[20:40]
                        tcph = struct.unpack("!HHLLBBHHH", tcp_header)

                        src_port = tcph[0]
                        dst_port = tcph[1]

                        # Filtrar porta 6668 (Tuya)
                        if src_port == 6668 or dst_port == 6668:
                            # Extrair payload
                            header_length = 40
                            payload = packet[header_length:]

                            if len(payload) > 0:
                                timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]

                                print(f"\n📦 Pacote #{packet_count} ({timestamp})")
                                print(f"   {src_ip}:{src_port} → {dst_ip}:{dst_port}")
                                print(f"   Tamanho: {len(payload)} bytes")

                                # Verificar se é pacote Tuya (prefix 000055aa)
                                if payload[:4] == b"\x00\x00\x55\xaa":
                                    print(f"   ✅ PACOTE TUYA DETECTADO!")

                                    # Tentar extrair informações
                                    self._analyze_tuya_packet(payload)

                                # Mostrar hex
                                print(f"   Hex: {payload[:100].hex()}")

                                # Procurar por possível Local Key
                                self._search_local_key(payload)

                                # Salvar
                                self.captured_packets.append(
                                    {
                                        "timestamp": timestamp,
                                        "src": f"{src_ip}:{src_port}",
                                        "dst": f"{dst_ip}:{dst_port}",
                                        "payload": payload.hex(),
                                    }
                                )

                except socket.timeout:
                    continue
                except KeyboardInterrupt:
                    break

            sock.close()

            print(f"\n✅ Captura finalizada!")
            print(f"📊 Total de pacotes capturados: {packet_count}")

            # Salvar resultados
            self._save_results()

        except PermissionError:
            print(f"❌ Erro: Requer permissões de root")
            print(f"💡 Execute: sudo python scripts/sniff_novadigital.py")
        except Exception as e:
            print(f"❌ Erro: {e}")

    def _analyze_tuya_packet(self, payload):
        """Analisar pacote Tuya"""
        try:
            # Extrair campos
            seqno = struct.unpack(">I", payload[4:8])[0]
            command = struct.unpack(">I", payload[8:12])[0]
            length = struct.unpack(">I", payload[12:16])[0]

            print(f"   📋 Tuya Packet:")
            print(f"      SeqNo: {seqno}")
            print(f"      Command: 0x{command:02x}")
            print(f"      Length: {length}")

            # Tentar extrair JSON
            if length > 8:
                payload_start = 20
                payload_end = 20 + length - 8
                data = payload[payload_start:payload_end]

                if b"{" in data:
                    print(f"      ✅ JSON detectado!")
                    try:
                        import json

                        json_str = data.decode("utf-8")
                        json_data = json.loads(json_str)
                        print(f"      📄 {json.dumps(json_data, indent=6)}")

                        # Procurar Local Key no JSON
                        if "localKey" in json_str or "local_key" in json_str:
                            print(f"      🎉 LOCAL KEY ENCONTRADA NO JSON!")
                    except:
                        pass

        except Exception as e:
            print(f"      ⚠️ Erro ao analisar: {e}")

    def _search_local_key(self, payload):
        """Procurar por possível Local Key"""
        # Local Key é 32 caracteres hexadecimais
        hex_str = payload.hex()

        # Procurar padrões de 32 caracteres hex
        pattern = r"[0-9a-f]{32}"
        matches = re.findall(pattern, hex_str)

        if matches:
            for match in matches:
                # Verificar se não é apenas zeros ou padrão repetitivo
                if match != "0" * 32 and len(set(match)) > 4:
                    print(f"   🔑 Possível Local Key: {match}")

    def _save_results(self):
        """Salvar resultados"""
        import json

        filename = f"sniff_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        with open(filename, "w") as f:
            json.dump(self.captured_packets, f, indent=2)

        print(f"📁 Resultados salvos em: {filename}")


def main():
    """Função principal"""
    print("🎯 SNIFFER NOVADIGITAL")
    print("=" * 60)
    print()
    print("Este sniffer captura tráfego da tomada NovaDigital")
    print("e procura pela Local Key nos pacotes.")
    print()
    print("⚠️ IMPORTANTE:")
    print("   - Requer permissões de root (sudo)")
    print("   - Funciona melhor no macOS/Linux")
    print("   - No Windows, use Wireshark")
    print()

    try:
        sniffer = TuyaSniffer(target_ip="192.168.68.100")
        sniffer.sniff(duration_seconds=60)

        print(f"\n💡 PRÓXIMOS PASSOS:")
        print(f"   1. Analise os resultados salvos")
        print(f"   2. Se encontrou Local Key, configure no .env")
        print(f"   3. Se não encontrou, tente:")
        print(f"      - Desligar/ligar a tomada durante captura")
        print(f"      - Usar app Tuya Smart durante captura")
        print(f"      - Capturar por mais tempo")

    except KeyboardInterrupt:
        print(f"\n⏹️ Captura interrompida")


if __name__ == "__main__":
    main()
