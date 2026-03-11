class VectorClock:

    def __init__(self,node_id: str):
        self.node_id = node_id
        # The clock is a dictionary mapping node IDs to their logical timestamps
        self.clock = {node_id: 0}

    def tick(self) -> None:
        """
        Rule 1: Increment the local clock counter before executing and event.
        """
        if self.node_id not in self.clock:
            self.clock[self.node_id] = 0

        self.clock[self.node_id] += 1

    def send_event(self) -> dict:
        """
        Rule 2: When sending a message, the node increments its clock and sends a copy of its current vector.
        """

        self.tick()
        # Return a copy to simulate the payload being sent over the network
        return self.clock.copy()

    def receive_event(self, incoming_vector: dict) -> None:
        """
        Rule 3: On receiving a message, update the local clock by taking the maximum value for each node's time stamp, then increment the local clock.
        """
        
        for node, timestamp in incoming_vector.items():
            if node in self.clock:
                #Update with the maximum known logical time
                self.clock[node] = max(self.clock[node],timestamp)
            else:
                #Discovering anew node in the system
                self.clock[node] = timestamp
                
        #Increment local clock after receiving (as receiving is an event)
        self.tick()
        
    def get_state(self) -> dict:
        """ Returns the current state of the vector clock"""
        return self.clock

class CausalityChecker:
    """ 
    A utility class to compare two vector clocks and determine their casual relationship.
    """

    @staticmethod
    def compare(vector_a:dict, vector_b:dict) ->str:
        """
        Compares two vector clocks (A and B).
        Returns the causal relationship:
        - "A -> B": A happened before B
        - "B -> A": B happened before A
        - "Concurrent": A and B happened concurrently (A||B)
        - "Equal": The vector are identical
        """

        # Get all unique nodes from both vector

        all_nodes = set(vector_a.keys()).union(set(vector_b.keys()))

        a_is_less_or_equal = True
        b_is_less_or_equal = True
        is_strictly_equal = True

        for node in all_nodes:
            # If a node is missing from one vector, its logical time is 0
            time_a = vector_a.get(node,0)

            time_b = vector_b.get(node,0)

            if time_a != time_b:
                is_strictly_equal = False

            # If A has a strictly greater value, it cannot be less than or equal to B
            if time_a > time_b:
                a_is_less_or_equal = False

            # If A has a strictly greater value, it cannot be less than or equal to B
            if time_b > time_a:
                b_is_less_or_equal = False

        # Evaluate the mathematical conditions

        if is_strictly_equal:
            return "Equal"
        elif a_is_less_or_equal and not is_strictly_equal:
            return "A -> B (A happened before B)"
        elif b_is_less_or_equal and not is_strictly_equal:
            return "B -> A (B happened before A)"
        else:
            return "Concurrent (A || B)"

if __name__ == "__main__":
    # Initialize three nodes for our distributed system
    node_1 = VectorClock("Node_1")
    node_2 = VectorClock("Node_2")
    node_3 = VectorClock("Node_3")

    print("--- 1. Strictly Equal (A = B) ---")
    # Both states are taken at the exact same logical time without any events happening
    state_a = node_1.get_state().copy()
    state_b = node_1.get_state().copy()

    print(f"State A: {state_a}")
    print(f"State B: {state_b}")
    print(f"Relationship: {CausalityChecker.compare(state_a, state_b)}")

    print("\n--- 2. Causal Relationship (A -> B) ---")
    # Node 1 executes an event and sends a message to Node 2
    msg_from_1 = node_1.send_event()
    node_2.receive_event(msg_from_1)

    # We compare the payload Node 1 sent with the new state of Node 2
    state_a = msg_from_1
    state_b = node_2.get_state().copy()

    print(f"State A (Sent by Node 1): {state_a}")
    print(f"State B (After Node 2 receives): {state_b}")
    print(f"Relationship: {CausalityChecker.compare(state_a, state_b)}")

    print("\n--- 3. Causal Relationship Reverse (B -> A) ---")
    # Now Node 2 does some internal work, then sends a message back to Node 1
    node_2.tick()
    msg_from_2 = node_2.send_event()
    node_1.receive_event(msg_from_2)

    # We compare the payload Node 2 sent with the new state of Node 1
    # Passing msg_from_2 first to see if the checker detects that the first argument caused the second
    state_b = msg_from_2
    state_a = node_1.get_state().copy()

    print(f"State A (Sent by Node 2): {state_a}")
    print(f"State B (After Node 1 receives): {state_b}")
    print(f"Relationship: {CausalityChecker.compare(state_a, state_b)}")

    print("\n--- 4. Concurrent Events (A || B) ---")
    # Now, Node 1 and Node 2 both do something independently at the exact same time.
    # They do NOT communicate with each other.
    node_1.tick()
    state_c = node_1.get_state().copy()

    node_2.tick()
    state_d = node_2.get_state().copy()

    print(f"State C (Node 1 independent event): {state_c}")
    print(f"State D (Node 2 independent event): {state_d}")
    print(f"Relationship: {CausalityChecker.compare(state_c, state_d)}")

    print("\n--- 5. Edge Case: Disjoint Vectors / Unseen Nodes (Concurrent) ---")
    # Node 3 wakes up and does something independently.
    # It has never spoken to Node 1 or Node 2, meaning they don't even share dictionary keys.
    node_3.tick()
    state_e = node_3.get_state().copy()

    # Let's compare Node 3's state with Node 1's state.
    # Because neither knows about the other's events, this MUST mathematically be Concurrent.
    state_f = node_1.get_state().copy()

    print(f"State E (Node 3's isolated state): {state_e}")
    print(f"State F (Node 1's current state): {state_f}")
    print(f"Relationship: {CausalityChecker.compare(state_e, state_f)}")
