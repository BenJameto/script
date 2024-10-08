#!/bin/bash

# Directorio donde se almacenarán las configuraciones de los pods
PODS_BACKUP_DIR="$HOME/.k8s_pods_backup"

function save_pods() {
    # Crear el directorio si no existe
    mkdir -p "$PODS_BACKUP_DIR"

    # Obtener todos los pods en todos los namespaces
    # Excluimos los pods que forman parte de un controlador (como Deployments) para evitar problemas
    kubectl get pods --all-namespaces -o json \
    | jq -c '.items[] | select(.metadata.ownerReferences == null)' \
    | while read -r pod; do
        namespace=$(echo "$pod" | jq -r '.metadata.namespace')
        name=$(echo "$pod" | jq -r '.metadata.name')

        # Crear el directorio del namespace si no existe
        mkdir -p "$PODS_BACKUP_DIR/$namespace"

        # Obtener la definición del pod y guardarla en un archivo YAML
        kubectl get pod "$name" -n "$namespace" -o yaml > "$PODS_BACKUP_DIR/$namespace/${name}.yaml"
        echo "Configuración del pod $name en el namespace $namespace guardada."
    done

    echo "Se han guardado las configuraciones de los pods."
}

function delete_pods() {
    # Obtener todos los pods en todos los namespaces
    # Excluimos los pods controlados por controladores
    kubectl get pods --all-namespaces -o json \
    | jq -c '.items[] | select(.metadata.ownerReferences == null)' \
    | while read -r pod; do
        namespace=$(echo "$pod" | jq -r '.metadata.namespace')
        name=$(echo "$pod" | jq -r '.metadata.name')

        # Eliminar el pod
        kubectl delete pod "$name" -n "$namespace"
        echo "Pod $name en el namespace $namespace eliminado."
    done

    echo "Se han eliminado los pods."
}

function restore_pods() {
    # Restaurar los pods desde las configuraciones guardadas
    for namespace_dir in "$PODS_BACKUP_DIR"/*; do
        namespace=$(basename "$namespace_dir")
        for pod_file in "$namespace_dir"/*.yaml; do
            kubectl apply -f "$pod_file" -n "$namespace"
            echo "Pod restaurado desde $pod_file en el namespace $namespace."
        done
    done

    echo "Se han restaurado los pods desde las configuraciones previas."
}

function usage() {
    echo "Uso: $0 [save|delete|restore]"
    exit 1
}

# Verificar que se proporcionó una acción
if [ $# -ne 1 ]; then
    usage
fi

action=$1

case "$action" in
    save)
        save_pods
        ;;
    delete)
        delete_pods
        ;;
    restore)
        restore_pods
        ;;
    *)
        echo "Acción no reconocida."
        usage
        ;;
esac
