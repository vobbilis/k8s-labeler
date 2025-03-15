package types

// DeploymentLabel represents the deployment troubleshooting format
type DeploymentLabel struct {
	BaseLabel
	DeploymentContext DeploymentContext  `json:"deployment_context"`
	Analysis          DeploymentAnalysis `json:"analysis"`
	Resolution        Resolution         `json:"resolution"`
}

// DeploymentContext represents the context of a deployment
type DeploymentContext struct {
	Service         string `json:"service"`
	OldVersion      string `json:"old_version"`
	NewVersion      string `json:"new_version"`
	RolloutStrategy string `json:"rollout_strategy"`
}

// DeploymentAnalysis represents the analysis of a deployment issue
type DeploymentAnalysis struct {
	Status        DeploymentStatus `json:"status"`
	Events        []Event          `json:"events"`
	PodConditions []PodCondition   `json:"pod_conditions"`
	Logs          []string         `json:"logs"`
}

// DeploymentStatus represents the status of a deployment
type DeploymentStatus struct {
	DesiredReplicas     int `json:"desired_replicas"`
	UpdatedReplicas     int `json:"updated_replicas"`
	AvailableReplicas   int `json:"available_replicas"`
	UnavailableReplicas int `json:"unavailable_replicas"`
}

// PodCondition represents the condition of a pod
type PodCondition struct {
	Type    string `json:"type"`
	Status  string `json:"status"`
	Reason  string `json:"reason"`
	Message string `json:"message"`
}

// Validate implements the Label interface
func (d *DeploymentLabel) Validate() error {
	// TODO: Implement validation logic
	return nil
}
