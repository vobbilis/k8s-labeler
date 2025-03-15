package types

// NetworkLabel represents the network policy analysis format
type NetworkLabel struct {
	BaseLabel
	NetworkContext NetworkContext  `json:"network_context"`
	Analysis       NetworkAnalysis `json:"analysis"`
}

// NetworkContext represents the context of a network issue
type NetworkContext struct {
	Source      ServiceEndpoint `json:"source"`
	Destination ServiceEndpoint `json:"destination"`
}

// ServiceEndpoint represents a service endpoint in the network
type ServiceEndpoint struct {
	Service   string            `json:"service"`
	Namespace string            `json:"namespace"`
	Labels    map[string]string `json:"labels"`
}

// NetworkAnalysis represents the analysis of a network issue
type NetworkAnalysis struct {
	ConnectivityTest ConnectivityTest `json:"connectivity_test"`
	NetworkPolicies  []NetworkPolicy  `json:"network_policies"`
	Diagnosis        string           `json:"diagnosis"`
	Solution         string           `json:"solution"`
}

// ConnectivityTest represents a network connectivity test
type ConnectivityTest struct {
	Protocol string `json:"protocol"`
	Port     int    `json:"port"`
	Result   string `json:"result"`
}

// NetworkPolicy represents a Kubernetes network policy
type NetworkPolicy struct {
	Name      string            `json:"name"`
	Namespace string            `json:"namespace"`
	Spec      NetworkPolicySpec `json:"spec"`
}

// NetworkPolicySpec represents the specification of a network policy
type NetworkPolicySpec struct {
	Ingress []NetworkPolicyRule `json:"ingress"`
}

// NetworkPolicyRule represents a rule in a network policy
type NetworkPolicyRule struct {
	From []NetworkPolicyPeer `json:"from"`
}

// NetworkPolicyPeer represents a peer in a network policy rule
type NetworkPolicyPeer struct {
	NamespaceSelector LabelSelector `json:"namespaceSelector,omitempty"`
	PodSelector       LabelSelector `json:"podSelector,omitempty"`
}

// LabelSelector represents a Kubernetes label selector
type LabelSelector struct {
	MatchLabels map[string]string `json:"matchLabels"`
}

// Validate implements the Label interface
func (n *NetworkLabel) Validate() error {
	// TODO: Implement validation logic
	return nil
}
