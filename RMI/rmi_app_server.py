from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler

# Restrict to a particular path.
class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)

address='localhost'
port= 12000

with SimpleXMLRPCServer((address,port),
                        requestHandler=RequestHandler) as server:
    server.register_introspection_functions()
    
    def operate(a,b, operation):
        # operations=['add', 'sub', 'prod', 'div']
        # if operation not in operations:
        #     return None
        comp_1=complex(a[0],a[1])
        comp_2=complex(b[0],b[1])

        match operation:
            case 'add':
                result=comp_1+comp_2
                to_send=(result.real,result.imag)
                return to_send
            case 'sub':
                result=comp_1-comp_2
                to_send=(result.real,result.imag)
                return to_send
            case 'prod':
                result=comp_1*comp_2
                to_send=(result.real,result.imag)
                return to_send
            case 'div':
                result=comp_1/comp_2
                to_send=(result.real,result.imag)
                return to_send
            case _:
                return None
    server.register_function(operate,'operate')

     # Run the server's main loop
    print("Server is listening on port 12000...")
    server.serve_forever()
