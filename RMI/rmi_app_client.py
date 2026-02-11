import random as rd
import xmlrpc.client

# Create a client proxy
proxy = xmlrpc.client.ServerProxy("http://localhost:12000/RPC2")

complex_numbers=[]
operations=['add', 'sub', 'prod', 'div']
for i in range(20):
    real= rd.randint(1,20)
    imag= rd.randint(1,20)
    comp_number=(real,imag)
    complex_numbers.append(comp_number)

while complex_numbers:
    operation=operations[rd.randint(0,3)]
    factor_1=complex_numbers.pop()
    factor_2=complex_numbers.pop()
    n1=complex(factor_1[0],factor_1[1])
    n2=complex(factor_2[0],factor_2[1])
    result=proxy.operate(factor_1,factor_2,operation)
    number=complex(result[0],result[1])
    print("_______________________________________")
    print(f"factor 1: {n1}")
    print(f"factor 2: {n2}")
    print(f"operation: {operation}")
    print(f"result: {number}")
