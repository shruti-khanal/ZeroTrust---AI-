# ==================================================
# ZERO TRUST AI - DATA STRUCTURES
# Hash Table + Graph + Priority Queue
# ==================================================


# ==================================================
# HASH TABLE
# ==================================================

class UserHashTable:

    def __init__(self):

        self.table = {}


    def add_user(
        self,
        username,
        device
    ):

        self.table[username] = {

            "device":
                device,

            "access_count":
                0,

            "failed_attempts":
                0

        }


    def get_user(
        self,
        username
    ):

        return self.table.get(
            username
        )


    def record_access(
        self,
        username
    ):

        if username in self.table:

            self.table[
                username
            ]["access_count"] += 1


# ==================================================
# CREATE HASH TABLE
# ==================================================

user_hash_table = UserHashTable()


# ==================================================
# GRAPH
# ==================================================

class AccessGraph:

    def __init__(self):

        self.graph = {}


    def add_connection(
        self,
        user,
        resource
    ):

        if user not in self.graph:

            self.graph[user] = []


        if resource not in self.graph[user]:

            self.graph[user].append(
                resource
            )


    def get_user_resources(
        self,
        user
    ):

        return self.graph.get(
            user,
            []
        )


    def get_graph(self):

        return self.graph


# ==================================================
# CREATE GRAPH
# ==================================================

access_graph = AccessGraph()


# ==================================================
# PRIORITY QUEUE
# ==================================================

class RiskPriorityQueue:

    def __init__(self):

        self.queue = []


    def add_request(
        self,
        username,
        resource,
        risk_score,
        risk_level
    ):

        request = {

            "username":
                username,

            "resource":
                resource,

            "risk_score":
                risk_score,

            "risk_level":
                risk_level

        }


        self.queue.append(
            request
        )


        self.queue.sort(

            key=lambda item:
                item["risk_score"],

            reverse=True

        )


    def get_highest_priority(self):

        if len(self.queue) == 0:

            return None

        return self.queue[0]


    def get_all_requests(self):

        return self.queue


# ==================================================
# CREATE PRIORITY QUEUE
# ==================================================

risk_priority_queue = (
    RiskPriorityQueue()
)


# ==================================================
# PROCESS ACCESS REQUEST
# ==================================================

def process_access_request(
    username,
    resource,
    device,
    risk_score,
    risk_level
):

    # HASH TABLE

    if user_hash_table.get_user(
        username
    ) is None:

        user_hash_table.add_user(
            username,
            device
        )


    user_hash_table.record_access(
        username
    )


    # GRAPH

    access_graph.add_connection(
        username,
        resource
    )


    # PRIORITY QUEUE

    risk_priority_queue.add_request(

        username,

        resource,

        risk_score,

        risk_level

    )


# ==================================================
# GET DSA INFORMATION
# ==================================================

def get_dsa_information():

    return {

        "users":
            user_hash_table.table,

        "access_graph":
            access_graph.get_graph(),

        "priority_queue":
            risk_priority_queue.get_all_requests()

    }