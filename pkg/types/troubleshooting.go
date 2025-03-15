package types

// TroubleshootingLabel represents the comprehensive troubleshooting format
type TroubleshootingLabel struct {
	BaseLabel
	Analysis TroubleshootingAnalysis `json:"analysis"`
	Metadata Context                 `json:"metadata"`
}

// TroubleshootingAnalysis represents the analysis part of a troubleshooting label
type TroubleshootingAnalysis struct {
	Symptoms   []string                `json:"symptoms"`
	RootCause  string                  `json:"root_cause"`
	Evidence   TroubleshootingEvidence `json:"evidence"`
	Resolution Resolution              `json:"resolution"`
}

// TroubleshootingEvidence represents the evidence collected during troubleshooting
type TroubleshootingEvidence struct {
	Metrics map[string]string `json:"metrics"`
	Logs    []string          `json:"logs"`
	Events  []string          `json:"events"`
}

// Validate implements the Label interface
func (t *TroubleshootingLabel) Validate() error {
	// TODO: Implement validation logic
	return nil
}
