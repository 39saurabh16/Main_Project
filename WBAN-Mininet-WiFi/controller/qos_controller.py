 

from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER, CONFIG_DISPATCHER, set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet, ethernet, ipv4, udp, tcp
import requests                                            # REST call to your ML‑IDS

ML_IDS_URL = "http://127.0.0.1:5000/ids/predict"           # adjust to your flask/fastapi service
CRITICAL_DSCP = 46                                         # Expedited‑Forwarding
HIGH_Q = 0
NORMAL_Q = 1

class QoSController(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def add_flow(self, datapath, priority, match, actions, idle=0, hard=0):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
                                             actions)]
        mod = parser.OFPFlowMod(datapath=datapath,
                                priority=priority,
                                idle_timeout=idle,
                                hard_timeout=hard,
                                match=match,
                                instructions=inst)
        datapath.send_msg(mod)

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        """Install table‑miss rule."""
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser  = datapath.ofproto_parser
        match   = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                          ofproto.OFPCML_NO_BUFFER)]
        self.add_flow(datapath, 0, match, actions)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self, ev):
        msg       = ev.msg
        datapath  = msg.datapath
        ofproto   = datapath.ofproto
        parser    = datapath.ofproto_parser
        in_port   = msg.match['in_port']

        pkt  = packet.Packet(msg.data)
        eth  = pkt.get_protocol(ethernet.ethernet)
        ip4  = pkt.get_protocol(ipv4.ipv4)

        # ignore LLDP/BPDU
        if eth.ethertype < 0x0600:
            return

        # FIX: ignore packets without IPv4 header
        if ip4 is None:
            return

        ### 1️⃣ Classify QoS
        queue_id = NORMAL_Q
        if ip4.tos >> 2 == CRITICAL_DSCP:
            queue_id = HIGH_Q

        ### 2️⃣ (Optional) call ML IDS for new flows
        verdict_drop = False
        try:
            payload = {"src": ip4.src, "dst": ip4.dst,
                    "proto": ip4.proto, "tos": ip4.tos}
            r = requests.post(ML_IDS_URL, json=payload, timeout=0.2)
            verdict_drop = r.json().get("attack", False)
        except Exception:
            self.logger.warning("IDS offline – default allow")

        ### 3️⃣ Decide forwarding
        if verdict_drop:
            match = parser.OFPMatch(eth_type=0x0800,
                                    ipv4_src=ip4.src,
                                    ipv4_dst=ip4.dst)
            self.add_flow(datapath, 200, match, [], hard=30)
            return  # drop packet (do not forward)

        # Forwarding (flood out all ports)
        out_port = ofproto.OFPP_FLOOD
        actions  = [parser.OFPActionSetQueue(queue_id),
                    parser.OFPActionOutput(out_port)]

        ### 4️⃣ Install forwarding rule
        match = parser.OFPMatch(in_port=in_port,
                                eth_type=0x0800,
                                ipv4_src=ip4.src,
                                ipv4_dst=ip4.dst)
        self.add_flow(datapath, 100 if queue_id == HIGH_Q else 10,
                    match, actions, idle=60)

        # Send the current packet out
        out = parser.OFPPacketOut(datapath=datapath,
                                buffer_id=msg.buffer_id,
                                in_port=in_port,
                                actions=actions,
                                data=None if msg.buffer_id
                                            != ofproto.OFP_NO_BUFFER else msg.data)
        datapath.send_msg(out)
