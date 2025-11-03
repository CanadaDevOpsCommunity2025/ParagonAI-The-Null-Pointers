from typing import Dict, Any
import logging
import json

logger = logging.getLogger(__name__)


class MonitoringService:
    def generate_prometheus_config(self, config: Dict[str, Any]) -> str:
        """Generate Prometheus configuration"""
        app_name = config.get("app_name", "agent-app")
        namespace = config.get("namespace", "default")
        
        prometheus_config = f"""apiVersion: v1
kind: ConfigMap
metadata:
  name: prometheus-config
  namespace: {namespace}
data:
  prometheus.yml: |
    global:
      scrape_interval: 15s
      evaluation_interval: 15s
    
    scrape_configs:
      - job_name: '{app_name}'
        kubernetes_sd_configs:
          - role: pod
            namespaces:
              names:
                - {namespace}
        relabel_configs:
          - source_labels: [__meta_kubernetes_pod_label_app]
            action: keep
            regex: {app_name}
          - source_labels: [__meta_kubernetes_pod_name]
            target_label: pod
          - source_labels: [__meta_kubernetes_namespace]
            target_label: namespace
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: prometheus
  namespace: {namespace}
spec:
  replicas: 1
  selector:
    matchLabels:
      app: prometheus
  template:
    metadata:
      labels:
        app: prometheus
    spec:
      containers:
      - name: prometheus
        image: prom/prometheus:latest
        ports:
        - containerPort: 9090
        volumeMounts:
        - name: config
          mountPath: /etc/prometheus
        - name: storage
          mountPath: /prometheus
      volumes:
      - name: config
        configMap:
          name: prometheus-config
      - name: storage
        emptyDir: {{}}
---
apiVersion: v1
kind: Service
metadata:
  name: prometheus
  namespace: {namespace}
spec:
  selector:
    app: prometheus
  ports:
  - port: 9090
    targetPort: 9090
  type: ClusterIP
"""
        return prometheus_config
    
    def generate_grafana_config(self, config: Dict[str, Any]) -> str:
        """Generate Grafana deployment configuration"""
        namespace = config.get("namespace", "default")
        
        grafana_config = f"""apiVersion: apps/v1
kind: Deployment
metadata:
  name: grafana
  namespace: {namespace}
spec:
  replicas: 1
  selector:
    matchLabels:
      app: grafana
  template:
    metadata:
      labels:
        app: grafana
    spec:
      containers:
      - name: grafana
        image: grafana/grafana:latest
        ports:
        - containerPort: 3000
        env:
        - name: GF_SECURITY_ADMIN_PASSWORD
          value: "admin"
        - name: GF_INSTALL_PLUGINS
          value: "grafana-piechart-panel"
        volumeMounts:
        - name: grafana-storage
          mountPath: /var/lib/grafana
      volumes:
      - name: grafana-storage
        emptyDir: {{}}
---
apiVersion: v1
kind: Service
metadata:
  name: grafana
  namespace: {namespace}
spec:
  selector:
    app: grafana
  ports:
  - port: 3000
    targetPort: 3000
  type: LoadBalancer
"""
        return grafana_config
    
    def generate_grafana_dashboard(self, config: Dict[str, Any]) -> str:
        """Generate Grafana dashboard JSON"""
        app_name = config.get("app_name", "agent-app")
        
        # Simple dashboard JSON without complex f-strings
        dashboard = {
            "dashboard": {
                "title": f"{app_name} Metrics",
                "panels": [],
                "refresh": "10s",
                "time": {"from": "now-1h", "to": "now"}
            }
        }
        return json.dumps(dashboard, indent=2)
    
    def generate_fluentd_config(self, config: Dict[str, Any]) -> str:
        """Generate Fluentd logging configuration"""
        namespace = config.get("namespace", "default")
        
        fluentd_config = f"""apiVersion: v1
kind: ConfigMap
metadata:
  name: fluentd-config
  namespace: {namespace}
data:
  fluent.conf: |
    <source>
      @type tail
      path /var/log/containers/*.log
      pos_file /var/log/fluentd-containers.log.pos
      tag kubernetes.*
      read_from_head true
      <parse>
        @type json
        time_format %Y-%m-%dT%H:%M:%S.%NZ
      </parse>
    </source>
    
    <filter kubernetes.**>
      @type kubernetes_metadata
    </filter>
    
    <match **>
      @type stdout
    </match>
---
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: fluentd
  namespace: {namespace}
spec:
  selector:
    matchLabels:
      app: fluentd
  template:
    metadata:
      labels:
        app: fluentd
    spec:
      containers:
      - name: fluentd
        image: fluent/fluentd-kubernetes-daemonset:v1-debian-elasticsearch
        volumeMounts:
        - name: varlog
          mountPath: /var/log
        - name: config
          mountPath: /fluentd/etc
      volumes:
      - name: varlog
        hostPath:
          path: /var/log
      - name: config
        configMap:
          name: fluentd-config
"""
        return fluentd_config


monitoring_service = MonitoringService()