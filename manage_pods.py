import os
import sys
import yaml
from kubernetes import client, config

# Ruta donde se almacenarán las configuraciones
BACKUP_DIR = os.path.expanduser('~/.k8s_backup')

def save_resources():
    config.load_kube_config()
    apps_v1 = client.AppsV1Api()
    core_v1 = client.CoreV1Api()

    # Crear el directorio si no existe
    os.makedirs(BACKUP_DIR, exist_ok=True)

    # Guardar Deployments
    deployments = apps_v1.list_deployment_for_all_namespaces()
    for dep in deployments.items:
        namespace = dep.metadata.namespace
        name = dep.metadata.name

        dep_def = apps_v1.read_namespaced_deployment(name, namespace)
        dep_def_dict = client.ApiClient().sanitize_for_serialization(dep_def)
        dep_def_yaml = yaml.dump(dep_def_dict)

        dep_dir = os.path.join(BACKUP_DIR, 'deployments', namespace)
        os.makedirs(dep_dir, exist_ok=True)
        dep_file = os.path.join(dep_dir, f"{name}.yaml")

        with open(dep_file, 'w') as f:
            f.write(dep_def_yaml)

    # Puedes repetir el mismo proceso para otros recursos como Services, ConfigMaps, etc.

    print("Se han guardado las configuraciones de los Deployments.")

def delete_resources():
    config.load_kube_config()
    apps_v1 = client.AppsV1Api()

    # Eliminar Deployments
    deployments = apps_v1.list_deployment_for_all_namespaces()
    for dep in deployments.items:
        namespace = dep.metadata.namespace
        name = dep.metadata.name

        apps_v1.delete_namespaced_deployment(name, namespace)
        print(f"Deployment {name} en el namespace {namespace} eliminado.")

    # Si deseas eliminar otros recursos, agrégalos aquí.

def restore_resources():
    config.load_kube_config()
    # Restaurar Deployments
    deployments_dir = os.path.join(BACKUP_DIR, 'deployments')
    for root, dirs, files in os.walk(deployments_dir):
        for file in files:
            if file.endswith('.yaml'):
                dep_file = os.path.join(root, file)
                os.system(f"kubectl apply -f {dep_file}")

    print("Se han restaurado los Deployments desde las configuraciones previas.")

def main():
    if len(sys.argv) != 2:
        print("Uso: python manage_resources.py [save|delete|restore]")
        sys.exit(1)

    action = sys.argv[1]

    if action == 'save':
        save_resources()
    elif action == 'delete':
        delete_resources()
    elif action == 'restore':
        restore_resources()
    else:
        print("Acción no reconocida. Uso: python manage_resources.py [save|delete|restore]")
        sys.exit(1)

if __name__ == '__main__':
    main()
