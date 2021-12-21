Needs a secret in kubernetes with name: `datasafe-keys`, which holds "privateKeys.pem" and "publicKeys.pem".

This will be distributed through the datasafe team.

You need private and public keys for communication with datasafe. Store them in kubernetes with the following command.

```bash
kubectl create secret generic datasafe-keys --from-file=privateKey.pem --from-file=publicKey.pem
```

To install the connector, you can use this chart manifest with the following command. Beware, that you need to configure the `values.yaml.example` to your needs and rename it to `values.yaml`.

```bash
helm upgrade layer1-datasafe ./ -i --values values.yaml
```

Uninstall the manifest with the following command, if you use the same name as the command above.

```bash
helm uninstall layer1-datasafe
```