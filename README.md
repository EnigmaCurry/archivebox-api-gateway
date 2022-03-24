# archivebox-api-gateway

status: alpha

[ArchiveBox](https://github.com/archivebox/archivebox) is a cool open-source
website archiving platform. However, it's [currently missing a REST
API](https://github.com/ArchiveBox/ArchiveBox/issues/496). This project is an
API wrapper service for ArchiveBox. 

**This project requires to be deployed via
[d.rymcg.tech](https://github.com/EnigmaCurry/d.rymcg.tech/tree/master/archivebox),
using the Traefik HTTP reverse proxy. The
[docker-compose.yaml](https://github.com/EnigmaCurry/d.rymcg.tech/blob/master/archivebox/docker-compose.yml)
defines important HTTP Basic Authentication. Deploying directly from this
repository without Traefik is not supported.**

