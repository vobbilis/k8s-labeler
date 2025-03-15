package types

// ServiceMeshLabel represents the service mesh observability format
type ServiceMeshLabel struct {
	BaseLabel
	MeshContext MeshContext  `json:"mesh_context"`
	Telemetry   Telemetry    `json:"telemetry"`
	Analysis    MeshAnalysis `json:"analysis"`
}

// MeshContext represents the context of a service mesh observation
type MeshContext struct {
	SourceService      string `json:"source_service"`
	DestinationService string `json:"destination_service"`
	MeshPlatform       string `json:"mesh_platform"`
	ObservedPeriod     string `json:"observed_period"`
}

// Telemetry represents telemetry data from the service mesh
type Telemetry struct {
	Metrics MeshMetrics `json:"metrics"`
	Traces  []Trace     `json:"traces"`
}

// MeshMetrics represents service mesh metrics
type MeshMetrics struct {
	ErrorRate         string `json:"error_rate"`
	LatencyP95        string `json:"latency_p95"`
	RequestsPerSecond string `json:"requests_per_second"`
}

// Trace represents a distributed trace
type Trace struct {
	TraceID string `json:"trace_id"`
	Spans   []Span `json:"spans"`
}

// Span represents a span in a distributed trace
type Span struct {
	Service   string `json:"service"`
	Operation string `json:"operation"`
	Duration  string `json:"duration"`
	Status    string `json:"status"`
	Error     string `json:"error,omitempty"`
}

// MeshAnalysis represents the analysis of service mesh issues
type MeshAnalysis struct {
	RootCause string `json:"root_cause"`
	Evidence  string `json:"evidence"`
	Solution  string `json:"solution"`
}

// Validate implements the Label interface
func (s *ServiceMeshLabel) Validate() error {
	// TODO: Implement validation logic
	return nil
}
