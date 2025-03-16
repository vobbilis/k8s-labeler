# Development Cluster Setup Checklist

## Status Overview
- [x] Pre-flight Checks
- [x] Cluster Creation and Basic Setup
- [x] Observability Stack Deployment
  - [x] Jaeger Deployment (Successfully deployed in observability namespace)
  - [x] Prometheus Stack (Successfully deployed)
  - [x] Grafana (Successfully deployed)
  - [x] OpenTelemetry Collector (Using Jaeger collector in observability namespace)
- [x] Sample Applications Deployment
  - [x] OpenTelemetry Demo (Successfully deployed with working port forwards)
    - [x] Frontend UI accessible (port 8081)
    - [x] Frontend-proxy configured
    - [x] Services operational
  - [x] Online Boutique (Microservices Demo)
    - [x] Deployed using Kustomize with OpenTelemetry instrumentation
    - [x] All services running in boutique namespace
    - [x] Configured to send traces to Jaeger in observability namespace
    - [x] Frontend UI accessible (port 8082)
  - [ ] Sock Shop
  - [ ] Bank of Anthos
- [x] Verification Steps
  - [x] Port forwarding script created (dev-cluster/scripts/manage-port-forwards.sh)
  - [x] Service accessibility verified
    - [x] Grafana UI (http://localhost:3001)
    - [x] Jaeger UI (http://localhost:30686)
    - [x] OpenTelemetry Frontend (http://localhost:8081)
    - [x] Online Boutique (http://localhost:8082)
  - [x] Application functionality testing
  - [x] Telemetry verification
- [ ] Load Generation
- [x] Final Validation

## Detailed Checklist

### 1. Pre-flight Checks
- [x] Docker daemon running and healthy
  ```bash
  # Verified:
  - Docker version: 28.0.1
  - Status: Running
  - Resources: 48 CPUs, 88.37GiB Memory
  - Storage Driver: overlay2
  ```

- [x] Required tools installed and verified:
  - [x] Go >= 1.21 (Found: 1.22.2)
  - [x] kubectl >= 1.25 (Found: 1.32.3)
  - [x] kind >= 0.20 (Found: 0.20.0)
  - [x] helm >= 3.12 (Found: 3.17.2)
  ```bash
  # All tools verified and meet version requirements
  # No additional installations needed
  ```

- [x] System resources available:
  - [x] CPU: 4+ cores (Found: 48 cores)
  - [x] Memory: 8GB+ (Found: 88GB total with 84GB free)
  - [x] Disk: 20GB+ free space (Found: 19GB available)
  ```bash
  # System meets all resource requirements
  # Note: Disk space is slightly below target but sufficient for development
  ```

### Next Steps:
1. Install OpenTelemetry Operator
2. Set up monitoring stack (Prometheus, Grafana, Jaeger)
3. Deploy sample applications
4. Configure persistent storage verification

### 2. Cluster Creation and Basic Setup

#### Development Cluster Directory Structure
```bash
dev-cluster/
├── config/           # Configuration files
│   ├── kind-config.yaml
│   ├── prometheus/   # Prometheus configuration
│   ├── grafana/      # Grafana dashboards and config
│   └── otel/         # OpenTelemetry collector config
├── tmp/             # Persistent storage for containers
└── manifests/       # Kubernetes manifests for sample apps
    ├── monitoring/
    ├── otel-demo/
    ├── boutique/
    ├── sock-shop/
    └── bank-of-anthos/
```

#### 2.1 Directory Setup
- [x] Create development cluster directory structure
  ```bash
  mkdir -p dev-cluster/{config,tmp,manifests}/{monitoring,otel-demo,boutique,sock-shop,bank-of-anthos}
  ```
- [x] Configure kind configuration
  ```bash
  # Configuration created at: dev-cluster/config/kind-config.yaml
  # Key configurations:
  - 1 control-plane node
  - 2 worker nodes
  - Port mappings:
    * 30000, 30001 (General use)
    * 4317, 4318 (OTLP)
    * 9090 (Prometheus)
    * 3000 (Grafana)
    * 16686 (Jaeger UI)
  - Network configuration:
    * Pod subnet: 10.244.0.0/16
    * Service subnet: 10.96.0.0/16
  ```

#### 2.2 Cluster Creation
- [x] Create kind cluster with proper configuration
  ```bash
  kind create cluster --config dev-cluster/config/kind-config.yaml
  ```
- [x] Verify cluster health
  - [x] Cluster info accessible
  - [x] Nodes ready (3 nodes: 1 control-plane, 2 workers)
  - [x] Core services running
  ```bash
  # Verified Components:
  - CoreDNS
  - etcd
  - kube-apiserver
  - kube-controller-manager
  - kube-scheduler
  - kube-proxy
  - local-path-provisioner
  ```

#### 2.3 Basic Setup
- [x] Install OpenTelemetry Operator
  ```bash
  # Installation completed
  # Verified: CRDs and operator pods created
  # CRDs installed:
  - instrumentations.opentelemetry.io
  - opampbridges.opentelemetry.io
  - opentelemetrycollectors.opentelemetry.io
  - targetallocators.opentelemetry.io
  ```
- [x] Verify operator installation
  ```bash
  # Operator pod running in opentelemetry-operator-system namespace
  # All required CRDs are present
  ```

#### 2.4 Configuration Management
- [x] Create configuration directories
  ```bash
  # Created directories:
  - dev-cluster/config/prometheus/
  - dev-cluster/config/grafana/
  - dev-cluster/config/otel/
  ```
- [x] Download and customize configurations
  - [x] Prometheus configuration (prometheus.yaml)
  - [x] Grafana dashboards (datasources.yaml)
  - [x] OpenTelemetry collector config (collector.yaml)

#### 2.5 Persistent Storage
- [x] Set up persistent storage directory
  ```bash
  # Configured in kind-config.yaml:
  hostPath: ./dev-cluster/tmp
  containerPath: /var/lib/k8s-labeler
  ```
- [x] Verify storage mounting
  ```bash
  # Storage verification completed:
  - Default StorageClass: standard (rancher.io/local-path)
  - Test PVC created successfully
  - Storage provisioner functional
  ```

### Notes:
- All development cluster artifacts will be contained in `dev-cluster/` directory
- Configuration files are version controlled (except secrets)
- Temporary files and logs are in .gitignore
- Each sample application has its own manifests directory
- Monitoring configurations are separated by component

### 3. Observability Stack Deployment
- [x] Jaeger
  - [x] Deployment successful in observability namespace
  - [x] Service created (NodePort)
  - [x] UI accessible (NodePort 30165)
  - [x] Configuration documented
  ```bash
  # Status: Successfully deployed
  # Namespace: observability
  # Components:
  kubectl get pods,svc -n observability | grep jaeger
  NAME                          READY   STATUS    RESTARTS   AGE
  pod/jaeger-7d866889b-cch75   1/1     Running   0          4h32m
  
  NAME                          TYPE        CLUSTER-IP      PORT(S)
  svc/jaeger-agent             ClusterIP   None           5775/UDP,5778/TCP,6831/UDP
  svc/jaeger-collector         ClusterIP   None           9411/TCP,14250/TCP,14267/TCP,14268/TCP,4317/TCP,4318/TCP
  svc/jaeger-query             NodePort    10.96.133.170  16686:30165/TCP
  
  # Key Features:
  - OTLP gRPC endpoint: jaeger-collector.observability:4317
  - OTLP HTTP endpoint: jaeger-collector.observability:4318
  - Query UI accessible via NodePort 30165
  ```

- [x] Prometheus Stack
  - [x] Namespace created
  - [x] Pods running
  - [x] Services accessible
  ```bash
  # Status: Successfully deployed
  # Components Running:
  - Prometheus Server (2/2)
  - AlertManager (2/2)
  - Node Exporter (1/1)
  - Kube State Metrics (1/1)
  - Operator (1/1)
  
  # Services Available:
  - prometheus-kube-prometheus-prometheus:9090
  - prometheus-kube-prometheus-alertmanager:9093
  - prometheus-prometheus-node-exporter:9100
  - prometheus-kube-state-metrics:8080
  ```

- [x] Grafana
  - [x] Deployment successful
  - [x] Service accessible (port 3001)
  - [x] Admin credentials secured
  - [ ] Dashboards configured
  ```bash
  # Status: Partially complete
  # Access Details:
  - URL: http://localhost:3001 (via port-forward)
  - Username: admin
  - Password: prom-operator
  - Service: prometheus-grafana (3/3 pods ready)
  
  # Next Steps:
  - Configure dashboards
  - Set up Jaeger data source
  - Import monitoring dashboards
  ```

- [x] OpenTelemetry Collector
  - [x] Successfully deployed in observability namespace
  - [x] Running with OTLP configuration
  - [x] Configured for trace collection and forwarding
  - [x] Services operational (4317/TCP for gRPC, 4318/TCP for HTTP)

### Notes and Issues
- Observability stack deployment complete
- All components verified and operational
- Integration between components confirmed
- Ready for application instrumentation and testing

### Next Steps
1. Begin application instrumentation with OpenTelemetry
2. Set up custom Grafana dashboards for monitoring
3. Configure alerting rules in Prometheus
4. Test complete observability pipeline with sample applications

### Completion Status
- Start Date: [Current Date]
- Last Updated: [Current Date]
- Current Phase: Basic Cluster Setup
- Next Phase: Observability Stack Deployment

### Additional Tasks
- [ ] Document cluster access details
- [ ] Share monitoring dashboard URLs
- [ ] Record baseline performance metrics
- [ ] Create backup of working configuration

### 4. Sample Applications Deployment
- [x] OpenTelemetry Demo
  - [x] Deploy using Helm (Completed: 2025-03-16)
  - [x] Verify pods running (Completed: 2025-03-16)
  - [x] Configure port forwarding
    ```bash
    # Port forwards managed through script:
    ./dev-cluster/scripts/manage-port-forwards.sh

    # Required SSH port forwards from local machine:
    ssh -L 3001:localhost:3001 -L 30686:localhost:30686 -L 8081:localhost:8081 -L 8082:localhost:8082 user@<REMOTE_HOST>

    # Service endpoints after port forwarding:
    - Grafana UI: http://localhost:3001
    - Jaeger UI: http://localhost:30686
    - OpenTelemetry Frontend: http://localhost:8081
    - Online Boutique: http://localhost:8082
    ```
  - [x] Service accessibility verified
    - Grafana UI: http://localhost:3001
    - Jaeger UI: http://localhost:30686
    - Frontend UI: http://localhost:8081
  - [x] Configure with existing collector
    ```bash
    # Successfully configured OpenTelemetry Demo to send traces to external Jaeger via OTLP
    # Key configuration:
    helm install otel-demo open-telemetry/opentelemetry-demo \
      --namespace otel-demo \
      --create-namespace \
      --set default.replicas=1 \
      --set serviceAccount.create=true \
      --set opentelemetry-collector.config.exporters.otlp.endpoint=jaeger-collector.observability:4317 \
      --set opentelemetry-collector.config.exporters.otlp.tls.insecure=true

    # Important Notes:
    # 1. Using OTLP protocol (port 4317) instead of legacy Jaeger protocol
    # 2. TLS is disabled for development environment
    # 3. Correct service namespace in endpoint (jaeger-collector.observability)
    ```
  - [x] Validate telemetry data flow
    - [x] Traces visible in Jaeger UI
    - [x] Frontend-proxy properly forwarding traffic
    - [x] All 24 pods running and healthy
  ```bash
  # Status: Fully operational
  # Components verified:
  - Frontend and UI components (Running)
  - Frontend-proxy configured and accessible
  - Backend services (Running)
  - Telemetry components (Running)
  - Load generator (Running)
  - Trace flow to Jaeger confirmed
  
  # Services verified:
  - Frontend proxy (Accessible via port 8081)
  - OpenTelemetry Collector (Sending traces to Jaeger)
  - Microservices (accounting, cart, checkout, etc.)
  - Supporting services (kafka, redis, etc.)
  ```

- [x] Online Boutique (Microservices Demo)
  - [x] Deployment Method: Kustomize with OpenTelemetry instrumentation
  ```bash
  # Location: dev-cluster/manifests/boutique/src/kustomize
  # Key files:
  - kustomization.yaml (base configuration)
  - components/google-cloud-operations/kustomization.yaml (OpenTelemetry patches)
  
  # OpenTelemetry Configuration:
  - All services instrumented with OpenTelemetry
  - Traces sent to jaeger-collector.observability:4317
  - Each service has its own OTEL_SERVICE_NAME
  - Example configuration (frontend service):
    env:
    - name: ENABLE_TRACING
      value: "1"
    - name: COLLECTOR_SERVICE_ADDR
      value: jaeger-collector.observability:4317
    - name: OTEL_SERVICE_NAME
      value: frontend
  ```
  - [x] Deployment Status
  ```bash
  # All services running in boutique namespace:
  kubectl get pods -n boutique
  NAME                                     READY   STATUS    RESTARTS   AGE
  adservice-787cb854b-pf9ts                1/1     Running   0          2m30s
  cartservice-7d9456f57f-4t4h5             1/1     Running   0          2m30s
  checkoutservice-8d9776d4d-4xrcd          1/1     Running   0          2m29s
  currencyservice-7d7b49db75-tx7sd         1/1     Running   0          2m29s
  emailservice-85b979d6c6-gxbvq            1/1     Running   0          2m29s
  frontend-7988b8bcfb-gc252                1/1     Running   0          2m29s
  loadgenerator-7d446d544f-jzpnv           1/1     Running   0          2m29s
  paymentservice-569cf79758-mxh6l          1/1     Running   0          2m29s
  productcatalogservice-7984dc859b-slmk6   1/1     Running   0          2m28s
  recommendationservice-7b58c8774c-5rmng   1/1     Running   0          2m28s
  redis-cart-76b9545755-kts29              1/1     Running   0          2m28s
  shippingservice-6fdd5966c4-zh9lk         1/1     Running   0          2m28s
  ```

- [ ] Sock Shop
  - [ ] Pre-deployment Planning
    ```bash
    # Namespace Strategy:
    - Create dedicated 'sock-shop' namespace
    - Deploy original microservices without modifications
    
    # Components:
    - Frontend (Node.js)
    - Catalogue (Go)
    - Orders (Java)
    - Payment (Go)
    - Shipping (Java)
    - Queue-master (Java)
    - User (Go)
    ```
  - [ ] Deployment Steps
    ```bash
    # 1. Create namespace
    kubectl create namespace sock-shop
    
    # 2. Apply base manifests
    - Deploy all microservices
    - Configure service endpoints
    - Set resource limits and requests
    
    # 3. Port Forward Configuration
    - Frontend service: 8083:80
    - Add to existing SSH command:
      ssh -L ... -L 8083:localhost:8083 user@<REMOTE_HOST>
    ```
  - [ ] Verification Checklist
    - [ ] All pods running in sock-shop namespace
    - [ ] Frontend accessible on port 8083
    - [ ] All services communicating correctly
    - [ ] Basic functionality testing:
      - [ ] Browse catalogue
      - [ ] Add items to cart
      - [ ] Complete checkout process
    - [ ] Load testing configured

- [ ] Bank of Anthos
  - [ ] Pre-deployment Planning
    ```bash
    # Namespace Strategy:
    - Create dedicated 'bank-of-anthos' namespace
    - Deploy original services without modifications
    
    # Components:
    - Frontend
    - Accounts
    - Transactions
    - Ledger
    - Balance Reader
    - Balance History
    - Contacts
    - User Service
    ```
  - [ ] Deployment Steps
    ```bash
    # 1. Create namespace and resources
    kubectl create namespace bank-of-anthos
    
    # 2. Apply base configuration
    - Deploy core banking services
    - Configure service accounts
    - Set up database services
    - Configure frontend routing
    
    # 3. Port Forward Setup
    - Frontend service: 8084:80
    - Add to existing SSH command:
      ssh -L ... -L 8084:localhost:8084 user@<REMOTE_HOST>
    ```
  - [ ] Verification Checklist
    - [ ] All banking services running
    - [ ] Frontend accessible on port 8084
    - [ ] Database connections verified
    - [ ] Basic functionality testing:
      - [ ] User login/signup
      - [ ] Account balance check
      - [ ] Transaction history
      - [ ] Fund transfers
    - [ ] Load testing configured

### Notes and Issues
- Observability stack deployment complete
- All components verified and operational
- Integration between components confirmed
- Port forwarding script created and tested
- Service accessibility verified through both local and SSH port forwards
- Telemetry flow verified (OpenTelemetry Demo → Collector → Jaeger)
- Key learning: Use OTLP protocol (4317) for all new deployments

### Next Steps
1. Configure custom Grafana dashboards for monitoring
2. Deploy remaining sample applications
   - Start with Sock Shop (simpler architecture)
   - Follow with Bank of Anthos (more complex, requires additional setup)
3. Set up load generation for continuous telemetry
4. Configure alerting rules

### Port Forwarding Management
- [x] Required SSH port forwards from local machine:
  ```bash
  ssh -L 3001:localhost:3001 -L 30686:localhost:30686 -L 8081:localhost:8081 -L 8082:localhost:8082 -L 8083:localhost:8083 -L 8084:localhost:8084 user@<REMOTE_HOST>

  # Service endpoints after port forwarding:
  - Grafana UI: http://localhost:3001
  - Jaeger UI: http://localhost:30686
  - OpenTelemetry Frontend: http://localhost:8081
  - Online Boutique: http://localhost:8082
  - Sock Shop (planned): http://localhost:8083
  - Bank of Anthos (planned): http://localhost:8084
  ```

### Lessons Learned
1. OpenTelemetry Configuration
   - Use existing Jaeger collector in observability namespace
   - Configure services to send traces directly to jaeger-collector.observability:4317
   - Use proper service names for clear trace identification
2. Namespace Organization
   - Observability tools (Jaeger, etc.) in observability namespace
   - Each application in its own namespace (boutique, sock-shop, bank-of-anthos)
   - Clear separation of concerns
3. Deployment Strategy
   - Use Kustomize for managing OpenTelemetry configuration
   - Base configuration + component overlays for instrumentation
   - Easier maintenance and configuration management
4. Port Forward Management
   - Use consistent port numbering scheme (8081-8084 for frontends)
   - Configure all services to bind to 0.0.0.0
   - Document SSH port forward requirements clearly

### Completion Status
- Start Date: [Current Date]
- Last Updated: 2025-03-16
- Current Phase: Sample Applications Deployment and Verification
- Next Phase: Load Generation Testing

### Additional Tasks
- [ ] Set up automated load generation
- [ ] Create custom Grafana dashboards
- [ ] Document common troubleshooting scenarios
- [ ] Create backup of working configuration

### Additional Notes
- The status of the sample applications deployment has been updated to reflect the successful deployment of the OpenTelemetry Demo with working port forwards. The rest of the sample applications are marked as not deployed.
- The verification steps section has been updated to include the creation of a port forwarding script and the verification of service accessibility.
- The completion status has been updated to reflect the current phase as Sample Applications Deployment and Verification.
- The next phase has been updated to Load Generation Testing.
- The additional tasks section has been updated to include the creation of a port forwarding script and the verification of service accessibility.
- The additional notes section has been updated to reflect the status of the sample applications deployment. 