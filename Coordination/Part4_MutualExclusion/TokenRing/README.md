# Implement the Token Ring Nodes

## file: node.py to represent a distributed approach.

Each node will connect to its "next" neighbor to form a logical ring. A single "Token" message will be passed around. A node can only access the shared resource if it holds the token. Once it finishes, it passes the token to the next node. If a node receives the token but does not need the resource, it simply forwards it immediately.
