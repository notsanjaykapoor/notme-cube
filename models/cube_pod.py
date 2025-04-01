import dataclasses


@dataclasses.dataclass
class CubePod:
    c_command: str
    c_env: str
    c_image: str
    c_name: str
    c_network: str
    c_ports: list[int]
    project_name: str


    def docker_run(self, detach: int) -> str:
        """
        Return docker run cmd
        """
        cmd = "docker run --rm"

        if detach == 1:
            cmd = f"{cmd} -d"

        cmd = f"{cmd} --name {self.c_name} --network {self.c_network} --env-file {self.c_env}"

        for port in self.c_ports:
            cmd = f"{cmd} -p {port}:{port}"

        cmd = f"{cmd} {self.c_image} {self.c_command}"

        return cmd
