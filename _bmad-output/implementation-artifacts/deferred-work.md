# Deferred Work

## Deferred from: code review of 1-1-projectspec-dataclass (2026-06-23)

- **Bool coercion silencieux dans `from_dict`** — `d.get("copyToSystemFolders", False)` accepte n'importe quelle valeur truthy sans conversion vers `bool`. Les callers actuels fournissent tous des bools propres, mais un futur caller direct pourrait passer une string et casser `_on_off()` dans `render_context.py`. À surveiller lors de l'intégration story 1.2/1.3.
- **Defaults non liés entre champ dataclass et fallback `from_dict`** — Les defaults du champ (`copy_to_artefacts_dir: bool = True`) et du fallback `from_dict` (`d.get("copyToArtefactsDir", True)`) sont synchronisés manuellement. Un changement de l'un sans l'autre est un bug silencieux. Considérer une constante partagée lors d'un refactor futur.
