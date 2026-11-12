"""locust -f locustfile.py --host=http://127.0.0.1:8005"""
from locust import HttpUser, task, between

_QUERIES = [
    "how does retrieval augmented generation work",
    "what is a vector embedding",
    "explain chunk overlap",
    "why is cosine similarity used for retrieval",
]


class AppUser(HttpUser):
    wait_time = between(1, 3)

    @task(3)
    def query(self):
        self.client.post("/query", json={"query": _QUERIES[0], "top_k": 5})

    @task(2)
    def cpu_bound(self):
        self.client.get("/cpu-bound")

    @task(1)
    def cpu_task(self):
        self.client.get("/tasks/cpu/matrix")

    @task(1)
    def io_task(self):
        self.client.get("/tasks/io/network")

    @task(1)
    def health(self):
        self.client.get("/health")
