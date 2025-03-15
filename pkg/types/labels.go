package types

import "time"

// Label is the base interface that all label types must implement
type Label interface {
	GetID() string
	GetQuestion() string
	GetTimestamp() time.Time
	Validate() error
}

// BaseLabel contains common fields for all label types
type BaseLabel struct {
	ID        string    `json:"id"`
	Question  string    `json:"question"`
	Timestamp time.Time `json:"timestamp"`
}

// GetID returns the label ID
func (b *BaseLabel) GetID() string {
	return b.ID
}

// GetQuestion returns the label question
func (b *BaseLabel) GetQuestion() string {
	return b.Question
}

// GetTimestamp returns the label timestamp
func (b *BaseLabel) GetTimestamp() time.Time {
	return b.Timestamp
}

// Context represents common contextual information
type Context struct {
	PodName    string                 `json:"pod_name,omitempty"`
	Namespace  string                 `json:"namespace,omitempty"`
	Events     []string               `json:"events,omitempty"`
	Cluster    string                 `json:"cluster,omitempty"`
	Service    string                 `json:"service,omitempty"`
	Version    string                 `json:"version,omitempty"`
	Additional map[string]interface{} `json:"additional,omitempty"`
}

// ResourceMetrics represents common resource metrics
type ResourceMetrics struct {
	CPU    ResourceMetric `json:"cpu"`
	Memory ResourceMetric `json:"memory"`
}

// ResourceMetric represents a single resource metric
type ResourceMetric struct {
	Usage       string `json:"usage"`
	Limit       string `json:"limit"`
	Request     string `json:"request"`
	Throttling  string `json:"throttling,omitempty"`
	Utilization string `json:"utilization,omitempty"`
}

// Resolution represents a resolution to an incident
type Resolution struct {
	RootCause    string   `json:"root_cause"`
	Steps        []string `json:"steps,omitempty"`
	Fix          string   `json:"fix,omitempty"`
	Verification string   `json:"verification"`
}

// MetricData represents common metric data
type MetricData struct {
	Value     string    `json:"value"`
	Timestamp time.Time `json:"timestamp"`
	Unit      string    `json:"unit,omitempty"`
}

// Event represents a Kubernetes event
type Event struct {
	Type      string    `json:"type"`
	Reason    string    `json:"reason"`
	Message   string    `json:"message"`
	Timestamp time.Time `json:"timestamp"`
}
