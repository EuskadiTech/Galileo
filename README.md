# Galileo
Un programa todo en uno.

## Instalación 
### Docker
```bash
docker run -p 8129:8129 -v ./GalileoDat:/data ghcr.io/naielv/galileo:main
```
## Configuración
Ejemplo:
```json
{
  "Resumen Diario": {
    "Weather": { "Enabled": true, "Location": "Ortuella" },
    "Jokes": { "Enabled": true, "Url": "https://naiel.fyi/chistes.txt" }
  },
  "Clave Proxy": "<CHANGE THIS>"
}
```