---

## ⚙️ Configuración

Todo configurable en `config.yaml` sin tocar el código:

```yaml
ibex35:
  periodo: "1y"
  empresas:
    Santander: "SAN.MC"
    BBVA: "BBVA.MC"
    # ... hasta 14 empresas

alertas:
  umbral_caida: 3.0
  umbral_subida: 3.0

ia:
  proveedor: "gemini"
  modelo: "gemini-1.5-flash"
```

---

## 🔒 Seguridad

Las API Keys se gestionan mediante variables de entorno en `.env` (excluido de Git). 