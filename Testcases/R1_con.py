from http import HTTPStatus
from threading import Thread
import requests

# concurrent test case
# Check if concurrent requests to '/acceptOrder' is updating the data consistently

# RESTAURANT SERVICE    : http://localhost:8080
# DELIVERY SERVICE      : http://localhost:8081
# WALLET SERVICE        : http://localhost:8082

def assureAllAgentSignOut():
    """required after renitializing delivery"""
    agents = [201, 202, 203]
    for agent in agents:
        # wait till status becomes signed-out
        while True:
            http_response = requests.get(f"http://localhost:8081/agent/{agent}")
            agent_status = http_response.json().get("status")
            if agent_status=="signed-out": break


def t1(result):  # First concurrent request

    # order of item 1, quantity 4 from restaurant 101

    http_response = requests.post(
        "http://localhost:8080/acceptOrder", json={"restId": 101, "itemId": 1, "qty": 4}
    )

    result["1"] = http_response


def t2(result):  # Second concurrent request

    # order of item 1, quantity 5 from restaurant 101

    http_response = requests.post(
        "http://localhost:8080/acceptOrder", json={"restId": 101, "itemId": 1, "qty": 5}
    )

    result["2"] = http_response


def test():

    result = {}

    # Reinitialize Restaurant service

    http_response = requests.post("http://localhost:8080/reInitialize")

    # ## Parallel Execution Begins ###

    thread1 = Thread(target=t1, kwargs={"result": result})
    thread2 = Thread(target=t2, kwargs={"result": result})

    thread1.start()
    thread2.start()

    thread1.join()
    thread2.join()

    # ## Parallel Execution Ends ###

    status_code1 = result["1"].status_code

    status_code2 = result["2"].status_code

    if status_code1 != 201 or status_code2 != 201:
        return "Fail"

    # check whether the item counts are updated by concurrent 
    # exection as expected by serial execution
    
    http_response = requests.post(
        "http://localhost:8080/acceptOrder", json={"restId": 101, "itemId": 1, "qty": 2}
    )

    if http_response.status_code != 410:
        return "Fail"

    http_response = requests.post(
        "http://localhost:8080/acceptOrder", json={"restId": 101, "itemId": 1, "qty": 1}
    )

    if http_response.status_code != 201:
        return "Fail"

    return "Pass"


if __name__ == "__main__":

    print(test())
