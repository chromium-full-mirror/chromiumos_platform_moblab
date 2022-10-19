import docker
import cherrypy
from cherrypy.process import plugins
import logging

CHECK_INTERVAL_SEC = 3600

class DockerMonitor(object):
    def __init__(self, containers=None):
        if containers:
            self.containers = list(map(lambda name: DockerContainer(name), containers))
        else:
            self.containers = []

    def startCollection(self, interval=CHECK_INTERVAL_SEC, run_immediately_when_start=False):
        if self.containers:
            self.monitor = plugins.Monitor(
                cherrypy.engine,
                self._collect,
                frequency=interval,

            )
            self.monitor.subscribe()
            if run_immediately_when_start:
                self._collect()

    def _collect(self):
        for container in self.containers:
            container.collect_status()


class ContainerNotExist(Exception):
    pass


def checkConrainerIsExist(name):
    try:
        client = docker.from_env()
        container = client.containers.get(name)
        return container is not None
    except (docker.errors.NotFound, docker.errors.APIError):
        return False


class DockerContainer(object):
    def __init__(self, container_name):
        self.container_name = container_name

    def container(self):
        if checkConrainerIsExist(self.container_name):
            client = docker.APIClient()
            container = client.inspect_container(self.container_name)
            return container
        else:
            raise ContainerNotExist()

    def started_at(self):
        info = self.container()
        containerState = info.get("State")
        startTime = containerState.get("StartedAt").split(".")[0]
        return startTime

    def status(self):
        info = self.container()
        containerState = info.get("State")
        return containerState["Status"]

    def collect_status(self):
        try:
            startTimestamp = self.started_at()
            status = self.status()
            logging.info(f"{self.container_name} start time is {startTimestamp}, status: {status}")
        except ContainerNotExist as e:
                logging.error(f"{self.container_name} doesn't exist.")

