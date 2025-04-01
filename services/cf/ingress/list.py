import dataclasses
import re

import models
import services.cf
import services.mql


@dataclasses.dataclass
class Struct:
    code: int
    ingress_list: list[models.CloudflareIngress]
    errors: list[str]


def list(query: str="") -> list[models.CloudflareIngress]:
    """
    """
    struct = Struct(
        code=0,
        ingress_list=[],
        errors=[],
    )

    client = services.cf.client()
    account_id = services.cf.account_id()

    # get tunnels that are not deleted
    tunnels = client.zero_trust.tunnels.list(
        account_id=account_id,
        is_deleted=False,
    )

    for tunnel in tunnels.result:
        # get tunnel config
        config = client.zero_trust.tunnels.cloudflared.configurations.get(
            tunnel_id=tunnel.id,
            account_id=account_id,
        )

        ingress_list = config.config.ingress

        for ingress in ingress_list:
             model = models.CloudflareIngress(
                 hostname=ingress.hostname,
                 path=ingress.path,
                 service=ingress.service,
                 tunnel_id=tunnel.id,
                 tunnel_name=tunnel.name,
                 tunnel_status=tunnel.status,
             )
             struct.ingress_list.append(model)

    struct_tokens = services.mql.parse(query=query)

    for token in struct_tokens.tokens:
        value = token["value"]

        if token["field"] == "name":
            if re.match(r"^~", value):
                # remove ~
                value_normal = re.sub(r"~", "", value)
            else:
                value_normal = value
            
            struct.ingress_list = [ingress for ingress in struct.ingress_list if value_normal in ingress.tunnel_name] 
        elif token["field"] == "port":
            struct.ingress_list = [ingress for ingress in struct.ingress_list if value in ingress.service] 
        elif token["field"] == "status":
            struct.ingress_list = [ingress for ingress in struct.ingress_list if ingress.tunnel_status == value] 

    struct.ingress_list.sort(key=lambda o: f"{o.tunnel_name} {o.hostname}")

    return struct

