The files must be deployed in the following order:
1. Config and secret YAMLs (i.e. postgres-config, postgres-secret, redis-config)
2. Database and cache YAMLs (i.e. postgres, redis)
3. Application YAMLs (i.e. django)
4. Ingress YAML