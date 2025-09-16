from locust import HttpUser, task, between

class PokeUser(HttpUser):
    wait_time = between(1, 3)

    @task
    def get_pikachu(self):
        self.client.get("/api/v2/pokemon/pikachu", name="/pokemon/pikachu")
