from server.model import World


class WebRtcManager:
    def __init__(self, world: World):
        self.world = world

    def send_offer(self, from_peer_id: str, to_peer_id: str, offer):
        """Handle sending WebRTC offer from one peer to another"""
        print(f"Sending offer from {from_peer_id} to {to_peer_id}")
        # TODO: Implement offer forwarding logic
        pass

    def send_answer(self, from_peer_id: str, to_peer_id: str, answer):
        """Handle sending WebRTC answer from one peer to another"""
        print(f"Sending answer from {from_peer_id} to {to_peer_id}")
        # TODO: Implement answer forwarding logic
        pass

    def send_ice_candidate(self, from_peer_id: str, to_peer_id: str, ice_candidate):
        """Handle sending ICE candidate from one peer to another"""
        print(f"Sending ICE candidate from {from_peer_id} to {to_peer_id}")
        # TODO: Implement ICE candidate forwarding logic
        pass
