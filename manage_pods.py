import os
import sys
import yaml
from kubernetes import client, config

# Ruta donde se almacenarán las configuraciones de los pods
PODS_BACKUP_DIR = os.path.expanduser('~/.k8s_pods_backup')

def save_pods():
    config.load_kube_config()
    v1 = client.CoreV1Api()
    
    # Crear el directorio si no existe
    os.makedirs(PODS_BACKUP_DIR, exist_ok=True)
    
    # Obtener todos los pods en todos los namespaces
    pods = v1.list_pod_for_all_namespaces(watch=False)
    
    for pod in pods.items:
        namespace = pod.metadata.namespace
        name = pod.metadata.name
        
        # Obtener la definición del pod
        pod_def = v1.read_namespaced_pod(name, namespace)
        
        # Serializar la definición del pod a YAML
        pod_def_dict = client.ApiClient().sanitize_for_serialization(pod_def)
        pod_def_yaml = yaml.dump(pod_def_dict)
        
        # Guardar la definición en un archivo YAML
        pod_dir = os.path.join(PODS_BACKUP_DIR, namespace)
        os.makedirs(pod_dir, exist_ok=True)
        pod_file = os.path.join(pod_dir, f"{name}.yaml")
        
        with open(pod_file, 'w') as f:
            f.write(pod_def_yaml)
    print("Se han guardado las configuraciones de los pods.")
    
def delete_pods():
    config.load_kube_config()
    v1 = client.CoreV1Api()
    
    # Obtener todos los pods en todos los namespaces
    pods = v1.list_pod_for_all_namespaces(watch=False)
    
    for pod in pods.items:
        namespace = pod.metadata.namespace
        name = pod.metadata.name
        
        # Eliminar el pod
        v1.delete_namespaced_pod(name, namespace)
        print(f"Pod {name} en el namespace {namespace} eliminado.")
        
def restore_pods():
    config.load_kube_config()
    for root, dirs, files in os.walk(PODS_BACKUP_DIR):
        for file in files:
            if file.endswith('.yaml'):
                pod_file = os.path.join(root, file)
                
                # Restaurar el pod usando kubectl
                os.system(f"kubectl apply -f {pod_file}")
                
    print("Se han restaurado los pods desde las configuraciones previas.")
    
def main():
    if len(sys.argv) != 2:
        print("Uso: python manage_pods.py [save|delete|restore]")
        sys.exit(1)
        
    action = sys.argv[1]
    
    if action == 'save':
        save_pods()
    elif action == 'delete':
        delete_pods()
    elif action == 'restore':
        restore_pods()
    else:
        print("Acción no reconocida. Uso: python manage_pods.py [save|delete|restore]")
        sys.exit(1)
        
if __name__ == '__main__':
    main()
